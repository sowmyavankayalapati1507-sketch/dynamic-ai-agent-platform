import os
import requests

API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(location, unit="metric"):

    # Convert user-friendly units
    if unit.lower() == "celsius":
        unit = "metric"
    elif unit.lower() == "fahrenheit":
        unit = "imperial"

    # Get latitude & longitude from location name
    geo_url = (
        f"https://api.openweathermap.org/geo/1.0/direct"
        f"?q={location}&limit=1&appid={API_KEY}"
    )

    geo_response = requests.get(geo_url).json()

    if not geo_response:
        return {
            "location": location,
            "error": "Location not found"
        }

    lat = geo_response[0]["lat"]
    lon = geo_response[0]["lon"]

    # Get weather data
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units={unit}"
    )

    weather_data = requests.get(weather_url).json()

    if "main" not in weather_data:
        return {
            "location": location,
            "error": weather_data.get("message", "Weather data unavailable")
        }

    return {
        "location": location,
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "description": weather_data["weather"][0]["description"]
    }