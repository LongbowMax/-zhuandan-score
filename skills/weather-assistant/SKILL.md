# Weather Assistant Skill

## Description
A skill that provides weather information including current conditions, forecasts, and weather alerts. This skill demonstrates the complete structure and functionality of an OpenClaw skill.

## Capabilities
- Get current weather conditions
- Retrieve weather forecasts
- Provide weather alerts
- Convert temperature units
- Location-based weather queries

## Configuration
Required configuration options:
- `api_key`: Weather API key for service access
- `default_location`: Default location for weather queries
- `temperature_unit`: Default temperature unit (celsius/fahrenheit)

## Tools Provided
- `get_current_weather(location)`: Fetch current weather for a location
- `get_forecast(location, days)`: Get weather forecast for upcoming days
- `get_weather_alerts(location)`: Retrieve any weather alerts
- `convert_temperature(value, from_unit, to_unit)`: Convert temperatures

## Usage Examples
```
"Current weather in Beijing?"
"Forecast for New York tomorrow?"
"Weather alerts for London?"
```

## Dependencies
- Weather API service
- Geolocation service
- Temperature conversion utilities

## Error Handling
- Network connectivity issues
- Invalid location queries
- API rate limits
- Invalid temperature units