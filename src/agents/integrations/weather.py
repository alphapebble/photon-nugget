"""
Weather integration module for Solar Sage.

This module provides functions to:
1. Fetch and process weather data for solar energy analysis
2. Integrate weather data with RAG system
3. Generate weather-based insights for solar energy production
4. Predict solar panel performance based on weather conditions
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dotenv import load_dotenv

from agents.types.weather import fetch_weather
from core.semantic_metric_layer import get_constant, evaluate_formula

# Load environment variables
load_dotenv()

def get_weather_for_location(lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
    """
    Get current and forecast weather data for a specific location.

    Args:
        lat: Latitude
        lon: Longitude
        units: Units (metric, imperial)

    Returns:
        Dictionary with weather data
    """
    return fetch_weather(lat, lon, units)

def extract_solar_relevant_weather(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract weather parameters relevant to solar energy production.

    Args:
        weather_data: Full weather data from API

    Returns:
        Dictionary with solar-relevant weather parameters
    """
    solar_weather = {
        "current": {
            "clouds": weather_data.get("current", {}).get("clouds", 0),
            "uvi": weather_data.get("current", {}).get("uvi", 0),
            "temp": weather_data.get("current", {}).get("temp", 0),
            "humidity": weather_data.get("current", {}).get("humidity", 0),
            "wind_speed": weather_data.get("current", {}).get("wind_speed", 0),
            "weather_main": weather_data.get("current", {}).get("weather", [{}])[0].get("main", ""),
            "weather_description": weather_data.get("current", {}).get("weather", [{}])[0].get("description", ""),
            "dt": weather_data.get("current", {}).get("dt", 0)
        },
        "daily": []
    }

    # Extract daily forecast data
    for day in weather_data.get("daily", []):
        solar_weather["daily"].append({
            "clouds": day.get("clouds", 0),
            "uvi": day.get("uvi", 0),
            "temp_day": day.get("temp", {}).get("day", 0),
            "humidity": day.get("humidity", 0),
            "wind_speed": day.get("wind_speed", 0),
            "weather_main": day.get("weather", [{}])[0].get("main", ""),
            "weather_description": day.get("weather", [{}])[0].get("description", ""),
            "dt": day.get("dt", 0),
            "pop": day.get("pop", 0)  # Probability of precipitation
        })

    return solar_weather

def estimate_irradiance(cloud_cover: float, uvi: float) -> float:
    """
    Estimate solar irradiance based on cloud cover and UV index.

    Args:
        cloud_cover: Cloud cover percentage (0-100)
        uvi: UV index

    Returns:
        Estimated irradiance in W/m²
    """
    # Use formulas from YAML
    params = {'uvi': uvi}
    clear_sky_irradiance = evaluate_formula('weather.uv_irradiance_estimate', params)

    params = {'clear_sky_irradiance': clear_sky_irradiance, 'cloud_cover': cloud_cover}
    return evaluate_formula('weather.cloud_adjusted_irradiance', params)

