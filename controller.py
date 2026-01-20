import os 

class WeatherController:
    def __init__(self, service, view):
        self.service = service
        self.view = view

    def run(self):
        netcdf_path = os.path.join("input_data", "air.2m.gauss.1948.nc")
        self.service.fetch_data(netcdf_path)
        self.view.show_message(f"Data loaded from {netcdf_path}")

        stats = self.service.compute_stats()

        self.view.show_stats(stats)
