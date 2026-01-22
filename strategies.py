from abc import ABC, abstractmethod


class WeatherOperationStrategy(ABC):
    @abstractmethod
    def execute(self, service, view, **kwargs):
        pass


class MeanStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        path = kwargs.get("path")
        result = service.compute_mean(path)
        view.show_result("Mean temperature", result)


class MaxStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        path = kwargs.get("path")
        result = service.compute_max(path)
        view.show_result("Max temperature", result)


class MinStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        path = kwargs.get("path")
        result = service.compute_min(path)
        view.show_result("Min temperature", result)


class BaselineStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        path = kwargs.get("path")
        start = kwargs.get("baseline_start")
        end = kwargs.get("baseline_end")


        service.compute_and_save_baseline(path,start, end)
        view.show_message(
            f"Baseline computed and saved ({start}–{end})"
        )


class AnomalyStrategy(WeatherOperationStrategy):
    def execute(self, service, view, **kwargs):
        path = kwargs.get("path")
        start = kwargs.get("baseline_start")
        end = kwargs.get("baseline_end")

        service.compute_and_save_anomaly(path, start, end)
        view.show_message(
            f"Anomaly computed and saved ({start}–{end})"
        )

class LocationAnomalyStrategy(WeatherOperationStrategy):
    
    def execute(self, service, view, **kwargs):
        lat = kwargs.get("latitude")
        lon = kwargs.get("longitude")
        
        if lat is None or lon is None:
            view.show_message("Error: latitude and longitude required")
            return
        
        try:
            location_data = service.get_location_anomaly(lat, lon)
            view.show_location_data(location_data, lat, lon)
        except Exception as e:
            view.show_message(f"Error retrieving location anomaly: {str(e)}")

class LocationBaselineStrategy(WeatherOperationStrategy):
    
    def execute(self, service, view, **kwargs):
        lat = kwargs.get("latitude")
        lon = kwargs.get("longitude")
        
        if lat is None or lon is None:
            view.show_message("Error: latitude and longitude required")
            return
        
        try:
            location_data = service.get_location_baseline(lat, lon)
            view.show_location_data(location_data, lat, lon)
        except Exception as e:
            view.show_message(f"Error retrieving location baseline: {str(e)}")