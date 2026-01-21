import os
import dask


class WeatherService:
    """Service for weather data computation and analysis."""
    
    def __init__(self, xr_data):
        self.xr_data = xr_data
        self.yearly_avg = None
        self.baseline = None
        self.anomaly = None
        self.baseline_start = None
        self.baseline_end = None
        self.outdir = "output/"
        os.makedirs(self.outdir, exist_ok=True)

    def compute_mean(self):
        return self.xr_data['air'].mean()

    def compute_max(self):
        return self.xr_data['air'].max()

    def compute_min(self):
        return self.xr_data['air'].min()

    def compute_stats(self):
        """Compute mean, max, min statistics."""
        computations = {
            "mean": self.compute_mean(),
            "max": self.compute_max(),
            "min": self.compute_min(),
        }
        
        # Compute all at once using dask.compute
        results = dask.compute(*computations.values())
        
        # Build dict with computed values
        return {key: float(val) for key, val in zip(computations.keys(), results)}

    def convert_kelvin_to_celsius(self):
        """Convert temperature from Kelvin to Celsius (idempotent)."""
        if "air_c" in getattr(self.xr_data, "data_vars", {}):
            return self.xr_data["air_c"]
        
        self.xr_data["air_c"] = self.xr_data["air"] - 273.15
        self.xr_data["air_c"].attrs["units"] = "Celsius"
        return self.xr_data["air_c"]

    def compute_yearly_average(self):
        """Compute yearly average temperature and cache it (idempotent)."""
        if self.yearly_avg is not None:
            return self.yearly_avg
        if "air_c" not in getattr(self.xr_data, "data_vars", {}):
            raise RuntimeError("air_c not found; call convert_kelvin_to_celsius() first")
        yearly_avg = self.xr_data["air_c"].groupby("time.year").mean(dim="time")
        yearly_avg.name = "yearly_mean_temperature"
        self.yearly_avg = yearly_avg.persist()
        return self.yearly_avg

    def compute_baseline(self):
        """Compute baseline average temperature over specified years and cache it."""
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
        """Compute temperature anomaly relative to baseline and cache it."""
        if self.anomaly is not None:
            return self.anomaly
        if self.yearly_avg is None or self.baseline is None:
            raise RuntimeError("yearly_avg and baseline must be computed first")
        anomaly = self.yearly_avg - self.baseline
        anomaly.name = "temperature_anomaly"
        self.anomaly = anomaly.persist()
        return self.anomaly

    def compute_and_save_to_netcdf(self, baseline_start, baseline_end):
        """Compute yearly average, baseline, anomaly and save to netCDF files."""
        self.baseline_start = baseline_start
        self.baseline_end = baseline_end
        self.convert_kelvin_to_celsius()
        self.compute_yearly_average()
        self.compute_baseline()
        self.compute_temperature_anomaly()

     
        for fname in ["yearly_average.nc", "baseline.nc", "temperature_anomaly.nc"]:
            fpath = os.path.join(self.outdir, fname)
            if os.path.exists(fpath):
                os.remove(fpath)

        self.yearly_avg.to_netcdf(os.path.join(self.outdir, "yearly_average.nc"))
        self.baseline.to_netcdf(os.path.join(self.outdir, "baseline.nc"))
        self.anomaly.to_netcdf(os.path.join(self.outdir, "temperature_anomaly.nc"))