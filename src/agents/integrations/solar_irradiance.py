"""
Solar irradiance data integration module.

This module provides integration with solar irradiance data sources to retrieve
current and forecasted solar irradiance data for specified locations.
"""
import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
import json
import os
import numpy as np
from core.config import get_config
from core.logging import get_logger
from core.semantic_metric_layer import get_constant, evaluate_formula

logger = get_logger(__name__)

class SolarIrradianceClient:
    """Base class for solar irradiance data clients."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the solar irradiance client."""
        self.api_key = api_key or get_config("solar_irradiance_api_key", "")
        if not self.api_key:
            logger.warning("No solar irradiance API key provided. Data will be calculated using models.")

    def get_current_irradiance(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current solar irradiance for a location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Current solar irradiance data
        """
        raise NotImplementedError("Subclasses must implement this method")

    def get_forecast(self, lat: float, lon: float, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get solar irradiance forecast for a location.

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast

        Returns:
            Solar irradiance forecast for the specified number of days
        """
        raise NotImplementedError("Subclasses must implement this method")


class SolarIrradianceModel:
    """Model-based solar irradiance calculator."""

    def __init__(self):
        """Initialize the solar irradiance model."""
        pass

    def calculate_solar_position(
        self, lat: float, lon: float, date_time: datetime.datetime
    ) -> Tuple[float, float]:
        """
        Calculate solar position (elevation and azimuth) for a given location and time.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            date_time: Date and time

        Returns:
            Tuple of (elevation, azimuth) in degrees
        """
        # Convert to radians
        lat_rad = np.radians(lat)

        # Day of year
        day_of_year = date_time.timetuple().tm_yday

        # Calculate declination angle using formula from YAML
        params = {
            'day_of_year': day_of_year,
            'radians': np.radians,
            'sin': np.sin
        }
        declination = evaluate_formula('solar_irradiance.declination_angle', params)
        declination_rad = np.radians(declination)

        # Calculate hour angle using formula from YAML
        hour = date_time.hour + date_time.minute / 60 + date_time.second / 3600
        params = {'hour': hour}
        hour_angle = evaluate_formula('solar_irradiance.hour_angle', params)
        hour_angle_rad = np.radians(hour_angle)

        # Calculate elevation using formula from YAML
        params = {
            'lat_rad': lat_rad,
            'declination_rad': declination_rad,
            'hour_angle_rad': hour_angle_rad,
            'sin': np.sin,
            'cos': np.cos,
            'asin': np.arcsin
        }
        elevation_rad = evaluate_formula('solar_irradiance.solar_elevation', params)
        elevation = np.degrees(elevation_rad)

        # Calculate azimuth using formula from YAML
        params = {
            'lat_rad': lat_rad,
            'declination_rad': declination_rad,
            'hour_angle_rad': hour_angle_rad,
            'elevation_rad': elevation_rad,
            'sin': np.sin,
            'cos': np.cos,
            'atan2': np.arctan2
        }
        azimuth = np.degrees(evaluate_formula('solar_irradiance.solar_azimuth', params))

        # Adjust azimuth to be 0-360
        if azimuth < 0:
            azimuth += 360

        return elevation, azimuth

    def calculate_clear_sky_irradiance(
        self, elevation: float, altitude: float = 0
    ) -> float:
        """
        Calculate clear sky irradiance based on solar elevation.

        Args:
            elevation: Solar elevation in degrees
            altitude: Location altitude in meters

        Returns:
            Clear sky irradiance in W/m²
        """
        if elevation <= 0:
            return 0  # No sunlight when sun is below horizon

        # Get constants from YAML
        solar_constant = get_constant('solar_irradiance.solar_constant')
        altitude_scale_height = get_constant('solar_irradiance.altitude_scale_height')
        atmospheric_transmittance = get_constant('solar_irradiance.atmospheric_transmittance')

        # Calculate air mass using formula from YAML
        params = {
            'elevation_rad': np.radians(elevation),
            'altitude': altitude,
            'altitude_scale_height': altitude_scale_height,
            'sin': np.sin,
            'exp': np.exp
        }
        air_mass = evaluate_formula('solar_irradiance.air_mass', params)

        # Calculate clear sky irradiance using formula from YAML
        params = {
            'solar_constant': solar_constant,
            'transmittance': atmospheric_transmittance,
            'air_mass': air_mass,
            'elevation_rad': np.radians(elevation),
            'sin': np.sin
        }
        irradiance = evaluate_formula('solar_irradiance.clear_sky_irradiance', params)

        return max(0, irradiance)

    def adjust_for_cloud_cover(self, clear_sky_irradiance: float, cloud_cover: float) -> float:
        """
        Adjust irradiance for cloud cover.

        Args:
            clear_sky_irradiance: Clear sky irradiance in W/m²
            cloud_cover: Cloud cover percentage (0-100)

        Returns:
            Adjusted irradiance in W/m²
        """
        # Use cloud impact formula from YAML
        params = {'cloud_cover': cloud_cover}
        cloud_factor = evaluate_formula('solar_irradiance.cloud_impact', params)
        return clear_sky_irradiance * cloud_factor

    def get_current_irradiance(
        self, lat: float, lon: float, cloud_cover: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate current solar irradiance for a location.

        Args:
            lat: Latitude
            lon: Longitude
            cloud_cover: Cloud cover percentage (0-100)

        Returns:
            Current solar irradiance data
        """
        now = datetime.datetime.now()
        elevation, azimuth = self.calculate_solar_position(lat, lon, now)
        clear_sky_irradiance = self.calculate_clear_sky_irradiance(elevation)
        actual_irradiance = self.adjust_for_cloud_cover(clear_sky_irradiance, cloud_cover)

        return {
            "timestamp": now.isoformat(),
            "elevation": elevation,
            "azimuth": azimuth,
            "clear_sky_irradiance": clear_sky_irradiance,
            "actual_irradiance": actual_irradiance,
            "cloud_cover": cloud_cover
        }

    def get_daily_profile(
        self, lat: float, lon: float, date: datetime.date, cloud_cover: float = 0
    ) -> List[Dict[str, Any]]:
        """
        Calculate solar irradiance profile for a day.

        Args:
            lat: Latitude
            lon: Longitude
            date: Date
            cloud_cover: Cloud cover percentage (0-100)

        Returns:
            Hourly solar irradiance data for the day
        """
        profile = []

        for hour in range(24):
            for minute in [0, 30]:  # Half-hour intervals
                time = datetime.datetime.combine(date, datetime.time(hour, minute))
                elevation, azimuth = self.calculate_solar_position(lat, lon, time)
                clear_sky_irradiance = self.calculate_clear_sky_irradiance(elevation)
                actual_irradiance = self.adjust_for_cloud_cover(clear_sky_irradiance, cloud_cover)

                profile.append({
                    "timestamp": time.isoformat(),
                    "elevation": elevation,
                    "azimuth": azimuth,
                    "clear_sky_irradiance": clear_sky_irradiance,
                    "actual_irradiance": actual_irradiance,
                    "cloud_cover": cloud_cover
                })

        return profile

    def get_forecast(
        self, lat: float, lon: float, days: int = 7, cloud_cover_forecast: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate solar irradiance forecast for a location.

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast
            cloud_cover_forecast: List of daily cloud cover percentages

        Returns:
            Daily solar irradiance forecast for the specified number of days
        """
        forecast = []
        today = datetime.datetime.now().date()

        # Default cloud cover if not provided
        if cloud_cover_forecast is None:
            cloud_cover_forecast = [30] * days

        # Ensure we have enough cloud cover values
        while len(cloud_cover_forecast) < days:
            cloud_cover_forecast.append(30)  # Default value

        for i in range(days):
            date = today + datetime.timedelta(days=i)
            cloud_cover = cloud_cover_forecast[i]

            # Calculate daily totals
            daily_profile = self.get_daily_profile(lat, lon, date, cloud_cover)

            # Calculate daily statistics
            irradiance_values = [hour["actual_irradiance"] for hour in daily_profile]
            max_irradiance = max(irradiance_values)
            avg_irradiance = sum(irradiance_values) / len(irradiance_values)
            daylight_hours = sum(1 for hour in daily_profile if hour["elevation"] > 0) / 2  # Half-hour intervals

            # Calculate total energy
            daily_energy = sum(hour["actual_irradiance"] for hour in daily_profile) / 2  # kWh/m²/day (half-hour intervals)
            daily_energy /= 1000  # Convert from W to kW

            forecast.append({
                "date": date.isoformat(),
                "max_irradiance": max_irradiance,
                "avg_irradiance": avg_irradiance,
                "daylight_hours": daylight_hours,
                "daily_energy": daily_energy,
                "cloud_cover": cloud_cover
            })

        return forecast


# Factory function to get the appropriate solar irradiance client
def get_solar_irradiance_client() -> SolarIrradianceModel:
    """
    Get the solar irradiance client or model.

    Returns:
        Solar irradiance client or model
    """
    # For now, we only have the model-based implementation
    return SolarIrradianceModel()


# Convenience functions
def get_current_irradiance(lat: float, lon: float, cloud_cover: float = 0) -> Dict[str, Any]:
    """
    Get current solar irradiance for a location.

    Args:
        lat: Latitude
        lon: Longitude
        cloud_cover: Cloud cover percentage (0-100)

    Returns:
        Current solar irradiance data
    """
    client = get_solar_irradiance_client()
    return client.get_current_irradiance(lat, lon, cloud_cover)


def get_irradiance_forecast(
    lat: float, lon: float, days: int = 7, cloud_cover_forecast: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Get solar irradiance forecast for a location.

    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days to forecast
        cloud_cover_forecast: List of daily cloud cover percentages

    Returns:
        Solar irradiance forecast for the specified number of days
    """
    client = get_solar_irradiance_client()
    return client.get_forecast(lat, lon, days, cloud_cover_forecast)
