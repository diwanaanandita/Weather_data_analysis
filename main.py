import argparse
import sys
import os

from controller import WeatherController
from service import WeatherService
from repository import WeatherRepository
from view import WeatherView


def parse_args():
    parser = argparse.ArgumentParser(
        description="Weather CLI application"
    )

    parser.add_argument(
        "operation",
        choices=["mean", "max", "min", "baseline", "anomaly", "location_anomaly", "location_baseline"],
        nargs="?",
        help="Operation to perform"
    )

    args = parser.parse_args()

    if args.operation is None:
        print("\nSelect an operation:")
        print("1. Mean temperature")
        print("2. Max temperature")
        print("3. Min temperature")
        print("4. Baseline")
        print("5. Anomaly")
        print("6. Location anomaly")
        print("7. Location baseline")

        choice = input("\nEnter choice (1/2/3/4/5/6/7): ").strip()

        mapping = {
            "1": "mean",
            "2": "max",
            "3": "min",
            "4": "baseline",
            "5": "anomaly",
            "6": "location_anomaly",
            "7": "location_baseline"
        }

        if choice not in mapping:
            print("Invalid choice")
            sys.exit(1)

        args.operation = mapping[choice]

    baseline_start = None
    baseline_end = None
    latitude = None
    longitude = None

    if args.operation == "baseline" or args.operation == "anomaly":
        baseline_start = int(input("\nEnter baseline start year greater than 1947: ").strip())
        baseline_end = int(input("\nEnter baseline end year less than 1958: ").strip())

    elif args.operation == "location_anomaly" or args.operation == "location_baseline":
            
            latitude = float(input("\nEnter latitude (-90 to 90): ").strip())
            longitude = float(input("Enter longitude (-180 to 180): ").strip())
            
    return args.operation, baseline_start, baseline_end, latitude, longitude


if __name__ == "__main__":
    operation, baseline_start, baseline_end, latitude, longitude = parse_args()
    NETCDF_PATH = "input_data"
    OUTDIR = "output"
    os.makedirs(OUTDIR, exist_ok=True)

    view = WeatherView()
    repo = WeatherRepository()
    service = WeatherService(repo, OUTDIR)
    controller = WeatherController(service, view, NETCDF_PATH)

    controller.run(operation, baseline_start, baseline_end, latitude, longitude)