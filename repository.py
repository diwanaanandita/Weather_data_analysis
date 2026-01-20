import xarray as xr

class WeatherRepository:
    def __init__(self, csv_file="weather_data.csv"):
        pass

    def load_netcdf(self, path):
        """Load netCDF data as Xarray DataArray with Dask backend."""
        # Open with chunks for large datasets (adjust based on dims)
        ds = xr.open_dataset(path, chunks={'time': 100, 'lat': 10, 'lon': 10})  # Assuming standard dims; tune as needed
        # Select temperature variable (assuming 'air' for 2m temperature)
        if 'air' in ds:
            da = ds['air']
        else:
            raise ValueError("'air' variable not found in netCDF")
        return da
    
