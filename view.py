class WeatherView:
    
    @staticmethod
    def get_user_input(prompt):
        return input(prompt)
    
    @staticmethod
    def show_message(msg):
        print(msg)

    @staticmethod
    def show_stats(stats):
        print("Weather statistics:")
        for k, v in stats.items():
            print(f"{k.capitalize()}: {v}")
















































    
    # @staticmethod
    # def plot_anomaly(anomaly, year):
    #     """Plot global map of temperature anomaly for a specific year."""
    #     fig, ax = plt.subplots(figsize=(12, 8))
    #     anomaly.plot(
    #         ax=ax,
    #         cmap='RdBu_r',
    #         cbar_kwargs={'label': 'Temperature Anomaly (°C)'}
    #     )
    #     ax.set_title(f'Global Temperature Anomaly - Year {year}')
    #     ax.set_xlabel('Longitude')
    #     ax.set_ylabel('Latitude')
        
    #     # Save and show
    #     output_path = f"output/anomaly_map_{year}.png"
    #     plt.savefig(output_path, dpi=150, bbox_inches='tight')
    #     print(f"Plot saved to {output_path}")
    #     plt.show()
