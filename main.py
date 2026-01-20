from controller import WeatherController
from service import WeatherService
from repository import WeatherRepository
from view import WeatherView

if __name__ == "__main__":

    view = WeatherView()
    repo = WeatherRepository()
    service = WeatherService(repo)
    controller = WeatherController(service, view)
    
    controller.run()

