import xarray as xr
import dask.array as da
import glob
import os

# =========================
# 1. CONFIGURATION
# =========================

DATA_DIR = "input_data/"
OUTPUT_DIR = "output/"

BASELINE_START = "1948"
BASELINE_END = "1957"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# 2. LOAD MULTIPLE YEARS (LAZY)
# =========================

files = sorted(glob.glob(f"{DATA_DIR}/air.2m.gauss.*.nc"))

ds = xr.open_mfdataset(
    files,
    combine="by_coords",
    chunks={"time": 200, "lat": 30, "lon": 30}
)

# =========================
# 3. UNIT CONVERSION
# =========================
# Kelvin → Celsius

ds["air_c"] = ds["air"] - 273.15
ds["air_c"].attrs["units"] = "Celsius"

# =========================
# 4. YEARLY AVERAGE
# =========================

yearly_avg = (
    ds["air_c"]
    .groupby("time.year")
    .mean(dim="time")
)

yearly_avg.name = "yearly_mean_temperature"

# =========================
# 5. BASELINE CALCULATION
# =========================

baseline = (
    yearly_avg
    .sel(year=slice(BASELINE_START, BASELINE_END))
    .mean(dim="year")
)

baseline.name = "baseline_temperature"

# =========================
# 6. TEMPERATURE ANOMALY
# =========================

anomaly = yearly_avg - baseline
anomaly.name = "temperature_anomaly"

# =========================
# 7. SAVE RESULTS
# =========================

yearly_avg.to_netcdf(f"{OUTPUT_DIR}/yearly_average.nc")
baseline.to_netcdf(f"{OUTPUT_DIR}/baseline.nc")
anomaly.to_netcdf(f"{OUTPUT_DIR}/temperature_anomaly.nc")
print("====================================================")
print("baseline")
print(baseline.compute())

print("✅ Climate analysis completed successfully")
