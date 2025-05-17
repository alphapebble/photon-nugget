"""
Unit tests for the Weather Integration module.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root and src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from agents.integrations.weather import (
    get_weather_for_location,
    extract_solar_relevant_weather,
    estimate_irradiance,
    estimate_production_impact,
    generate_weather_insights,
    get_weather_context_for_rag
)

class TestWeatherIntegration(unittest.TestCase):
    """Test cases for the Weather Integration module."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample weather data for testing
        self.sample_weather_data = {
            "current": {
                "dt": int(datetime.now().timestamp()),
                "temp": 25.5,
                "humidity": 65,
                "clouds": 30,
                "uvi": 6.2,
                "wind_speed": 3.5,
                "weather": [
                    {
                        "main": "Clouds",
                        "description": "scattered clouds"
                    }
                ]
            },
            "daily": [
                {
                    "dt": int((datetime.now().timestamp() + 86400 * i)),
                    "temp": {
                        "day": 26.5 - i,
                        "min": 20.0,
                        "max": 30.0
                    },
                    "humidity": 60 + i,
                    "clouds": 25 + i * 5,
                    "uvi": 6.0 - i * 0.5,
                    "wind_speed": 3.0 + i * 0.2,
                    "pop": 0.1 * i,  # Probability of precipitation
                    "weather": [
                        {
                            "main": "Clouds" if i < 3 else "Rain",
                            "description": "scattered clouds" if i < 3 else "light rain"
                        }
                    ]
                } for i in range(7)
            ]
        }

    @patch('agents.integrations.weather.fetch_weather')
    def test_get_weather_for_location(self, mock_fetch_weather):
        """Test that get_weather_for_location calls fetch_weather with correct parameters."""
        # Set up the mock
        mock_fetch_weather.return_value = self.sample_weather_data

        # Call the function
        result = get_weather_for_location(37.7749, -122.4194)

        # Check that fetch_weather was called with the correct parameters
        mock_fetch_weather.assert_called_once_with(37.7749, -122.4194, "metric")

        # Check that the result matches the mock data
        self.assertEqual(result, self.sample_weather_data)

    def test_extract_solar_relevant_weather(self):
        """Test that extract_solar_relevant_weather extracts the correct data."""
        # Call the function
        result = extract_solar_relevant_weather(self.sample_weather_data)

        # Check that the result has the expected structure
        self.assertIn("current", result)
        self.assertIn("daily", result)

        # Check current weather data
        current = result["current"]
        self.assertEqual(current["clouds"], 30)
        self.assertEqual(current["uvi"], 6.2)
        self.assertEqual(current["temp"], 25.5)
        self.assertEqual(current["humidity"], 65)
        self.assertEqual(current["wind_speed"], 3.5)
        self.assertEqual(current["weather_main"], "Clouds")
        self.assertEqual(current["weather_description"], "scattered clouds")

        # Check daily forecast data
        daily = result["daily"]
        self.assertEqual(len(daily), 7)
        self.assertEqual(daily[0]["clouds"], 25)
        self.assertEqual(daily[0]["uvi"], 6.0)
        self.assertEqual(daily[0]["temp_day"], 26.5)
        self.assertEqual(daily[0]["humidity"], 60)
        self.assertEqual(daily[0]["wind_speed"], 3.0)
        self.assertEqual(daily[0]["weather_main"], "Clouds")
        self.assertEqual(daily[0]["weather_description"], "scattered clouds")
        self.assertEqual(daily[0]["pop"], 0.0)

    def test_estimate_irradiance(self):
        """Test that estimate_irradiance calculates correct values."""
        # Test with different cloud cover and UV index values
        test_cases = [
            {"cloud_cover": 0, "uvi": 10, "expected_min": 900},  # Clear sky, high UV
            {"cloud_cover": 100, "uvi": 10, "expected_max": 100},  # Complete cloud cover
            {"cloud_cover": 50, "uvi": 5, "expected_range": (250, 350)}  # Partial cloud cover
        ]

        for case in test_cases:
            irradiance = estimate_irradiance(case["cloud_cover"], case["uvi"])

            if "expected_min" in case:
                self.assertGreaterEqual(irradiance, case["expected_min"])

            if "expected_max" in case:
                self.assertLessEqual(irradiance, case["expected_max"])

            if "expected_range" in case:
                self.assertTrue(
                    case["expected_range"][0] <= irradiance <= case["expected_range"][1],
                    f"Irradiance {irradiance} not in expected range {case['expected_range']}"
                )

    @patch('agents.integrations.weather.estimate_irradiance')
    def test_estimate_production_impact(self, mock_estimate_irradiance):
        """Test that estimate_production_impact calculates correct values."""
        # Set up the mock
        mock_estimate_irradiance.return_value = 700  # 70% of standard test conditions

        # Call the function
        result = estimate_production_impact(self.sample_weather_data, system_capacity_kw=5.0)

        # Check that the result has the expected structure
        self.assertIn("current", result)
        self.assertIn("daily_forecast", result)

        # Check current production impact
        current = result["current"]
        self.assertIn("production_factor", current)
        self.assertIn("expected_kwh", current)
        self.assertIn("weather", current)
        self.assertIn("temp", current)
        self.assertIn("clouds", current)
        self.assertIn("irradiance_estimate", current)

        # Check daily forecast
        daily_forecast = result["daily_forecast"]
        self.assertEqual(len(daily_forecast), 7)
        for day in daily_forecast:
            self.assertIn("date", day)
            self.assertIn("expected_kwh", day)
            self.assertIn("production_factor", day)
            self.assertIn("weather", day)
            self.assertIn("temp", day)
            self.assertIn("clouds", day)
            self.assertIn("uvi", day)

    def test_generate_weather_insights(self):
        """Test that generate_weather_insights generates correct insights."""
        # Create a sample weather impact
        weather_impact = {
            "current": {
                "production_factor": 0.8,
                "expected_kwh": 4.0,
                "weather": "scattered clouds",
                "temp": 25.5,
                "clouds": 30,
                "irradiance_estimate": 700
            },
            "daily_forecast": [
                {
                    "date": "2023-06-01",
                    "expected_kwh": 20.0,
                    "production_factor": 0.8,
                    "weather": "scattered clouds",
                    "temp": 26.5,
                    "clouds": 25,
                    "uvi": 6.0
                },
                {
                    "date": "2023-06-02",
                    "expected_kwh": 19.0,
                    "production_factor": 0.76,
                    "weather": "scattered clouds",
                    "temp": 25.5,
                    "clouds": 30,
                    "uvi": 5.5
                },
                {
                    "date": "2023-06-03",
                    "expected_kwh": 18.0,
                    "production_factor": 0.72,
                    "weather": "scattered clouds",
                    "temp": 24.5,
                    "clouds": 35,
                    "uvi": 5.0
                },
                {
                    "date": "2023-06-04",
                    "expected_kwh": 15.0,
                    "production_factor": 0.6,
                    "weather": "light rain",
                    "temp": 23.5,
                    "clouds": 40,
                    "uvi": 4.5
                },
                {
                    "date": "2023-06-05",
                    "expected_kwh": 12.5,
                    "production_factor": 0.5,
                    "weather": "light rain",
                    "temp": 22.5,
                    "clouds": 45,
                    "uvi": 4.0
                },
                {
                    "date": "2023-06-06",
                    "expected_kwh": 10.0,
                    "production_factor": 0.4,
                    "weather": "light rain",
                    "temp": 21.5,
                    "clouds": 50,
                    "uvi": 3.5
                },
                {
                    "date": "2023-06-07",
                    "expected_kwh": 7.5,
                    "production_factor": 0.3,
                    "weather": "light rain",
                    "temp": 20.5,
                    "clouds": 55,
                    "uvi": 3.0
                }
            ]
        }

        # Call the function
        insights = generate_weather_insights(weather_impact)

        # Check that the result has the expected structure
        self.assertIn("current_conditions", insights)
        self.assertIn("weekly_potential", insights)
        self.assertIn("best_production_day", insights)
        self.assertIn("maintenance_insights", insights)

        # Check that the insights are non-empty strings
        self.assertTrue(len(insights["current_conditions"]) > 0)
        self.assertTrue(len(insights["weekly_potential"]) > 0)
        self.assertTrue(len(insights["best_production_day"]) > 0)

    @patch('agents.integrations.weather.get_weather_for_location')
    @patch('agents.integrations.weather.estimate_production_impact')
    @patch('agents.integrations.weather.generate_weather_insights')
    def test_get_weather_context_for_rag(self, mock_insights, mock_impact, mock_weather):
        """Test that get_weather_context_for_rag generates correct context."""
        # Set up the mocks
        mock_weather.return_value = self.sample_weather_data
        mock_impact.return_value = {
            "current": {
                "production_factor": 0.8,
                "expected_kwh": 4.0,
                "weather": "scattered clouds",
                "temp": 25.5,
                "clouds": 30,
                "irradiance_estimate": 700
            },
            "daily_forecast": []
        }
        mock_insights.return_value = {
            "current_conditions": "Weather conditions are favorable for good energy production.",
            "weekly_potential": "The 7-day forecast shows moderate solar potential.",
            "best_production_day": "The best day for production in the next week is 2023-06-01.",
            "maintenance_insights": []
        }

        # Call the function
        context = get_weather_context_for_rag(37.7749, -122.4194)

        # Check that the context is a non-empty string
        self.assertIsInstance(context, str)
        self.assertTrue(len(context) > 0)

        # Check that the context contains expected information
        self.assertIn("CURRENT WEATHER CONTEXT", context)
        self.assertIn("7-DAY FORECAST SUMMARY", context)

    @patch('agents.integrations.weather.get_weather_for_location')
    def test_get_weather_context_for_rag_error_handling(self, mock_weather):
        """Test that get_weather_context_for_rag handles errors gracefully."""
        # Set up the mock to raise an exception
        mock_weather.side_effect = Exception("API error")

        # Call the function
        context = get_weather_context_for_rag(37.7749, -122.4194)

        # Check that the context indicates an error
        self.assertIn("Weather data unavailable", context)
        self.assertIn("API error", context)


if __name__ == '__main__':
    unittest.main()
