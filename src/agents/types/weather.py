import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"


def fetch_weather(lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
    """
    Fetch weather data from OpenWeather One Call API 3.0
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("Missing OpenWeather API key. Set OPENWEATHER_API_KEY in your .env file.")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": units,
        "exclude": "minutely"  # optional: exclude parts to save bandwidth
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Weather API call failed: {e}")
