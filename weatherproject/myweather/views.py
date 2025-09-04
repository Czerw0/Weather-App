import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from django.shortcuts import render
from .utils import cities, weather_codes
import requests
from datetime import datetime, timedelta

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image_base64

def weather_view(request):
    context = {"cities": cities}
    if request.method == "POST":
        city_name = request.POST.get("city")
        city = next((c for c in cities if c["name"].lower() == city_name.lower()), None)
        if city:
            latitude = city["latitude"]
            longitude = city["longitude"]
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
            response = requests.get(url)
            data = response.json()
            context["weather"] = data.get("current_weather", {})
            times = data["hourly"]["time"]
            temps = data["hourly"]["temperature_2m"]
            clouds = data["hourly"]["cloudcover"]
            rain = data["hourly"]["rain"]
            rain_prob = data["hourly"]["precipitation_probability"]

            # Convert times to datetime objects
            plot_times = [datetime.fromisoformat(t) for t in times]

            # Temperature plot
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(plot_times, temps, color='tab:red', marker='o')
            ax1.set_title("Temperature (°C)")
            ax1.set_xlabel("Time")
            ax1.set_ylabel("Temperature (°C)")
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
            plt.xticks(rotation=45)
            context["temp_plot"] = plot_to_base64(fig1)

            # Rain and Rain Probability plot
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(plot_times, rain, color='tab:blue', marker='s', label='Rain (mm)')
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Rain (mm)", color='tab:blue')
            ax2.tick_params(axis='y', labelcolor='tab:blue')
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=3))
            plt.xticks(rotation=45)
            ax3 = ax2.twinx()
            ax3.plot(plot_times, rain_prob, color='tab:green', marker='x', label='Rain Probability (%)')
            ax3.set_ylabel("Rain Probability (%)", color='tab:green')
            ax3.tick_params(axis='y', labelcolor='tab:green')
            fig2.legend(['Rain (mm)', 'Rain Probability (%)'], loc='upper left')
            fig2.tight_layout()
            context["rain_plot"] = plot_to_base64(fig2)

            # Cloud cover plot
            fig3, ax4 = plt.subplots(figsize=(10, 4))
            ax4.plot(plot_times, clouds, color='tab:gray', marker='d')
            ax4.set_title("Cloud Cover (%)")
            ax4.set_xlabel("Time")
            ax4.set_ylabel("Cloud Cover (%)")
            ax4.xaxis.set_major_locator(mdates.HourLocator(interval=3))
            plt.xticks(rotation=45)
            context["cloud_plot"] = plot_to_base64(fig3)

            context["forecast"] = zip(
                times, temps, data["hourly"]["weathercode"], clouds, rain, rain_prob,
            )
            context["weather_codes"] = weather_codes
            context["city"] = city_name
    return render(request, "myweather/weather.html", context)