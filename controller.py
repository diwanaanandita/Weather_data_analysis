from abc import ABC, abstractmethod


class WeatherOperationStrategy(ABC):
    @abstractmethod
    def execute(self, service, view, **kwargs):
        pass


class MeanStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        result = service.compute_mean()
        view.show_result("Mean temperature", result)


class MaxStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        result = service.compute_max()
        view.show_result("Max temperature", result)


class MinStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        result = service.compute_min()
        view.show_result("Min temperature", result)


class BaselineStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        start = kwargs.get("baseline_start")
        end = kwargs.get("baseline_end")

        service.compute_and_save_baseline(start, end)
        view.show_message(f"Baseline computed and saved ({start}–{end})")


class AnomalyStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        start = kwargs.get("baseline_start")
        end = kwargs.get("baseline_end")

        service.compute_and_save_anomaly(start, end)
        view.show_message(f"Anomaly computed and saved ({start}–{end})")


class LocationAnomalyStrategy(WeatherOperationStrategy):

    def execute(self, service, view, latitude, longitude, **kwargs):

        try:
            location_data = service.get_location_anomaly(latitude, longitude)
            view.show_location_data(location_data, latitude, longitude)
        except Exception as e:
            view.show_message(f"Error retrieving location anomaly: {str(e)}")


class LocationBaselineStrategy(WeatherOperationStrategy):

    def execute(self, service, view, latitude, longitude, **kwargs):
        try:
            location_data = service.get_location_baseline(latitude, longitude)
            view.show_location_data(location_data, latitude, longitude)
        except Exception as e:
            view.show_message(f"Error retrieving location baseline: {str(e)}")
