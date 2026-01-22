from strategies import (
    MeanStrategy,
    MaxStrategy,
    MinStrategy,
    BaselineStrategy,
    AnomalyStrategy,
)


class WeatherController:
    STRATEGY_MAP = {
        "mean": MeanStrategy(),
        "max": MaxStrategy(),
        "min": MinStrategy(),
        "baseline": BaselineStrategy(),
        "anomaly": AnomalyStrategy(),
    }

    def __init__(self, service, view, path):
        self.service = service
        self.view = view
        self.netcdf_path = path

    def run(self, operation, baseline_start=None, baseline_end=None):

        strategy = self.STRATEGY_MAP.get(operation)

        if not strategy:
            raise ValueError(f"Unsupported operation: {operation}")

        strategy.execute(
            service=self.service,
            view=self.view,
            path=self.netcdf_path,
            baseline_start=baseline_start,
            baseline_end=baseline_end,

        )
