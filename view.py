class WeatherView:
    @staticmethod
    def show_message(msg):
        print(msg)

    @staticmethod
    def show_stats(operation):
        print("Weather statistics:")
        for k, v in operation.items():
            print(f"{k.capitalize()}: {v}")

    def show_result(self, operation, value):
        print(f"{operation.upper()} temperature: {value}")