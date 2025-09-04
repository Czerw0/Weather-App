from django.shortcuts import render
from .utils import cities, weather_codes
import requests
from datetime import datetime, timedelta

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
            context["forecast"] = zip(
                data["hourly"]["time"],
                data["hourly"]["temperature_2m"],
                data["hourly"]["weathercode"],
                data["hourly"]["cloudcover"],
                data["hourly"]["rain"],
                data["hourly"]["precipitation_probability"],
            )
            context["weather_codes"] = weather_codes
            context["city"] = city_name
    return render(request, "myweather/weather.html", context)