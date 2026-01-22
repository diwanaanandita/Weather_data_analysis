import xarray as xr
import dask
import os

class WeatherService:
    def __init__(self, repository, OUTDIR):
        self.repo = repository
        self.yearly_avg = None
        self.baseline = None
        self.anomaly = None

        self.baseline_start = None
        self.baseline_end = None
        self.outdir = OUTDIR
        self.anomaly_file_name = 'temperature_anomaly.nc'
        self.baseline_file_name = 'baseline.nc'
        self.yearly_avg_file_name = 'yearly_average.nc'
    
    def _ensure_data_loaded(self, data):
        if data is None:
            raise RuntimeError("Data not loaded. Call fetch_data() first.")


    def compute_mean(self, path):
        data = self.repo.load_data(path)
        self._ensure_data_loaded(data)
        result = data['air'].mean()
        (result,) = dask.compute(result)
        return float(result)

    def compute_max(self, path):
        data = self.repo.load_data(path)
        self._ensure_data_loaded(data)
        result = data['air'].max()
        (result,) = dask.compute(result)
        return float(result)

    def compute_min(self, path):
        data = self.repo.load_data(path)
        self._ensure_data_loaded(data)
        result = data['air'].min()
        (result,) = dask.compute(result)
        return float(result)

    def compute_yearly_average(self, path):
        data = self.repo.load_data(path)
        self._ensure_data_loaded(data)
        if self.yearly_avg is not None:
            return self.yearly_avg
        if "air" not in getattr(data, "data_vars", {}):
            raise RuntimeError("air not found; call convert_kelvin_to_celsius() first")
        yearly_avg = data["air"].groupby("time.year").mean(dim="time")
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
        baseline = baseline.expand_dims(
            year=self.yearly_avg.year
        )
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
            raise ValueError("Baseline start and end years outside range 1948-1957 \n")
        if start > end:
            raise ValueError("Baseline start year must be <= end year \n")
        
    def _validate_coordinates(self, lat, lon):
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")


    def _compute_and_save(self, path, baseline_start, baseline_end, include_anomaly):
        self._validate_years(baseline_start, baseline_end)
        self.baseline_start = baseline_start
        self.baseline_end = baseline_end

        self._clear_outdir()

        self.yearly_avg = self.compute_yearly_average(path)
        self.baseline = self.compute_baseline()

        outputs = {
            self.yearly_avg_file_name: self.yearly_avg,
            self.baseline_file_name: self.baseline,
        }

        if include_anomaly:
            self.anomaly = self.compute_temperature_anomaly()
            outputs[self.anomaly_file_name] = self.anomaly

        for fname, data in outputs.items():
            data.to_netcdf(os.path.join(self.outdir, fname))
        
        for fname in outputs:
            path = os.path.join(self.outdir, fname)
            ds = xr.open_dataset(path, chunks="auto", engine='netcdf4')  
            print("\n\ndata saved as : \n\n", ds)


    def compute_and_save_baseline(self, path,baseline_start, baseline_end):
        self._compute_and_save(path,baseline_start, baseline_end, include_anomaly=False)

    def compute_and_save_anomaly(self, path, baseline_start, baseline_end):
        self._compute_and_save(path,baseline_start, baseline_end, include_anomaly=True)

    def get_location_data(self, lat, lon, file_name, dimension):
        self._validate_coordinates(lat, lon)
        file_path = os.path.join(self.outdir, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}. Run compute_and_save() first.")

        data_ds = xr.open_dataset(file_path, chunks="auto", engine='netcdf4')

        location = data_ds[dimension].sel(
            lat=lat, 
            lon=lon, 
            method='nearest'
        )
        
        return location
        
    def get_location_anomaly(self, lat, lon):
        dimension = 'temperature_anomaly'
        return self.get_location_data(lat, lon, self.anomaly_file_name, dimension)
    
    def get_location_baseline(self, lat, lon):
        dimension = 'baseline_temperature'
        return self.get_location_data(lat, lon, self.baseline_file_name, dimension)
