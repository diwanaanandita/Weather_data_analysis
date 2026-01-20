import xarray as xr
import dask

class WeatherService:
    def __init__(self, repository):
        self.repo = repository
        self._data = None

    def fetch_data(self, path):
        self._data = self.repo.load_data(path)

    def _ensure_data_loaded(self):
        if self._data is None:
            raise RuntimeError("Data not loaded. Call fetch_data() first.")

    def compute_mean(self):
        self._ensure_data_loaded()
        return self._data.mean()

    def compute_max(self):
        self._ensure_data_loaded()
        return self._data.max()

    def compute_min(self):
        self._ensure_data_loaded()

    def compute_baseline(self):
        mean_temp_per_location = self._data.mean(dim="time")
    
        # Step 2: compute to bring values into memory
        mean_temp_per_location = mean_temp_per_location.compute()
        
        # Step 3: iterate over all lat-lon pairs
        for lat in mean_temp_per_location.lat.values:
            for lon in mean_temp_per_location.lon.values:
                temp = mean_temp_per_location.sel(lat=lat, lon=lon).item()
                print(f"({lat:.2f}, {lon:.2f}) : {temp:.2f} K")

    def compute_stats(self):
        self.compute_baseline()
        computations = {
            "mean": self.compute_mean(),
            "max": self.compute_max(),
            "min": self.compute_min(),
        }
        
        results = dask.compute(*computations.values())
        
        return {key: float(val) for key, val in zip(computations.keys(), results)}