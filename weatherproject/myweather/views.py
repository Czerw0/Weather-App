import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
matplotlib.use("Agg") 
matplotlib.rcParams["font.family"] = "Segoe UI Emoji"
import io
import base64
from django.shortcuts import render
from .utils import cities, weather_codes
import requests
from datetime import datetime, timedelta, time 


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image_base64


def weather_view(request):
    search_term = ""
    filtered_cities = cities
    if request.method == "POST":
        search_term = request.POST.get("search", "").strip()
        if search_term:
            filtered_cities = [c for c in cities if search_term.lower() in c["name"].lower()]
        city_name = request.POST.get("city")
        city = next((c for c in filtered_cities if c["name"].lower() == city_name.lower()), None)
        context = {"cities": filtered_cities, "search": search_term}
        if city:
            latitude = city["latitude"]
            longitude = city["longitude"]
            now = datetime.utcnow()
            end_time = now + timedelta(days=3)
            start_date = now.strftime("%Y-%m-%d")
            end_date = end_time.strftime("%Y-%m-%d")
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={latitude}&longitude={longitude}"
                f"&current_weather=true"
                f"&hourly=temperature_2m,weathercode,cloudcover,rain,precipitation_probability,windspeed_10m"
                f"&start_date={start_date}&end_date={end_date}"
                f"&timezone=auto"
                f"&daily=sunrise,sunset" 
            )

            response = requests.get(url)
            data = response.json()
            context["weather"] = data.get("current_weather", {})
            times = data["hourly"]["time"]
            temps = data["hourly"]["temperature_2m"]
            clouds = data["hourly"]["cloudcover"]
            rain = data["hourly"]["rain"]
            rain_prob = data["hourly"]["precipitation_probability"]
            wind_speed = data["hourly"]["windspeed_10m"]

            plt.style.use("seaborn-v0_8-whitegrid")
            plot_times = [datetime.fromisoformat(t) for t in times]

            def shade_night(ax, daily_sunrise, daily_sunset):
                """Shade night as two continuous blocks per day: 00:00→sunrise and sunset→24:00."""
                sunrises = [datetime.fromisoformat(t) for t in daily_sunrise]
                sunsets  = [datetime.fromisoformat(t) for t in daily_sunset]

                for sr, ss in zip(sunrises, sunsets):
                    day_start = datetime(sr.year, sr.month, sr.day, 0, 0)
                    next_mid  = day_start + timedelta(days=1)

                    # Midnight → Sunrise
                    ax.axvspan(day_start, sr, color="grey", alpha=0.25, zorder=0)
                    # Sunset → Midnight
                    ax.axvspan(ss, next_mid,  color="grey", alpha=0.25, zorder=0)

            # ===================== Temperature =====================
            fig1, ax1 = plt.subplots(figsize=(12, 4))
            ax1.plot(plot_times, temps, color='crimson', marker='o', linewidth=2, markersize=6, alpha=0.8)
            shade_night(ax1, data["daily"]["sunrise"], data["daily"]["sunset"])

            ax1.set_xlabel("Hour of Day", fontsize=12)
            ax1.set_ylabel("Temperature (°C)", fontsize=12)
            ax1.tick_params(axis='both', labelsize=10)
            ax1.tick_params(axis='x', rotation=90)

            # Bottom axis = hours
            ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.xticks(rotation=90, ha='center')

            # Top axis = days
            ax1_top = ax1.secondary_xaxis('top')
            ax1_top.xaxis.set_major_locator(mdates.DayLocator())
            ax1_top.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax1_top.set_xlabel("Day", fontsize=12)
            

            fig1.tight_layout()
            context["temp_plot"] = plot_to_base64(fig1)
            plt.close(fig1)

            # ===================== Rain & Rain Probability =====================
            fig2, ax2 = plt.subplots(figsize=(12, 4))
            ax2.bar(plot_times, rain, color='royalblue', alpha=0.6, label='Rain (mm)', width=0.05)
            ax2.set_ylabel("Rain (mm)", fontsize=12, color='royalblue')
            ax2.tick_params(axis='y', labelcolor='royalblue')
            shade_night(ax2, data["daily"]["sunrise"], data["daily"]["sunset"])
            ax2.set_ylim(0, max(rain) * 1.2 if max(rain) > 0 else 1)

            # Bottom axis = hours
            ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax2.tick_params(axis='x', rotation=90)
            plt.xticks(rotation=90, ha='center')

            # Top axis = days
            ax2_top = ax2.secondary_xaxis('top')
            ax2_top.xaxis.set_major_locator(mdates.DayLocator())
            ax2_top.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax2_top.set_xlabel("Day", fontsize=12)

            # Twin axis for rain probability
            ax2 = ax2.twinx()
            ax2.plot(plot_times, rain_prob, color='seagreen', marker='x', linewidth=2, markersize=6, alpha=0.8, label='Rain Probability (%)')
            ax2.set_ylabel("Rain Probability (%)", fontsize=12, color='seagreen')
            ax2.tick_params(axis='y', labelcolor='seagreen')
            ax2.set_ylim(0, 100)

            fig2.suptitle("Rain & Rain Probability", fontsize=16, fontweight="bold", y=1.05)
            fig2.legend(loc='upper left', frameon=True, fontsize=10)
            fig2.tight_layout()
            context["rain_plot"] = plot_to_base64(fig2)
            plt.close(fig2)

            # ===================== Cloud Cover =====================
            fig3, ax3 = plt.subplots(figsize=(12, 4))
            ax3.plot(plot_times, clouds, color='dimgray', marker='D', linewidth=2, markersize=5, alpha=0.8)
            shade_night(ax3, data["daily"]["sunrise"], data["daily"]["sunset"])

            ax3.set_ylabel("Cloud Cover (%)", fontsize=12)
            ax3.tick_params(axis='both', labelsize=10)
            ax3.set_ylim(0, 100)

            # Bottom axis = hours
            plt.xticks(rotation=90, ha='center')
            ax3.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.xticks(rotation=90, ha='center')

            # Top axis = days
            ax3_top = ax3.secondary_xaxis('top')
            ax3_top.xaxis.set_major_locator(mdates.DayLocator())
            ax3_top.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax3_top.set_xlabel("Day", fontsize=12)
            fig3.tight_layout()
            context["cloud_plot"] = plot_to_base64(fig3)
            plt.close(fig3)

            #=========================== Wind =======================
            # Add text in the center
            fig4, ax4 = plt.subplots(figsize=(12, 4))
            ax4.bar(plot_times, wind_speed, color='royalblue', alpha=0.6, label='Wind (km/h)', width=0.05)
            ax4.set_ylabel("Wind (km/h)", fontsize=12, color='royalblue')
            ax4.tick_params(axis='y', labelcolor='royalblue')
            shade_night(ax4, data["daily"]["sunrise"], data["daily"]["sunset"])

            # Bottom axis = hours
            ax4.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax4.tick_params(axis='x', rotation=90)
            plt.xticks(rotation=90, ha='center')

            # Top axis = days
            ax4_top = ax4.secondary_xaxis('top')
            ax4_top.xaxis.set_major_locator(mdates.DayLocator())
            ax4_top.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            ax4_top.set_xlabel("Day", fontsize=12)

            fig4.suptitle("Wind speed", fontsize=16, fontweight="bold", y=1.05)
            fig4.legend(loc='upper left', frameon=True, fontsize=10)
            fig4.tight_layout()
            context["wind_plot"] = plot_to_base64(fig4)
            plt.close(fig4)


            context["weather_codes"] = weather_codes
            context["city"] = city_name
        else:
            context = {"cities": filtered_cities, "search": search_term}
    else:
        context = {"cities": cities, "search": ""}
    return render(request, "myweather/weather.html", context)