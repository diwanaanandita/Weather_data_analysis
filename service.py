import xarray as xr
import dask.dataframe as dd

class WeatherService:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.xr_data = None

    def load_xarray(self):
        """Load CSV as Dask DataFrame and convert to Xarray."""
        ddf = dd.read_csv(self.csv_file, assume_missing=True)
        breakpoint()
        self.xr_data = xr.DataArray(
            ddf["temperature"],
            dims="time",
            coords={"time": ddf["time"]}
        )
        return self.xr_data
    
#not a dask array; dask.array_random
    def compute_mean(self):
        return float(self.xr_data.mean().compute())

    def compute_median(self):
        return float(self.xr_data.median().compute())

    def compute_max(self):
        return float(self.xr_data.max().compute())

    def compute_min(self):
        return float(self.xr_data.min().compute())
    #

    def compute_stats(self):
        return {
            "mean": self.compute_mean(),
            "median": self.compute_median(),
            "max": self.compute_max(),
            "min": self.compute_min(),
        }
#combine computes