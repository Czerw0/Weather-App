import requests
from datetime import datetime, timedelta
from Notatio_weather_app import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_weather_and_forecast(latitude, longitude):
    now = datetime.utcnow()
    end_time = now + timedelta(days=2)
    start_date = now.strftime("%Y-%m-%d")
    end_date = end_time.strftime("%Y-%m-%d")

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current_weather=true"
        f"&hourly=temperature_2m,weathercode,cloudcover,rain,precipitation_probability"
        f"&start_date={start_date}&end_date={end_date}"
        f"&timezone=auto"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return

    # Current weather
    current = data.get("current_weather", {})
    print("Current Weather:")
    print(f"  Temperature: {current.get('temperature', 'N/A')}°C")
    print(f"  Windspeed: {current.get('windspeed', 'N/A')} km/h")
    print(f"  Weather: {weather_codes.get(current.get('weathercode'), 'Unknown')}")
    print(f"  Time: {current.get('time', 'N/A')}\n")

    # Forecast for next 2 days (hourly)
    print("Forecast for next 2 days (hourly):")
    times = data.get("hourly", {}).get("time", [])
    temps = data.get("hourly", {}).get("temperature_2m", [])
    codes = data.get("hourly", {}).get("weathercode", [])
    clouds = data.get("hourly", {}).get("cloudcover", [])
    rain = data.get("hourly", {}).get("rain", [])
    rain_prob = data.get("hourly", {}).get("precipitation_probability", [])  # Add this line

    plot_times = []
    plot_temps = []
    plot_clouds = []
    plot_rain = []
    plot_rain_prob = []  # Add this line

    for t, temp, code, cloud, r, rp in zip(times, temps, codes, clouds, rain, rain_prob):
        forecast_time = datetime.fromisoformat(t)
        if now < forecast_time <= end_time:
            print(f"{t}: {temp}°C, Weather: {weather_codes.get(code, 'Unknown')}, Cloud: {cloud}%, Rain: {r}mm, Rain Probability: {rp}%")
            plot_times.append(forecast_time)
            plot_temps.append(temp)
            plot_clouds.append(cloud)
            plot_rain.append(r)
            plot_rain_prob.append(rp)  # Add this line

    # Plot temperature forecast
    if plot_times:
        plt.figure(figsize=(12, 6))
        plt.plot(plot_times, plot_temps, color='tab:red', marker='o', label='Temperature (°C)')
        plt.xlabel("Time")
        plt.ylabel("Temperature (°C)", color='tab:red')
        plt.title("Hourly Temperature Forecast (Next 2 Days)")
        plt.xticks(rotation=60)
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.legend()
        plt.tight_layout()
        plt.show()

    # Plot 2: Rain, rain probability, and cloud cover forecast
    if plot_times:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Rain (mm)", color='tab:green')
        ax1.plot(plot_times, plot_rain, color='tab:green', marker='s', label='Rain (mm)')
        ax1.tick_params(axis='y', labelcolor='tab:green')

        ax2 = ax1.twinx()
        ax2.set_ylabel("Rain Probability (%)", color='tab:purple')
        ax2.plot(plot_times, plot_rain_prob, color='tab:purple', marker='o', label='Rain Probability (%)')
        ax2.tick_params(axis='y', labelcolor='tab:purple')

        # Optional: add cloud cover as a third axis
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.set_ylabel("Cloud Cover (%)", color='tab:blue')
        ax3.plot(plot_times, plot_clouds, color='tab:blue', marker='x', label='Cloud Cover (%)')
        ax3.tick_params(axis='y', labelcolor='tab:blue')

        # Legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')

        plt.title("Hourly Rain, Rain Probability & Cloud Cover Forecast (Next 2 Days)")
        fig.tight_layout()
        plt.show()

if __name__ == "__main__":
    city = input("Enter your city: ").strip()
    found = next((c for c in cities if c["name"].lower() == city.lower()), None)
    if found:
        latitude = found["latitude"]
        longitude = found["longitude"]
    else:
        print("City not found. Available cities:")
        print(", ".join(c["name"] for c in cities))
        try:
            latitude = float(input("Enter latitude: "))
            longitude = float(input("Enter longitude: "))
        except ValueError:
            print("Invalid input. Please enter numeric values for latitude and longitude.")
            exit(1)

    get_weather_and_forecast(latitude, longitude)