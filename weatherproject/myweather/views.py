import base64
import io
from datetime import datetime, timedelta

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
from django.shortcuts import render

from .utils import cities, weather_codes

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "Segoe UI Emoji"


def plot_to_base64(fig):
    """Converts a Matplotlib figure to a base64 encoded string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image_base64


def _shade_night(ax, daily_sunrise, daily_sunset):
    """Adds a shaded background to the plot during nighttime hours."""
    sunrises = [datetime.fromisoformat(t) for t in daily_sunrise]
    sunsets = [datetime.fromisoformat(t) for t in daily_sunset]
    for sr, ss in zip(sunrises, sunsets):
        day_start = sr.replace(hour=0, minute=0, second=0, microsecond=0)
        ax.axvspan(day_start, sr, color="grey", alpha=0.2, zorder=0)
        ax.axvspan(ss, day_start + timedelta(days=1), color="grey", alpha=0.2, zorder=0)


def _setup_plot_axes(ax, hour_interval, daily_sunrise, daily_sunset):
    """Configures the common elements for all weather plots."""
    _shade_night(ax, daily_sunrise, daily_sunset)
    # Configure bottom axis for hours
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=hour_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params(axis='x', rotation=90)
    ax.set_xlabel("Hour of Day", fontsize=12)

    # Configure top axis for days
    ax_top = ax.secondary_xaxis('top')
    ax_top.xaxis.set_major_locator(mdates.DayLocator())
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax_top.set_xlabel("Day", fontsize=12)


def weather_view(request):
    days_options = [(i, f"{i} Day{'s' if i > 1 else ''}") for i in range(1, 8)]

    context = {
        "cities": sorted(cities, key=lambda c: c["name"].lower()),
        "search": request.POST.get("search", "").strip(),
        "days_options": days_options,
        "selected_days": 2,  # Default value
    }

    # Filter cities based on search term
    if context["search"]:
        search_term = context["search"].lower()
        context["cities"] = [
            c for c in context["cities"] if search_term in c["name"].lower()
        ]

    if request.method == "POST":
        city_name = request.POST.get("city")
        selected_days = int(request.POST.get("days", 2))
        context["selected_days"] = selected_days

        city = next((c for c in context["cities"] if c["name"].lower() == city_name.lower()), None)

        if city:
            context["city"] = city_name
            try:
                # --- API Data Fetching ---
                now = datetime.utcnow()
                params = {
                    "latitude": city["latitude"],
                    "longitude": city["longitude"],
                    "current_weather": "true",
                    "hourly": "temperature_2m,cloudcover,rain,precipitation_probability,windspeed_10m,windgusts_10m,pressure_msl,uv_index",
                    "daily": "sunrise,sunset",
                    "start_date": now.strftime("%Y-%m-%d"),
                    "end_date": (now + timedelta(days=selected_days)).strftime("%Y-%m-%d"),
                    "timezone": "auto",
                }
                url = "https://api.open-meteo.com/v1/forecast"
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # --- Data Extraction and Processing ---
                hourly_data = data["hourly"]
                daily_data = data["daily"]

                plot_times = [datetime.fromisoformat(t) for t in hourly_data["time"]]
                temps = hourly_data["temperature_2m"]
                clouds = hourly_data["cloudcover"]
                rain = hourly_data["rain"]
                rain_prob = hourly_data["precipitation_probability"]
                wind_speed = hourly_data["windspeed_10m"]
                wind_gusts = hourly_data["windgusts_10m"]
                
                context.update({
                    "weather": data.get("current_weather", {}),
                    "weather_codes": weather_codes,
                    "daily_sunrise": daily_data["sunrise"],
                    "daily_sunset": daily_data["sunset"],
                    "clouds": clouds,
                    "pressure": hourly_data["pressure_msl"],
                    "uv_index": hourly_data["uv_index"],
                })

                # --- Plotting Configuration ---
                if selected_days <= 2:
                    hour_interval = 1
                elif selected_days <= 5:
                    hour_interval = 2
                else:
                    hour_interval = 4
                

                #Alerts 
                for i in range(0,25):
                    if rain_prob[i] > 50 and rain[i] > 0.2:
                        context["alert"] = "It's likely to rain today. Don't forget your umbrella!"
                        break
                    if wind_gusts[i] > 40:
                        context["alert"] = "Strong winds expected today. Stay safe!"
                        break
                    if temps[i] > 30:
                        context["alert"] = "High temperatures expected today. Stay hydrated!"
                        break
                    if temps[i] < 0:
                        context["alert"] = "Freezing temperatures expected today. Dress warmly!"
                        break

                # --- Temperature Plot ---
                fig1, ax1 = plt.subplots(figsize=(13, 5))
                plt.grid(visible=True, which='major', axis='y', linestyle='--', alpha=0.7)
                plt.grid(visible=True, which='major', axis='x', linestyle='--', alpha=0.7)
                ax1.plot(plot_times, temps, color='crimson', marker='o', linewidth=2, markersize=6, alpha=0.8)
                ax1.set_ylabel("Temperature (°C)", fontsize=12)
                _setup_plot_axes(ax1, hour_interval, daily_data["sunrise"], daily_data["sunset"])
                fig1.tight_layout()
                context["temp_plot"] = plot_to_base64(fig1)

                # --- Rain & Rain Probability Plot ---
                fig2, ax2 = plt.subplots(figsize=(13, 5))
                plt.grid(visible=True, which='major', axis='y', linestyle='--', alpha=0.7)
                plt.grid(visible=True, which='major', axis='x', linestyle='--', alpha=0.7)
                ax2.bar(plot_times, rain, color='royalblue', alpha=0.6, label='Rain (mm)', width=0.05)
                ax2.set_ylabel("Rain (mm)", fontsize=12, color='royalblue')
                ax2.tick_params(axis='y', labelcolor='royalblue')
                ax2.set_ylim(0, max(rain) * 1.2 if max(rain) > 0 else 1)

                ax2_twin = ax2.twinx()
                ax2_twin.plot(plot_times, rain_prob, color='seagreen', marker='x', linewidth=2, markersize=6, alpha=0.8, label='Rain Probability (%)')
                ax2_twin.set_ylabel("Rain Probability (%)", fontsize=12, color='seagreen')
                ax2_twin.tick_params(axis='y', labelcolor='seagreen')
                ax2_twin.set_ylim(0, 100)
                
                _setup_plot_axes(ax2, hour_interval, daily_data["sunrise"], daily_data["sunset"])
                fig2.suptitle("Rain & Rain Probability", fontsize=16, fontweight="bold", y=1.05)
                fig2.legend(loc='upper left', frameon=True, fontsize=12)
                fig2.tight_layout()
                context["rain_plot"] = plot_to_base64(fig2)

                # --- Cloud Cover Plot ---
                fig3, ax3 = plt.subplots(figsize=(13, 5))
                plt.grid(visible=True, which='major', axis='y', linestyle='--', alpha=0.7)
                plt.grid(visible=True, which='major', axis='x', linestyle='--', alpha=0.7)
                ax3.plot(plot_times, clouds, color='dimgray', marker='D', linewidth=2, markersize=5, alpha=0.8)
                ax3.set_ylabel("Cloud Cover (%)", fontsize=12)
                ax3.set_ylim(0, 100)
                _setup_plot_axes(ax3, hour_interval, daily_data["sunrise"], daily_data["sunset"])
                fig3.tight_layout()
                context["cloud_plot"] = plot_to_base64(fig3)

                # --- Wind Speed and Gusts Plot ---
                fig4, ax4 = plt.subplots(figsize=(13, 5))
                plt.grid(visible=True, which='major', axis='y', linestyle='--', alpha=0.7)
                gust_difference = [max(0, g - s) for g, s in zip(wind_gusts, wind_speed)]
                ax4.bar(plot_times, wind_speed, color='royalblue', alpha=0.7, label='Wind Speed (km/h)', width=0.05)
                ax4.bar(plot_times, gust_difference, bottom=wind_speed, color='lightcoral', alpha=0.7, label='Wind Gust (km/h)', width=0.05)
                ax4.set_ylabel("Wind Speed (km/h)", fontsize=12)
                
                _setup_plot_axes(ax4, hour_interval, daily_data["sunrise"], daily_data["sunset"])
                fig4.suptitle("Wind Speed and Gusts", fontsize=16, fontweight="bold", y=1.05)
                fig4.legend(loc='upper left', frameon=True, fontsize=12)
                fig4.tight_layout()
                context["wind_plot"] = plot_to_base64(fig4)

            except requests.exceptions.RequestException as e:
                context["error"] = f"Could not retrieve weather data: {e}"
            except (KeyError, TypeError):
                context["error"] = "Could not parse weather data from the API."

    return render(request, "myweather/weather.html", context)