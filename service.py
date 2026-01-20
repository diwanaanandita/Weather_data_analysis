import xarray as xr
import dask

class WeatherService:
    def __init__(self, xr_data):
        self.xr_data = xr_data

    def compute_mean(self):
        return self.xr_data.mean()

    def compute_max(self):
        return self.xr_data.max()

    def compute_min(self):
        return self.xr_data.min()

    def compute_stats(self):

        computations = {
            "mean": self.compute_mean(),
            "max": self.compute_max(),
            "min": self.compute_min(),
        }
        
        # Compute all at once using dask.compute
        results = dask.compute(*computations.values())
        
        # Build dict with computed values
        return {key: float(val) for key, val in zip(computations.keys(), results)}