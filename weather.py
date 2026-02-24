"""
Weather utility for Kisan Sahayak
Uses OpenWeatherMap free API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(location: str) -> dict | None:
    """
    Get current weather for a location.
    
    Args:
        location: City name (e.g., "Hyderabad", "Delhi")
    
    Returns:
        Weather data dict or None if unavailable
    """
    if not WEATHER_API_KEY:
        # Return mock data when no API key
        return {
            "temp": 28,
            "humidity": 65,
            "wind": 12,
            "condition": "Partly Cloudy",
            "description": "Moderate humidity, suitable for farming activities",
            "city": location
        }
    
    try:
        params = {
            "q": f"{location},IN",
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temp": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "wind": round(data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"].title(),
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", 10000) / 1000,
            "city": data["name"],
            "country": data["sys"]["country"]
        }
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Invalid Weather API key")
        elif response.status_code == 404:
            print(f"Location '{location}' not found")
        return None
    except Exception as e:
        print(f"Weather error: {e}")
        return None


def get_farming_advisory(weather_data: dict) -> str:
    """Generate basic farming advisory from weather data without AI."""
    if not weather_data:
        return "Weather data unavailable. Check local forecasts."
    
    advisory = []
    temp = weather_data.get("temp", 25)
    humidity = weather_data.get("humidity", 60)
    wind = weather_data.get("wind", 10)
    condition = weather_data.get("condition", "Clear")
    
    # Temperature advisory
    if temp > 38:
        advisory.append("🌡️ High temperature alert! Irrigate crops in early morning or evening to prevent heat stress.")
    elif temp < 10:
        advisory.append("❄️ Cold weather! Protect frost-sensitive crops with mulching or poly covers.")
    else:
        advisory.append(f"🌡️ Temperature ({temp}°C) is suitable for most crops.")
    
    # Humidity advisory
    if humidity > 80:
        advisory.append("💧 High humidity - High risk of fungal diseases. Apply preventive fungicide spray.")
    elif humidity < 30:
        advisory.append("🏜️ Low humidity - Increase irrigation frequency to prevent moisture stress.")
    
    # Wind advisory
    if wind > 30:
        advisory.append("💨 Strong winds - Avoid spraying. Stake tall crops to prevent lodging.")
    elif wind > 15:
        advisory.append("💨 Moderate winds - Spray only if wind is below 10 km/h.")
    else:
        advisory.append("🌬️ Wind speed is suitable for pesticide/fertilizer spraying.")
    
    # Condition-based advisory
    if "Rain" in condition:
        advisory.append("🌧️ Rainy weather - Avoid spraying. Ensure proper field drainage.")
    elif "Clear" in condition or "Sunny" in condition:
        advisory.append("☀️ Clear weather - Good for harvesting, threshing and field operations.")
    
    return "\n".join(advisory)
