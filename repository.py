import urllib.request
import json
import pandas as pd

class WeatherRepository:
    def __init__(self, csv_file="weather_data.csv"):
        self.csv_file = csv_file

    def fetch_json(self, url):
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            print("Fetched data from URL : ", data)
        return data

    def save_to_csv(self, data):
        times = data['hourly']['time']
        temps = data['hourly']['temperature_2m']
        df = pd.DataFrame({"time": times, "temperature": temps})           
        df.to_csv(self.csv_file, index=False)
        return self.csv_file
