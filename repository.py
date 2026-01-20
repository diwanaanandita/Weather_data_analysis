import xarray as xr

class WeatherRepository:
    def __init__(self):
        pass

    def load_data(self, path):
        """Load netCDF data as Xarray DataArray with Dask backend."""
        ds = xr.open_dataset(path, chunks={'time': 100, 'lat': 10, 'lon': 10})  

        if "air" not in ds:
            raise ValueError("'air' variable not found")
        return ds["air"]