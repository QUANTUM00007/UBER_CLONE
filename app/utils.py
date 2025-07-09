import requests
import os
from urllib.parse import quote_plus

def get_distance_km(pickup, drop):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return 5  # fallback if no key

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={quote_plus(pickup)}&destination={quote_plus(drop)}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if data['status'] != 'OK':
        return 5  # fallback

    # Get distance in meters and convert to km
    meters = data['routes'][0]['legs'][0]['distance']['value']
    return round(meters / 1000, 2)
