class WeatherController:
    def __init__(self, service, view, path):
        self.service = service
        self.view = view
        self.netcdf_path = path

    def run(self, operation, baseline_start=None, baseline_end=None):

        self.service.fetch_data(self.netcdf_path)
        self.view.show_message(f"Data loaded from {self.netcdf_path}")

        if operation == "mean":
            result = self.service.compute_mean()
            self.view.show_result("Mean temperature", result)

        elif operation == "max":
            result = self.service.compute_max()
            self.view.show_result("Max temperature", result)

        elif operation == "min":
            result = self.service.compute_min()
            self.view.show_result("Min temperature", result)

        elif operation == "baseline":
            self.service.compute_and_save_baseline(baseline_start, baseline_end)
            self.view.show_message(
                f"Baseline computed and saved ({baseline_start}–{baseline_end})"
            )

        elif operation == "anomaly":
            self.service.compute_and_save_anomaly(baseline_start, baseline_end)
            self.view.show_message(
                f"Anomaly computed and saved ({baseline_start}–{baseline_end})"
            )

        else:
            raise ValueError(f"Unsupported operation: {operation}")