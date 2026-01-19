import pandas as pd
import xarray as xr
import dask.array as da

class WeatherService:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.xr_data = None

    def load_xarray(self):
        df = pd.read_csv(self.csv_file)
        dask_array = da.from_array(df["temperature"].values, chunks=10)
        self.xr_data = xr.DataArray(dask_array, dims=("time",))
        return self.xr_data

    def compute_stats(self):
        if self.xr_data is None:
            raise ValueError("Data not loaded")
        return {
            "mean": self.xr_data.mean().compute().values,
            "max": self.xr_data.max().compute().values,
            "min": self.xr_data.min().compute().values,
        }
