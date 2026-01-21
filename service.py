import xarray as xr
import dask
import os

class WeatherService:
    def __init__(self, repository, OUTDIR):
        self.repo = repository
        self._data = None
        self.yearly_avg = None
        self.baseline = None
        self.anomaly = None

        self.baseline_start = None
        self.baseline_end = None
        self.operation = None
        self.outdir = OUTDIR

    def fetch_data(self, path):
        self._data = self.repo.load_data(path)

    def _ensure_data_loaded(self):
        if self._data is None:
            raise RuntimeError("Data not loaded. Call fetch_data() first.")

    def run_operation(self, operation, **kwargs):
        self.operation = operation
        if self.operation in {"mean", "max", "min"}:
            return self.compute_stats()

        if self.operation == "baseline" or self.operation == "anomaly":
            self.compute_and_save_to_netcdf(kwargs["baseline_start"], kwargs["baseline_end"])
            return None

        raise ValueError(f"Unsupported operation: {operation}")

    def compute_mean(self):
        self._ensure_data_loaded()
        return self._data['air'].mean()

    def compute_max(self):
        self._ensure_data_loaded()
        return self._data['air'].max()

    def compute_min(self):
        self._ensure_data_loaded()
        return self._data['air'].min()


    def compute_stats(self):
        self._ensure_data_loaded()
        operations = {"mean": self.compute_mean, "max": self.compute_max, "min": self.compute_min}

        if self.operation not in operations:
            raise ValueError(f"Unsupported operation: {self.operation}")

        result = operations[self.operation]()
        (result,) = dask.compute(result)
        return float(result)
    
    def compute_yearly_average(self):
        if self.yearly_avg is not None:
            return self.yearly_avg
        if "air" not in getattr(self._data, "data_vars", {}):
            raise RuntimeError("air not found; call convert_kelvin_to_celsius() first")
        yearly_avg = self._data["air"].groupby("time.year").mean(dim="time")
        yearly_avg.name = "yearly_mean_temperature"
        return yearly_avg
    
    def compute_baseline(self):
        if self.baseline is not None:
            return self.baseline
        if self.yearly_avg is None:
            raise RuntimeError("yearly_avg not computed; call compute_yearly_average() first")
        if self.baseline_start is None or self.baseline_end is None:
            raise RuntimeError("baseline_start and baseline_end must be set before computing baseline")
        baseline = self.yearly_avg.sel(year=slice(self.baseline_start, self.baseline_end)).mean(dim="year")
        baseline.name = "baseline_temperature"
        return baseline
    
    def compute_temperature_anomaly(self):
        if self.anomaly is not None:
            return self.anomaly
        if self.yearly_avg is None or self.baseline is None:
            raise RuntimeError("yearly_avg and baseline must be computed first")
        anomaly = self.yearly_avg - self.baseline
        anomaly.name = "temperature_anomaly"
        return anomaly
    
    def _clear_outdir(self):
        for fname in os.listdir(self.outdir):
            fpath = os.path.join(self.outdir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)

    def compute_and_save_to_netcdf(self, baseline_start, baseline_end):
        self.baseline_start = baseline_start
        self.baseline_end = baseline_end

        self._clear_outdir()

        self.yearly_avg = self.compute_yearly_average()
        self.baseline = self.compute_baseline()
        outputs = { "yearly_average.nc": self.yearly_avg, "baseline.nc": self.baseline}

        if self.operation == "anomaly":
            self.anomaly = self.compute_temperature_anomaly()
            outputs["temperature_anomaly.nc"] = self.anomaly

        for fname, data in outputs.items():
            data.to_netcdf(os.path.join(self.outdir, fname))

        for fname in outputs:
            path = os.path.join(self.outdir, fname)
            ds = xr.open_dataset(path, chunks="auto", engine='netcdf4')  
            print("data saved as : ", ds)