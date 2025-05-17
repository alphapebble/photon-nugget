"""
Weather tools for Solar Sage Agent.

This module implements weather-related tools that the agent can use to provide
solar-specific insights and recommendations based on weather data.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from agents.weather_integration import (
    get_weather_for_location,
    extract_solar_relevant_weather,
    estimate_irradiance,
    estimate_production_impact,
    generate_weather_insights
)

def get_production_forecast(
    lat: float, 
    lon: float, 
    system_capacity_kw: float = 5.0,
    days_ahead: int = 7
) -> Dict[str, Any]:
    """
    Get solar production forecast based on weather.
    
    Args:
        lat: Latitude
        lon: Longitude
        system_capacity_kw: System capacity in kW
        days_ahead: Number of days to forecast
        
    Returns:
        Production forecast data
    """
    # Get weather data
    weather_data = get_weather_for_location(lat, lon)
    
    # Estimate production impact
    impact = estimate_production_impact(
        weather_data, 
        system_capacity_kw=system_capacity_kw
    )
    
    # Generate insights
    insights = generate_weather_insights(impact)
    
    # Format response
    daily_forecast = []
    for day in impact["daily_forecast"][:days_ahead]:
        daily_forecast.append({
            "date": day["date"],
            "expected_kwh": round(day["expected_kwh"], 1),
            "production_factor": round(day["production_factor"] * 100, 1),
            "weather": day["weather"]
        })
    
    return {
        "current": {
            "expected_kwh": round(impact["current"]["expected_kwh"], 1),
            "production_factor": round(impact["current"]["production_factor"] * 100, 1),
            "weather": impact["current"]["weather"],
            "temperature": impact["current"]["temp"],
            "clouds": impact["current"]["clouds"],
            "irradiance": round(impact["current"]["irradiance_estimate"], 1)
        },
        "daily_forecast": daily_forecast,
        "insights": insights,
        "system_capacity_kw": system_capacity_kw
    }

def get_maintenance_recommendations(
    lat: float, 
    lon: float,
    last_cleaning_date: Optional[str] = None,
    panel_tilt: float = 30.0
) -> Dict[str, Any]:
    """
    Get maintenance recommendations based on weather.
    
    Args:
        lat: Latitude
        lon: Longitude
        last_cleaning_date: Date of last panel cleaning (YYYY-MM-DD)
        panel_tilt: Panel tilt angle in degrees
        
    Returns:
        Maintenance recommendations
    """
    # Get weather data
    weather_data = get_weather_for_location(lat, lon)
    solar_weather = extract_solar_relevant_weather(weather_data)
    
    # Calculate days since last cleaning
    days_since_cleaning = None
    if last_cleaning_date:
        try:
            last_date = datetime.strptime(last_cleaning_date, "%Y-%m-%d")
            days_since_cleaning = (datetime.now() - last_date).days
        except ValueError:
            pass
    
    # Check for upcoming rain (natural cleaning)
    rain_forecast = []
    for day in solar_weather["daily"]:
        weather = day["weather_main"].lower()
        if "rain" in weather or "shower" in weather or "drizzle" in weather:
            date = datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d")
            rain_forecast.append({
                "date": date,
                "intensity": "heavy" if "heavy" in day["weather_description"].lower() else "light"
            })
    
    # Determine if cleaning is needed
    cleaning_needed = False
    cleaning_urgency = "low"
    
    if days_since_cleaning is not None:
        if days_since_cleaning > 60:
            cleaning_needed = True
            cleaning_urgency = "high"
        elif days_since_cleaning > 30:
            cleaning_needed = True
            cleaning_urgency = "medium"
    
    # If rain is coming soon, maybe wait for natural cleaning
    if rain_forecast and rain_forecast[0]["intensity"] == "heavy" and cleaning_urgency != "high":
        cleaning_needed = False
    
    # Check for dust/pollen conditions
    current_season = get_current_season(lat)
    high_pollen = current_season == "spring" and solar_weather["current"]["humidity"] < 40
    
    # Generate recommendations
    recommendations = []
    
    if cleaning_needed:
        if rain_forecast and rain_forecast[0]["date"] <= (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"):
            recommendations.append({
                "type": "cleaning",
                "action": "Wait for rain",
                "reason": f"Rain expected on {rain_forecast[0]['date']} which will naturally clean your panels",
                "priority": "low"
            })
        else:
            recommendations.append({
                "type": "cleaning",
                "action": "Clean panels",
                "reason": f"Panels have not been cleaned for {days_since_cleaning} days" if days_since_cleaning else "Regular cleaning recommended",
                "priority": cleaning_urgency
            })
    
    # Check for extreme temperatures
    hot_days = [day for day in solar_weather["daily"][:7] if day["temp_day"] > 35]
    if hot_days:
        recommendations.append({
            "type": "monitoring",
            "action": "Monitor performance during high temperatures",
            "reason": f"High temperatures expected on {len(hot_days)} days this week, which may reduce panel efficiency",
            "priority": "medium"
        })
    
    # Check for snow if in winter
    if current_season == "winter" and any("snow" in day["weather_description"].lower() for day in solar_weather["daily"][:3]):
        if panel_tilt < 35:
            recommendations.append({
                "type": "snow_removal",
                "action": "Plan for snow removal",
                "reason": "Snow expected and your panel tilt angle is too low for natural snow shedding",
                "priority": "high"
            })
    
    return {
        "recommendations": recommendations,
        "days_since_cleaning": days_since_cleaning,
        "rain_forecast": rain_forecast,
        "current_season": current_season
    }

def get_optimal_production_times(
    lat: float, 
    lon: float, 
    days_ahead: int = 7,
    threshold_percentage: float = 70.0
) -> Dict[str, Any]:
    """
    Identify optimal times for solar production or energy-intensive activities.
    
    Args:
        lat: Latitude
        lon: Longitude
        days_ahead: Number of days to analyze
        threshold_percentage: Production threshold percentage to consider "optimal"
        
    Returns:
        Optimal production times
    """
    # Get weather data and production impact
    weather_data = get_weather_for_location(lat, lon)
    impact = estimate_production_impact(weather_data)
    
    # Find best production days
    daily_forecast = impact["daily_forecast"][:days_ahead]
    
    # Sort days by production factor
    sorted_days = sorted(
        daily_forecast, 
        key=lambda x: x["production_factor"], 
        reverse=True
    )
    
    # Find days above threshold
    optimal_days = [
        {
            "date": day["date"],
            "expected_kwh": round(day["expected_kwh"], 1),
            "production_factor": round(day["production_factor"] * 100, 1),
            "weather": day["weather"]
        }
        for day in sorted_days
        if day["production_factor"] * 100 >= threshold_percentage
    ]
    
    # Find best day of the week
    days_of_week = {}
    for day in daily_forecast:
        date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        if day_name not in days_of_week:
            days_of_week[day_name] = []
        days_of_week[day_name].append(day["production_factor"])
    
    avg_by_day = {
        day: sum(factors) / len(factors) * 100
        for day, factors in days_of_week.items()
    }
    
    best_day_of_week = max(avg_by_day.items(), key=lambda x: x[1])
    
    return {
        "optimal_days": optimal_days,
        "best_day_of_week": {
            "day": best_day_of_week[0],
            "avg_production_factor": round(best_day_of_week[1], 1)
        },
        "threshold_percentage": threshold_percentage,
        "days_analyzed": days_ahead
    }

def analyze_weather_impact(
    lat: float, 
    lon: float,
    system_capacity_kw: float = 5.0,
    expected_monthly_kwh: Optional[float] = None
) -> Dict[str, Any]:
    """
    Analyze weather impact on solar production compared to expectations.
    
    Args:
        lat: Latitude
        lon: Longitude
        system_capacity_kw: System capacity in kW
        expected_monthly_kwh: Expected monthly production in kWh
        
    Returns:
        Weather impact analysis
    """
    # Get weather data
    weather_data = get_weather_for_location(lat, lon)
    impact = estimate_production_impact(weather_data, system_capacity_kw)
    
    # Calculate expected production for next 30 days
    next_30_days = impact["daily_forecast"][:30]
    total_expected_kwh = sum(day["expected_kwh"] for day in next_30_days)
    avg_daily_expected_kwh = total_expected_kwh / len(next_30_days)
    
    # Compare with expected monthly production if provided
    comparison = None
    if expected_monthly_kwh:
        weather_impact_percentage = (total_expected_kwh / expected_monthly_kwh) * 100
        comparison = {
            "expected_monthly_kwh": expected_monthly_kwh,
            "weather_adjusted_monthly_kwh": round(total_expected_kwh, 1),
            "weather_impact_percentage": round(weather_impact_percentage, 1)
        }
    
    # Identify significant weather events
    significant_events = []
    
    for day in next_30_days:
        if day["production_factor"] < 0.3:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            significant_events.append({
                "date": day["date"],
                "day": date_obj.strftime("%A"),
                "weather": day["weather"],
                "production_factor": round(day["production_factor"] * 100, 1),
                "impact": "severe"
            })
        elif day["production_factor"] < 0.5:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            significant_events.append({
                "date": day["date"],
                "day": date_obj.strftime("%A"),
                "weather": day["weather"],
                "production_factor": round(day["production_factor"] * 100, 1),
                "impact": "moderate"
            })
    
    return {
        "total_expected_kwh_30days": round(total_expected_kwh, 1),
        "avg_daily_expected_kwh": round(avg_daily_expected_kwh, 1),
        "comparison_to_expected": comparison,
        "significant_weather_events": significant_events,
        "system_capacity_kw": system_capacity_kw
    }

def get_current_season(lat: float) -> str:
    """
    Get the current season based on latitude and date.
    
    Args:
        lat: Latitude
        
    Returns:
        Current season name
    """
    now = datetime.now()
    month = now.month
    
    # Northern hemisphere
    if lat >= 0:
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "fall"
        else:
            return "winter"
    # Southern hemisphere
    else:
        if 3 <= month <= 5:
            return "fall"
        elif 6 <= month <= 8:
            return "winter"
        elif 9 <= month <= 11:
            return "spring"
        else:
            return "summer"
