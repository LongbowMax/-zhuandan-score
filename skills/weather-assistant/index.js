/**
 * Weather Assistant Skill
 * Provides weather information services
 */

class WeatherAssistant {
  constructor(config) {
    this.config = config;
    this.apiKey = config.api_key;
    this.defaultLocation = config.default_location;
    this.temperatureUnit = config.temperature_unit;
    this.forecastDays = config.forecast_days || 7;
  }

  /**
   * Get current weather for a location
   */
  async getCurrentWeather(location = null) {
    const targetLocation = location || this.defaultLocation;
    
    // Simulate API call to weather service
    console.log(`Fetching current weather for ${targetLocation}`);
    
    // In a real implementation, this would call the actual weather API
    return {
      location: targetLocation,
      timestamp: new Date().toISOString(),
      condition: this.getRandomCondition(),
      temperature: this.getRandomTemperature(),
      humidity: this.getRandomHumidity(),
      windSpeed: this.getRandomWindSpeed()
    };
  }

  /**
   * Get weather forecast for a location
   */
  async getForecast(location = null, days = null) {
    const targetLocation = location || this.defaultLocation;
    const numDays = days || this.forecastDays;
    
    console.log(`Fetching ${numDays}-day forecast for ${targetLocation}`);
    
    const forecast = [];
    for (let i = 0; i < numDays; i++) {
      forecast.push({
        day: i + 1,
        date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        condition: this.getRandomCondition(),
        highTemp: this.getRandomTemperature(),
        lowTemp: this.getRandomTemperature(true),
        precipitation: Math.floor(Math.random() * 100)
      });
    }
    
    return {
      location: targetLocation,
      forecast: forecast
    };
  }

  /**
   * Get weather alerts for a location
   */
  async getWeatherAlerts(location = null) {
    const targetLocation = location || this.defaultLocation;
    
    // Simulate checking for weather alerts
    const hasAlert = Math.random() > 0.7; // 30% chance of alert
    
    if (hasAlert) {
      return {
        location: targetLocation,
        alerts: [{
          type: "Severe Weather Warning",
          severity: "Moderate",
          description: "Possible thunderstorms expected in the afternoon",
          startTime: new Date().toISOString(),
          endTime: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString()
        }]
      };
    } else {
      return {
        location: targetLocation,
        alerts: []
      };
    }
  }

  /**
   * Convert temperature between units
   */
  convertTemperature(value, fromUnit, toUnit) {
    if (fromUnit.toLowerCase() === toUnit.toLowerCase()) {
      return value;
    }
    
    if (fromUnit.toLowerCase() === 'celsius' && toUnit.toLowerCase() === 'fahrenheit') {
      return (value * 9/5) + 32;
    } else if (fromUnit.toLowerCase() === 'fahrenheit' && toUnit.toLowerCase() === 'celsius') {
      return (value - 32) * 5/9;
    }
    
    throw new Error(`Unsupported temperature conversion: ${fromUnit} to ${toUnit}`);
  }

  // Helper methods
  getRandomCondition() {
    const conditions = ['Sunny', 'Cloudy', 'Rainy', 'Snowy', 'Thunderstorm', 'Foggy', 'Windy'];
    return conditions[Math.floor(Math.random() * conditions.length)];
  }

  getRandomTemperature(isLow = false) {
    const baseTemp = isLow ? 10 : 20; // Lower range for low temps
    const variation = Math.floor(Math.random() * 20) - 10; // -10 to +10
    return baseTemp + variation;
  }

  getRandomHumidity() {
    return Math.floor(Math.random() * 40) + 40; // 40-80%
  }

  getRandomWindSpeed() {
    return Math.floor(Math.random() * 30); // 0-30 km/h
  }
}

module.exports = WeatherAssistant;