"""
Weather Agent - Fetches Real Weather Data

Uses OpenWeatherMap API to get current weather conditions for outfit recommendations.
"""

import requests
from typing import Dict, Any, Optional


class WeatherFetcher:
    """
    Fetches weather data from OpenWeatherMap API.

    This is the data source for weather-based outfit recommendations.
    """

    def __init__(self, api_key: str):
        """
        Initialize the weather fetcher.

        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fetch current weather for a city.

        Args:
            city: City name (e.g., "Manila", "Tokyo", "New York")
            units: "metric" for Celsius, "imperial" for Fahrenheit

        Returns:
            Dictionary with weather data or error information

        Example:
            >>> fetcher = WeatherFetcher(api_key)
            >>> weather = fetcher.get_weather("Manila")
            >>> print(weather['temperature'])
            28.5
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                weather_info = {
                    'success': True,
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'conditions': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'wind_direction': data['wind']['deg'],
                    'units': 'C' if units == 'metric' else 'F'
                }

                return weather_info

            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f"City '{city}' not found"
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': "Invalid API key"
                }
            else:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}"
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': "Request timed out"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }


def format_weather_message(weather_data: Dict[str, Any]) -> str:
    """
    Format weather data into a readable message.

    Args:
        weather_data: Dictionary with weather information

    Returns:
        Formatted string describing the weather
    """
    if not weather_data['success']:
        return f"Error: {weather_data['error']}"

    message = f"""
Location: {weather_data['city']}, {weather_data['country']}
Temperature: {weather_data['temperature']}°{weather_data['units']}
Feels Like: {weather_data['feels_like']}°{weather_data['units']}
Conditions: {weather_data['conditions']} ({weather_data['description']})
Humidity: {weather_data['humidity']}%
Wind: {weather_data['wind_speed']} m/s, {weather_data['wind_direction']}°
"""
    return message.strip()
