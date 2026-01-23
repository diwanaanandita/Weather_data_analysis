import dask


ANOMALY_FILE_NAME = "temperature_anomaly.nc"
BASELINE_FILE_NAME = "baseline.nc"
YEARLY_AVG_FILE_NAME = "yearly_average.nc"
DIMENSION_TEMPERATURE_ANOMALY = "temperature_anomaly"
DIMENSION_TEMPERATURE_BASELINE = "baseline_temperature"
DIMENSION_TEMPERATURE_YEARLY_AVG = "yearly_mean_temperature"


class WeatherService:
    def __init__(self, repository):
        self.repo = repository

    def _ensure_data_loaded(self, data):
        if data is None:
            raise RuntimeError("Data not loaded. Call fetch_data() first.")

    def compute_mean(self):
        data = self.repo.read_data()
        self._ensure_data_loaded(data)
        result = data["air"].mean()
        (result,) = dask.compute(result)
        return float(result)

    def compute_max(self):
        data = self.repo.read_data()
        self._ensure_data_loaded(data)
        result = data["air"].max()
        (result,) = dask.compute(result)
        return float(result)

    def compute_min(self):
        data = self.repo.read_data()
        self._ensure_data_loaded(data)
        result = data["air"].min()
        (result,) = dask.compute(result)
        return float(result)

    def compute_yearly_average(self):
        data = self.repo.read_data()
        self._ensure_data_loaded(data)
        if "air" not in getattr(data, "data_vars", {}):
            raise RuntimeError("air not found; call convert_kelvin_to_celsius() first")
        yearly_avg = data["air"].groupby("time.year").mean(dim="time")
        yearly_avg.name = DIMENSION_TEMPERATURE_YEARLY_AVG
        yearly_avg = yearly_avg.persist()
        return yearly_avg

    def compute_baseline(self, yearly_avg, baseline_start, baseline_end):
        if yearly_avg is None:
            raise RuntimeError(
                "yearly_avg not computed; call compute_yearly_average() first"
            )
        if baseline_start is None or baseline_end is None:
            raise RuntimeError(
                "baseline_start and baseline_end must be set before computing baseline"
            )
        baseline = yearly_avg.sel(year=slice(baseline_start, baseline_end)).mean(
            dim="year"
        )
        baseline = baseline.expand_dims(year=yearly_avg.year)
        baseline.name = DIMENSION_TEMPERATURE_BASELINE
        baseline = baseline.persist()
        return baseline

    def compute_temperature_anomaly(self, yearly_avg, baseline):
        if yearly_avg is None or baseline is None:
            raise RuntimeError("yearly_avg and baseline must be computed first")
        anomaly = yearly_avg - baseline
        anomaly.name = DIMENSION_TEMPERATURE_ANOMALY
        anomaly = anomaly.persist()
        return anomaly

    def _validate_years(self, start, end):
        if start < int("1948") or end > int("1957"):
            raise ValueError("Baseline start and end years outside range 1948-1957 \n")
        if start > end:
            raise ValueError("Baseline start year must be <= end year \n")

    def _validate_coordinates(self, lat, lon):
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")

    def _compute_and_save(self, baseline_start, baseline_end, include_anomaly):
        self._validate_years(baseline_start, baseline_end)
        baseline_start = baseline_start
        baseline_start = baseline_end
        yearly_avg = self.compute_yearly_average()
        baseline = self.compute_baseline(yearly_avg, baseline_start, baseline_end)

        outputs = {
            YEARLY_AVG_FILE_NAME: yearly_avg,
            BASELINE_FILE_NAME: baseline,
        }

        if include_anomaly:
            anomaly = self.compute_temperature_anomaly(yearly_avg, baseline)
            outputs[ANOMALY_FILE_NAME] = anomaly
        self.repo.write_data(outputs)

    def compute_and_save_baseline(self, baseline_start, baseline_end):
        self._compute_and_save(baseline_start, baseline_end, include_anomaly=False)

    def compute_and_save_anomaly(self, baseline_start, baseline_end):
        self._compute_and_save(baseline_start, baseline_end, include_anomaly=True)

    def get_location_data(self, lat, lon, file_name, dimension):
        self._validate_coordinates(lat, lon)
        data_ds = self.repo.load_output(file_name)
        location = data_ds[dimension].sel(lat=lat, lon=lon, method="nearest")
        return location

    def get_location_anomaly(self, lat, lon):
        return self.get_location_data(
            lat, lon, ANOMALY_FILE_NAME, DIMENSION_TEMPERATURE_ANOMALY
        )

    def get_location_baseline(self, lat, lon):
        return self.get_location_data(
            lat, lon, BASELINE_FILE_NAME, DIMENSION_TEMPERATURE_BASELINE
        )
