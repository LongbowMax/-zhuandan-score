# Weather Assistant Usage Guide

## Overview
The Weather Assistant skill provides weather information including current conditions, forecasts, and alerts. This guide explains how to properly configure and use the skill.

## Initial Setup

### 1. Configuration
Before using the skill, you need to configure it with your weather API credentials:

1. Sign up for a weather API service (e.g., OpenWeatherMap, WeatherAPI)
2. Obtain your API key
3. Edit the `config.json` file to include your API key:
   ```json
   {
     "api_key": "your-api-key-here",
     "default_location": "Beijing",
     "temperature_unit": "celsius",
     "forecast_days": 7
   }
   ```

### 2. Required Parameters
- `api_key`: Your weather service API key (required)
- `default_location`: Location to use when none is specified (default: "Beijing")
- `temperature_unit`: Default unit for temperature display ("celsius" or "fahrenheit")

## Available Functions

### Get Current Weather
Retrieves current weather conditions for a specified location.

**Usage:**
- "What's the weather like in [location]?"
- "Current weather in [location]"
- "Show me today's weather for [location]"

**Parameters:**
- `location` (required): City name, coordinates, or other location identifier

### Get Forecast
Provides weather forecast for upcoming days.

**Usage:**
- "Forecast for [location] for [number] days"
- "Weather prediction for [location]"
- "Show me the next [number] days forecast for [location]"

**Parameters:**
- `location` (required): City name, coordinates, or other location identifier
- `days` (optional): Number of days to forecast (1-14, default: 7)

### Get Weather Alerts
Retrieves any active weather alerts for a location.

**Usage:**
- "Are there weather alerts for [location]?"
- "Weather warnings for [location]"
- "Any severe weather alerts in [location]?"

**Parameters:**
- `location` (required): City name, coordinates, or other location identifier

### Convert Temperature
Converts temperature between Celsius and Fahrenheit.

**Usage:**
- "Convert [number] degrees [unit] to [unit]"
- "What's [number]°C in Fahrenheit?"
- "[number] degrees Fahrenheit equals how many degrees Celsius?"

**Parameters:**
- `value` (required): The temperature value to convert
- `from_unit` (required): The unit to convert from ("celsius" or "fahrenheit")
- `to_unit` (required): The unit to convert to ("celsius" or "fahrenheit")

## Example Commands

### Basic Weather Queries
```
"What's the current weather in New York?"
"Show me the weather for London"
"How hot is it in Tokyo today?"
```

### Forecast Requests
```
"Give me a 5-day forecast for Paris"
"Weather prediction for Berlin next week"
"Show me the next 3 days weather for Sydney"
```

### Alert Checks
```
"Are there any weather warnings for Miami?"
"Check for weather alerts in Chicago"
"Any severe weather alerts in Denver?"
```

### Temperature Conversions
```
"Convert 25°C to Fahrenheit"
"What's 77°F in Celsius?"
"Change 32°F to Celsius"
```

## Troubleshooting

### Common Issues
- **Missing API Key**: Ensure your `config.json` includes a valid weather API key
- **Invalid Location**: Verify location spelling and formatting
- **API Limit Exceeded**: Check your weather service account for usage limits
- **Network Errors**: Confirm internet connectivity and API endpoint accessibility

### Error Messages
- `"No API key provided"`: Add your API key to the configuration
- `"Invalid location"`: Check the location format and spelling
- `"Service unavailable"`: The weather API may be temporarily down

## Best Practices

1. **Secure Your API Key**: Never share your API key publicly
2. **Set Appropriate Defaults**: Configure sensible default values in config.json
3. **Handle Rate Limits**: Be aware of API call limitations
4. **Validate Inputs**: Always specify locations clearly in requests
5. **Monitor Usage**: Track API usage to avoid exceeding limits

## Integration Tips

- Combine with calendar skills to get weather for planned events
- Link with travel planning tools for destination weather
- Connect with home automation for climate control adjustments