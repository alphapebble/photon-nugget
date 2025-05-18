# Gradio UI Architecture

This document provides an overview of the Gradio UI architecture for Solar Sage, explaining the different components and how they interact with the backend API.

## Overview

The Gradio UI provides a simplified conversational interface for quick interactions with the RAG system. It's maintained for backward compatibility and for users who prefer a simpler interface.

## Key Components

### Main Application

The main Gradio application is defined in `ui/app.py`. It sets up the Gradio server and loads the UI components.

### UI Components

The Gradio UI is organized around components, each providing a different interface:

- **Simple UI** (`ui/components/simple_ui.py`): Main conversational interface
  - Chat interface with message history
  - Input field for new messages
  - Location input for weather-enhanced responses
- **Evaluation Dashboard** (`ui/components/evaluation_dashboard.py`): Dashboard for RAG evaluation metrics
  - Summary metrics display
  - Metrics over time chart
  - Metrics comparison chart
  - Detailed results table
- **Weather Dashboard** (`ui/components/weather_dashboard.py`): Weather data visualization
  - Current conditions display
  - Forecast chart
  - Insights card

### API Client

The Gradio UI communicates with the backend API through a Python-based API client (`ui/api/client.py`). The API client provides methods for:

- **Chat**: `chat()` - Send a chat message to the API
- **Weather**: `get_weather()` - Get weather data for a location
- **Solar Forecast**: `get_solar_forecast()` - Get a solar energy forecast

The API client handles retries, error formatting, and response parsing.

## Features

### Conversational Interface

The conversational interface (`ui/components/simple_ui.py`) provides a simple chat interface for interacting with the RAG system:

- **Message History**: Display of past messages
- **Input Field**: Field for entering new messages
- **Location Input**: Field for setting location parameters
- **Weather Context**: Display of weather context in responses
- **Solar Context**: Display of solar context in responses

### Evaluation Dashboard

The evaluation dashboard (`ui/components/evaluation_dashboard.py`) provides a visualization of RAG system evaluation metrics:

- **Summary Metrics**: Overview of key metrics (keyword match, response time, etc.)
- **Metrics Over Time**: Chart showing how metrics change over time
- **Metrics Comparison**: Chart comparing metrics across different questions
- **Detailed Results**: Table with detailed results for each question

### Weather Dashboard

The weather dashboard (`ui/components/weather_dashboard.py`) provides a visualization of weather data for solar forecasting:

- **Current Conditions**: Display of current weather conditions
- **Forecast Chart**: Chart showing weather forecast for the next 7 days
- **Insights Card**: Display of insights based on weather data

## Templates and Styling

The Gradio UI uses HTML templates and CSS for styling:

- **Templates** (`ui/templates/`): HTML templates for UI components
- **CSS** (`ui/templates/css/`): CSS styles for UI components

## Accessing the Gradio UI

The Gradio UI is available at:

```
http://localhost:7860
```

You can start it using:

```bash
# Start only the Gradio UI
./solar_sage.sh ui start 7860
```

For more information about shell commands, see the [Shell Commands Reference](../reference/shell_commands.md).

## API Integration

For information about how the Gradio UI integrates with the backend API, see the [API Architecture](api_architecture.md) documentation.

## Why Gradio UI is Maintained

The Gradio UI is maintained for several reasons:

1. **Backward Compatibility**: Existing users and documentation may reference the Gradio UI
2. **Simplicity**: Provides a simpler interface for quick interactions
3. **Rapid Prototyping**: Easier to prototype new features and visualizations
4. **Python Integration**: Tighter integration with Python-based components
5. **Conversational Focus**: Optimized for conversational interactions

While the Next.js frontend is the primary UI for Solar Sage, the Gradio UI remains a valuable alternative for specific use cases.

## Future Considerations

As the project evolves, the role of the Gradio UI may change:

1. **Specialized Interfaces**: Focus on specialized interfaces not covered by the Next.js frontend
2. **Developer Tools**: Provide developer-focused tools and debugging interfaces
3. **Evaluation Tools**: Enhance the evaluation dashboard with more advanced metrics
4. **Integration Testing**: Use for integration testing and automated UI testing

The Gradio UI will continue to be maintained as long as it provides value to users and developers.
