from repository import WeatherRepository
from service import WeatherService
from view import WeatherView
import os 

class WeatherController:
    def __init__(self):
        self.repo = WeatherRepository()
        self.view = WeatherView()
        self.service = None

    def run(self):

        netcdf_path = os.path.join("input_data", "air.2m.gauss.1948.nc")

        xr_data = self.repo.load_netcdf(netcdf_path)
        self.view.show_message(f"Data loaded from {netcdf_path}")

        self.service = WeatherService(xr_data)
        stats = self.service.compute_stats()

        self.view.show_stats(stats)
