import geoip2.database

from django_project.settings.base import GEOIP_PATH

def get_location_and_temperature(ip_address):
    reader = geoip2.database.Reader(GEOIP_PATH)
    try:
        response = reader.city(ip_address)
        city = response.city.name
        # For simplicity, return a dummy temperature.
        # Implement `get_temperature` to fetch real temperature data if needed.
        temperature = 11  # Example temperature
        return city, temperature
    except Exception as e:
        return None, None
