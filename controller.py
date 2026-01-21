import os 

class WeatherController:
    def __init__(self, service, view, path):
        self.service = service
        self.view = view
        self.netcdf_path = path

    def run(self,operation, baseline_start=None, baseline_end=None):
        self.service.fetch_data(self.netcdf_path)
        self.view.show_message(f"Data loaded from {self.netcdf_path}")

        result = self.service.run_operation(operation, baseline_start=baseline_start, baseline_end=baseline_end)

        if result is not None:
            self.view.show_result(operation, result)
        else:
            self.view.show_message(f"{operation} computed and saved to netCDF file.")

