import xarray as xr
import os
import glob

class WeatherRepository:
    def __init__(self):
        self.NETCDF_PATTERN = "air.2m.gauss.*.nc"

    def load_data(self, path):
        pattern = os.path.join(path, self.NETCDF_PATTERN)
        files = sorted(glob.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No netCDF files found matching {pattern}")
        return self.load_netcdf(files)


    def load_netcdf(self, files):

        ds = xr.open_mfdataset(files, chunks="auto", engine='netcdf4')

        if 'air' not in ds:
            raise ValueError("'air' variable not found in netCDF")
        return ds