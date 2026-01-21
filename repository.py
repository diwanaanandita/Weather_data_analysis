import xarray as xr
import os
import glob


class WeatherRepository:
   
    
    INPUT_DIR = "input_data"
    NETCDF_PATTERN = "air.2m.gauss.*.nc"
    
    def __init__(self, csv_file="weather_data.csv"):
        pass

    def get_netcdf_files(self):
      
        pattern = os.path.join(self.INPUT_DIR, self.NETCDF_PATTERN)
        files = sorted(glob.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No netCDF files found matching {pattern}")
        return files

    def load_netcdf(self, files):

        # Open with chunks for large datasets (adjust based on dims)
        ds = xr.open_mfdataset(files, chunks="auto", engine='netcdf4')
        # Ensure the expected temperature variable exists in the dataset
        if 'air' not in ds:
            raise ValueError("'air' variable not found in netCDF")
        # Return the full Dataset so downstream code can access/add variables
        return ds
    











































    
    def load_anomaly(self, year):
        """Load temperature anomaly for a specific year from output files."""
        anomaly_path = os.path.join("output", "temperature_anomaly.nc")
        if not os.path.exists(anomaly_path):
            raise FileNotFoundError(f"Anomaly data not found at {anomaly_path}. Run compute first.")
        ds = xr.open_dataset(anomaly_path)
        if "temperature_anomaly" not in ds.data_vars:
            raise ValueError("temperature_anomaly variable not found in output file")
        
        # Get available years
        available_years = list(ds.coords['year'].values)
        year_int = int(year)
        
        if year_int not in available_years:
            raise ValueError(f"Year {year} not found in anomaly data. Available years: {available_years}")
        
        # Select data for the specific year
        anomaly = ds["temperature_anomaly"].sel(year=year_int)
        return anomaly
