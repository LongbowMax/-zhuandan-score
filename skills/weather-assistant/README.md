# Weather Assistant Skill

This is a sample skill demonstrating the complete structure and creation process for OpenClaw skills. The Weather Assistant provides weather-related functionality as an example implementation.

## Purpose

This skill serves as both a functional weather service and an educational example showing:

1. How to structure a skill directory
2. How to define skill capabilities
3. How to implement skill functionality
4. How to configure tools and APIs
5. How to handle errors and edge cases

## Files Structure

```
weather-assistant/
├── SKILL.md          # Skill description and documentation
├── README.md         # This file
├── config.json       # Configuration options
├── index.js          # Main skill implementation
├── tools.json        # Tool definitions for AI interaction
└── package.json      # Dependencies and metadata
```

## Setup Instructions

1. Obtain a weather API key from a service like OpenWeatherMap or WeatherAPI
2. Update the `config.json` file with your API key
3. Set your default location and preferred temperature unit
4. Install any required dependencies if specified in package.json

## Usage

Once configured, you can use commands like:
- "What's the weather in Beijing?"
- "Show me the forecast for London"
- "Are there any weather alerts for Tokyo?"

## Development Notes

This example skill includes:
- Asynchronous API calls simulation
- Error handling patterns
- Configuration management
- Tool definition for AI consumption
- Sample responses for testing

## Customization

You can modify this skill to:
- Integrate with a real weather API
- Add additional weather data points
- Include weather visualization
- Add location geocoding functionality

## Testing

To test the skill functionality:
1. Ensure all configuration values are set
2. Run the skill in a development environment
3. Try various weather queries to verify responses