def estimate_production_impact(weather_data: Dict[str, Any],
                              system_capacity_kw: float = 5.0) -> Dict[str, Any]:
    """
    Estimate impact of weather on solar energy production.

    Args:
        weather_data: Weather data from API
        system_capacity_kw: Solar system capacity in kW

    Returns:
        Dictionary with production impact estimates
    """
    solar_weather = extract_solar_relevant_weather(weather_data)

    # Current conditions impact
    current = solar_weather["current"]
    current_irradiance = estimate_irradiance(current["clouds"], current["uvi"])

    # Get constants from YAML
    stc_irradiance = get_constant('solar_panel.stc.irradiance')
    stc_temperature = get_constant('solar_panel.stc.temperature')

    # Temperature impact on efficiency using formula from YAML
    params = {
        'temperature_coefficient': get_constant('solar_panel.characteristics.temperature_coefficient'),
        'temperature': current["temp"],
        'stc_temperature': stc_temperature
    }
    temp_impact = evaluate_formula('energy.temperature_impact', params)

    # Current production estimate (relative to ideal conditions)
    params = {
        'irradiance': current_irradiance,
        'stc_irradiance': stc_irradiance,
        'temperature_impact': temp_impact
    }
    current_production_factor = evaluate_formula('energy.production_factor', params)

    # Adjust for weather conditions
    if current["weather_main"] in ["Rain", "Drizzle", "Thunderstorm"]:
        current_production_factor *= get_constant('solar_panel.weather_impact.rain_factor')
    elif current["weather_main"] in ["Snow", "Sleet"]:
        current_production_factor *= get_constant('solar_panel.weather_impact.snow_factor')
    elif current["weather_main"] == "Fog":
        current_production_factor *= get_constant('solar_panel.weather_impact.fog_factor')

    # Calculate expected kWh for current hour
    current_expected_kwh = system_capacity_kw * current_production_factor

    # Daily forecast
    daily_forecast = []
    for day in solar_weather["daily"]:
        day_irradiance = estimate_irradiance(day["clouds"], day["uvi"])

        # Temperature impact on efficiency using formula from YAML
        params = {
            'temperature_coefficient': get_constant('solar_panel.characteristics.temperature_coefficient'),
            'temperature': day["temp_day"],
            'stc_temperature': stc_temperature
        }
        day_temp_impact = evaluate_formula('energy.temperature_impact', params)

        # Base production factor
        params = {
            'irradiance': day_irradiance,
            'stc_irradiance': stc_irradiance,
            'temperature_impact': day_temp_impact
        }
        day_production_factor = evaluate_formula('energy.production_factor', params)

        # Adjust for weather conditions
        weather_adjustment = 1.0
        if day["weather_main"] in ["Rain", "Drizzle", "Thunderstorm"]:
            rain_factor = get_constant('solar_panel.weather_impact.rain_factor')
            rain_impact = get_constant('solar_panel.weather_impact.precipitation_impact.rain')
            weather_adjustment = rain_factor - (rain_impact * day["pop"])
        elif day["weather_main"] in ["Snow", "Sleet"]:
            snow_factor = get_constant('solar_panel.weather_impact.snow_factor')
            snow_impact = get_constant('solar_panel.weather_impact.precipitation_impact.snow')
            weather_adjustment = snow_factor - (snow_impact * day["pop"])
        elif day["weather_main"] == "Fog":
            weather_adjustment = get_constant('solar_panel.weather_impact.fog_factor')

        day_production_factor *= weather_adjustment

        # Calculate expected kWh for the day (using peak sun hours from YAML)
        peak_sun_hours = get_constant('solar_panel.peak_sun_hours')
        day_expected_kwh = system_capacity_kw * day_production_factor * peak_sun_hours

        # Convert timestamp to date
        date = datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d")

        daily_forecast.append({
            "date": date,
            "expected_kwh": day_expected_kwh,
            "production_factor": day_production_factor,
            "weather": day["weather_description"],
            "temp": day["temp_day"],
            "clouds": day["clouds"],
            "uvi": day["uvi"]
        })

    return {
        "current": {
            "production_factor": current_production_factor,
            "expected_kwh": current_expected_kwh,
            "weather": current["weather_description"],
            "temp": current["temp"],
            "clouds": current["clouds"],
            "irradiance_estimate": current_irradiance
        },
        "daily_forecast": daily_forecast
    }

