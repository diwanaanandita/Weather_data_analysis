class WeatherView:
    @staticmethod
    def show_message(msg):
        print(msg)

    @staticmethod
    def show_stats(stats):
        print("Weather statistics:")
        for k, v in stats.items():
            print(f"{k.capitalize()}: {v}")
