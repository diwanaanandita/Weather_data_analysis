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
        choices=["mean", "max", "min", "baseline", "anomaly"],
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

        choice = input("\nEnter choice (1/2/3/4/5): ").strip()

        mapping = {
            "1": "mean",
            "2": "max",
            "3": "min",
            "4": "baseline",
            "5": "anomaly"
        }

        if choice not in mapping:
            print("Invalid choice")
            sys.exit(1)

        args.operation = mapping[choice]

    baseline_start = None
    baseline_end = None

    if args.operation == "baseline" or args.operation == "anomaly":
        baseline_start = int(input("\nEnter baseline start year greater than 1947: ").strip())
        baseline_end = int(input("\nEnter baseline end year less than 1958: ").strip())

        if baseline_start > baseline_end:
            print("Start year must be <= end year")
            sys.exit(1)

    return args.operation, baseline_start, baseline_end


if __name__ == "__main__":
    operation, baseline_start, baseline_end = parse_args()
    NETCDF_PATH = "input_data"
    OUTDIR = "output"
    os.makedirs(OUTDIR, exist_ok=True)

    view = WeatherView()
    repo = WeatherRepository()
    service = WeatherService(repo, OUTDIR)
    controller = WeatherController(service, view, NETCDF_PATH)

    controller.run(operation, baseline_start, baseline_end)