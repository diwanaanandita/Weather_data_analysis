from repository import WeatherRepository
from service import WeatherService
from view import WeatherView

class WeatherController:
    def __init__(self):
        self.repo = WeatherRepository()
        self.view = WeatherView()
        self.service = None

    def run(self):
        url = "https://api.open-meteo.com/v1/forecast?latitude=28.61&longitude=77.23&hourly=temperature_2m"

        data = self.repo.fetch_json(url)
        csv_file = self.repo.save_to_csv(data)
        self.view.show_message(f"Data saved to {csv_file}")

        self.service = WeatherService(csv_file)
        self.service.load_xarray()

        stats = self.service.compute_stats()

        self.view.show_stats(stats)
