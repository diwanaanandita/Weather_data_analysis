class WeatherView:
    @staticmethod
    def show_message(msg):
        print(msg)

    def show_result(self, operation, value):
        print(f"{operation.upper()} temperature: {value}")

    @staticmethod
    def show_location_data(location_data, lat, lon):
        df = location_data.to_pandas().reset_index()
        if "year" in df.columns:
            df.columns = ["Year", "Temperature (°C)"]

        print("\n" + "=" * 60)
        print(f"Location: Latitude {lat:.2f}°, Longitude {lon:.2f}°")
        print("=" * 60)
        print(df.to_string(index=False))
        print("=" * 60)
        print()
