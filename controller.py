from repository import WeatherRepository
from service import WeatherService
from view import WeatherView


class WeatherController:

    BASELINE_START = "1948"
    BASELINE_END = "1957"
    
    def __init__(self):

        self.repo = WeatherRepository()
        self.view = WeatherView()
        self.service = None

    def run(self):
        
        while True:
            user_input = self.view.get_user_input("Enter compute, visualize <year>, or exit: ")
            if user_input == "exit":
                break
            elif user_input == "compute":
                self._handle_compute()
            elif user_input.startswith("visualize"):
                self._handle_visualize(user_input)
    
    def _handle_compute(self):
       
        try:
            self.view.show_message("Computing yearly average, baseline, and temperature anomaly...")
            
            # Load data
            files = self.repo.get_netcdf_files()
            self.view.show_message(f"Loading netCDF data...")
            xr_data = self.repo.load_netcdf(files)
            self.view.show_message(f"Data loaded successfully.")

            # Initialize and configure service
            self.service = WeatherService(xr_data)

            # Compute and save
            self.service.compute_and_save_to_netcdf(self.BASELINE_START, self.BASELINE_END)
            compute_stats = self.service.compute_stats()
            self.view.show_stats(compute_stats)
            self.view.show_message("Computed yearly average, baseline, and temperature anomaly, and saved to netCDF files.")
        except Exception as e:
            self.view.show_message(f"Error during compute: {str(e)}")
    
    def _handle_visualize(self, user_input):
        pass


















































        # """Parse visualize command and plot anomaly for requested year."""
        # parts = user_input.split()
        # if len(parts) < 2:
        #     self.view.show_message("Usage: visualize <year>")
        #     return
        
        # year = parts[1]
        # try:
        #     self.view.show_message(f"Loading anomaly data for year {year}...")
        #     anomaly = self.repo.load_anomaly(year)
        #     self.view.show_message(f"Plotting global temperature anomaly map for {year}...")
        #     self.view.plot_anomaly(anomaly, year)
        # except Exception as e:
        #     self.view.show_message(f"Error: {str(e)}")
