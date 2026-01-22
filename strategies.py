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
