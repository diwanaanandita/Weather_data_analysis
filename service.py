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
        self.outdir = OUTDIR

    def fetch_data(self, path):
        self._data = self.repo.load_data(path)

    def _ensure_data_loaded(self):
        if self._data is None:
            raise RuntimeError("Data not loaded. Call fetch_data() first.")

    def compute_mean(self):
        self._ensure_data_loaded()
        result = self._data['air'].mean()
        (result,) = dask.compute(result)
        return float(result)

    def compute_max(self):
        self._ensure_data_loaded()
        result = self._data['air'].max()
        (result,) = dask.compute(result)
        return float(result)

    def compute_min(self):
        self._ensure_data_loaded()
        result = self._data['air'].min()
        (result,) = dask.compute(result)
        return float(result)

    def compute_yearly_average(self):
        if self.yearly_avg is not None:
            return self.yearly_avg
        if "air" not in getattr(self._data, "data_vars", {}):
            raise RuntimeError("air not found; call convert_kelvin_to_celsius() first")
        yearly_avg = self._data["air"].groupby("time.year").mean(dim="time")
        yearly_avg.name = "yearly_mean_temperature"
        self.yearly_avg = yearly_avg.persist()
        return self.yearly_avg

    def compute_baseline(self):
        if self.baseline is not None:
            return self.baseline
        if self.yearly_avg is None:
            raise RuntimeError("yearly_avg not computed; call compute_yearly_average() first")
        if self.baseline_start is None or self.baseline_end is None:
            raise RuntimeError("baseline_start and baseline_end must be set before computing baseline")
        baseline = self.yearly_avg.sel(year=slice(self.baseline_start, self.baseline_end)).mean(dim="year")
        baseline.name = "baseline_temperature"
        self.baseline = baseline.persist()
        return self.baseline

    def compute_temperature_anomaly(self):
        if self.anomaly is not None:
            return self.anomaly
        if self.yearly_avg is None or self.baseline is None:
            raise RuntimeError("yearly_avg and baseline must be computed first")
        anomaly = self.yearly_avg - self.baseline
        anomaly.name = "temperature_anomaly"
        self.anomaly = anomaly.persist()
        return self.anomaly

    def _clear_outdir(self):
        for fname in os.listdir(self.outdir):
            fpath = os.path.join(self.outdir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)

    def _validate_years(self, start, end):
        if start < int("1948") or end > int("1957"):
            raise ValueError("Baseline start and end years outside reange 1948-1957 \n")
        if start > end:
            raise ValueError("Baseline start year must be <= end year \n")


    def _compute_and_save(self, baseline_start, baseline_end, include_anomaly):
        self._validate_years(baseline_start, baseline_end)
        self.baseline_start = baseline_start
        self.baseline_end = baseline_end

        self._clear_outdir()

        self.yearly_avg = self.compute_yearly_average()
        self.baseline = self.compute_baseline()

        outputs = {
            "yearly_average.nc": self.yearly_avg,
            "baseline.nc": self.baseline,
        }

        if include_anomaly:
            self.anomaly = self.compute_temperature_anomaly()
            outputs["temperature_anomaly.nc"] = self.anomaly

        for fname, data in outputs.items():
            data.to_netcdf(os.path.join(self.outdir, fname))
        
        for fname in outputs:
            path = os.path.join(self.outdir, fname)
            ds = xr.open_dataset(path, chunks="auto", engine='netcdf4')  
            print("\n\ndata saved as : \n\n", ds)


    def compute_and_save_baseline(self, baseline_start, baseline_end):
        self._compute_and_save(baseline_start, baseline_end, include_anomaly=False)

    def compute_and_save_anomaly(self, baseline_start, baseline_end):
        self._compute_and_save(baseline_start, baseline_end, include_anomaly=True)
