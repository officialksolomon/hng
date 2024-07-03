import geoip2.database
import requests


from django_project.settings.base import GEOIP_PATH, OPENWEATHERMAP_API_KEY


def get_location_and_temperature(ip):
    try:
        # Open the GeoIP2 database
        reader = geoip2.database.Reader(GEOIP_PATH)
        response = reader.city(ip)
        city = response.city.name
        reader.close()

        # Fetch temperature data from OpenWeatherMap API
        api_key = OPENWEATHERMAP_API_KEY
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if weather_response.status_code == 200 and "main" in weather_data:
            temperature = weather_data["main"]["temp"]
        else:
            temperature = 11

        return city, temperature
    except Exception:
        # Handle exceptions
        return None, None