def generate_weather_insights(weather_impact: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate human-readable insights from weather impact data.

    Args:
        weather_impact: Weather impact data

    Returns:
        Dictionary with insights
    """
    current = weather_impact["current"]
    forecast = weather_impact["daily_forecast"]

    # Current conditions insight
    if current["production_factor"] < 0.3:
        current_insight = "Production is significantly reduced due to poor weather conditions."
    elif current["production_factor"] < 0.7:
        current_insight = "Production is moderately reduced due to suboptimal weather conditions."
    else:
        current_insight = "Weather conditions are favorable for good energy production."

    # Weekly potential
    avg_weekly_factor = sum(day["production_factor"] for day in forecast[:7]) / min(7, len(forecast))
    if avg_weekly_factor < 0.3:
        weekly_insight = "The 7-day forecast shows poor solar potential overall."
    elif avg_weekly_factor < 0.7:
        weekly_insight = "The 7-day forecast shows moderate solar potential."
    else:
        weekly_insight = "The 7-day forecast shows excellent solar potential."

    # Best day insight
    if forecast:
        best_day = max(forecast[:7], key=lambda x: x["production_factor"])
        best_day_insight = f"The best day for production in the next week is {best_day['date']} with expected production at {best_day['production_factor']*100:.1f}% of ideal conditions."
    else:
        best_day_insight = "No forecast data available to determine the best production day."

    # Maintenance insights
    maintenance_insights = []

    # Check for rain after dry period (panel cleaning)
    dry_days = 0
    rain_coming = False
    rain_date = ""

    for day in forecast:
        if "rain" in day["weather"].lower() or "shower" in day["weather"].lower():
            rain_coming = True
            rain_date = day["date"]
            break
        dry_days += 1

    # Get maintenance thresholds from YAML
    dry_days_threshold = get_constant('weather.maintenance.dry_days_threshold')
    high_temp_threshold = get_constant('weather.maintenance.high_temperature_threshold')

    if rain_coming and dry_days > dry_days_threshold:
        maintenance_insights.append(f"Rain expected on {rain_date} after {dry_days} dry days - this may naturally clean your panels.")

    # Check for extreme temperatures
    hot_days = [day for day in forecast[:7] if day["temp"] > high_temp_threshold]
    if hot_days:
        maintenance_insights.append(f"High temperatures expected on {len(hot_days)} days this week, which may reduce panel efficiency.")

    return {
        "current_conditions": current_insight,
        "weekly_potential": weekly_insight,
        "best_production_day": best_day_insight,
        "maintenance_insights": maintenance_insights
    }

def get_weather_forecast(lat: float, lon: float, days: int = 7) -> List[Dict[str, Any]]:
    """
    Get weather forecast for a location.

    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days to forecast

    Returns:
        Weather forecast for the specified number of days
    """
    try:
        weather_data = get_weather_for_location(lat, lon)
        solar_weather = extract_solar_relevant_weather(weather_data)

        forecast = []
        for day in solar_weather["daily"][:days]:
            # Convert timestamp to date
            date = datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d")

            forecast.append({
                "date": date,
                "temperature": day["temp_day"],
                "cloud_cover": day["clouds"],
                "weather_description": day["weather_description"],
                "uvi": day["uvi"],
                "humidity": day["humidity"],
                "wind_speed": day["wind_speed"],
                "precipitation": day["pop"] * 10  # Convert probability to mm (rough estimate)
            })

        return forecast
    except Exception as e:
        print(f"Error getting weather forecast: {e}")
        # Return mock data
        return _get_mock_weather_forecast(days)

def _get_mock_weather_forecast(days: int = 7) -> List[Dict[str, Any]]:
    """
    Get mock weather forecast when real data is unavailable.

    Args:
        days: Number of days to forecast

    Returns:
        Mock weather forecast
    """
    forecast = []
    today = datetime.now().date()

    for i in range(days):
        date = today + timedelta(days=i)

        # Create some variation in the forecast
        temp_base = 22.5 + 2 * (i % 3 - 1)
        cloud_cover = 25 + 10 * (i % 5)

        forecast.append({
            "date": date.isoformat(),
            "temperature": temp_base,
            "cloud_cover": cloud_cover,
            "weather_description": "Partly cloudy" if cloud_cover < 50 else "Cloudy",
            "uvi": 5.0 - (cloud_cover / 20),
            "humidity": 65 + (i % 3) * 5,
            "wind_speed": 3.5 + (i % 4),
            "precipitation": 0 if cloud_cover < 70 else 2.5
        })

    return forecast

def get_weather_context_for_rag(lat: float, lon: float) -> str:
    """
    Get weather context formatted for inclusion in RAG prompts.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Formatted weather context string
    """
    try:
        weather_data = get_weather_for_location(lat, lon)
        impact = estimate_production_impact(weather_data)
        insights = generate_weather_insights(impact)

        # Format as a concise context string
        context = f"""
CURRENT WEATHER CONTEXT:
- Current conditions: {weather_data['current']['weather'][0]['description']}
- Temperature: {weather_data['current']['temp']}°C
- Cloud cover: {weather_data['current']['clouds']}%
- UV Index: {weather_data['current']['uvi']}
- Expected production: {impact['current']['production_factor']*100:.1f}% of ideal conditions
- {insights['current_conditions']}

7-DAY FORECAST SUMMARY:
- {insights['weekly_potential']}
- {insights['best_production_day']}
"""

        if insights['maintenance_insights']:
            context += "MAINTENANCE NOTES:\n"
            for insight in insights['maintenance_insights']:
                context += f"- {insight}\n"

        return context
    except Exception as e:
        return f"Weather data unavailable: {str(e)}"
