# Next.js Frontend Architecture

This document provides an overview of the Next.js frontend architecture for Solar Sage, explaining the different components and how they interact with the backend API.

## Overview

The Next.js frontend is the primary user interface for Solar Sage, providing a modern, responsive web application with advanced features. It's built with Next.js, React, and styled-components.

## Key Components

### Pages

The Next.js frontend is organized around pages, each representing a different section of the application:

- **Home Page** (`src/pages/index.tsx`): Welcome screen with navigation to key features
- **Chat Page** (`src/pages/chat.tsx`): Chat interface for interacting with the RAG system
- **Solar Forecast Page** (`src/pages/solar-forecast.tsx`): Form for inputting location and system details, displaying forecast results
- **Evaluation Dashboard** (`src/pages/evaluation.tsx`): Visualize and analyze RAG system evaluation metrics
- **About Page** (`src/pages/about.tsx`): Information about the system

### Components

The frontend uses a component-based architecture with reusable React components:

- **Layout Components** (`src/components/Layout/`):
  - `Layout.tsx`: Main layout wrapper with sidebar and navbar
  - `Sidebar.tsx`: Navigation sidebar
  - `Navbar.tsx`: Top navigation bar
- **Chat Components** (`src/components/Chat/`):
  - `ChatInput.tsx`: Input field for chat messages
  - `ChatMessage.tsx`: Display for chat messages
  - `LocationSettings.tsx`: Form for location settings
- **Solar Forecast Components** (`src/components/SolarForecast/`):
  - `ForecastForm.tsx`: Form for inputting forecast parameters
  - `ForecastResults.tsx`: Display for forecast results
- **Common Components** (`src/components/common/`):
  - `ClientOnly.tsx`: Wrapper for components that should only render on the client

### API Client

The Next.js frontend communicates with the backend API through an API client (`src/api/apiClient.ts`). The API client provides methods for:

- **Chat**: `chat()` - Send a chat message to the API
- **Solar Forecast**: `getSolarForecast()` - Get a solar energy forecast
- **Cost Savings**: `getCostSavings()` - Get a cost savings analysis
- **RAG**: `getRagResponse()` - Get a RAG response

API requests are proxied through Next.js API routes (`src/pages/api/[...path].ts`), which forward the requests to the FastAPI backend. This approach:

1. Avoids CORS issues
2. Provides a consistent API URL
3. Allows for request/response transformation if needed
4. Simplifies authentication and error handling

## Features

### Chat Interface

The chat interface (`src/pages/chat.tsx`) provides a natural language interaction with the RAG system:

- **Message History**: Display of past messages
- **Input Field**: Field for entering new messages
- **Location Settings**: Form for setting location parameters
- **Weather Context**: Display of weather context in responses
- **Solar Context**: Display of solar context in responses

### Solar Forecast

The solar forecast page (`src/pages/solar-forecast.tsx`) provides a form for inputting location and system details, and displays forecast results:

- **Forecast Form**: Form for inputting location and system parameters
- **Forecast Results**: Display of forecast results
- **Cost Savings Analysis**: Display of cost savings analysis
- **Visualization**: Charts and graphs for forecast data

### Evaluation Dashboard

The evaluation dashboard (`src/pages/evaluation.tsx`) provides a comprehensive view of RAG system evaluation metrics:

- **Summary Metrics**: Overview of key metrics (keyword match, response time, etc.)
- **Metrics Over Time**: Chart showing how metrics change over time
- **Metrics Comparison**: Chart comparing metrics across different questions
- **Detailed Results**: Table with detailed results for each question

## Styling

The application uses styled-components for styling. Global styles are defined in `src/pages/_app.tsx`.

## Accessing the Next.js Frontend

The Next.js frontend is available at:

```
http://localhost:3000
```

You can start it using:

```bash
# Start only the Next.js frontend
./solar_sage.sh next start 3000
```

For more information about shell commands, see the [Shell Commands Reference](../reference/shell_commands.md).

## API Integration

For information about how the Next.js frontend integrates with the backend API, see the [API Architecture](api_architecture.md) documentation.

## Future Enhancements

Planned enhancements for the Next.js frontend include:

1. **Real-time Updates**: WebSocket integration for real-time updates
2. **Mobile App**: Native mobile app using React Native
3. **Offline Support**: Progressive Web App (PWA) for offline access
4. **Accessibility Improvements**: Better support for screen readers and keyboard navigation
5. **Authentication**: User authentication and authorization
6. **Personalization**: User preferences and settings
7. **Notifications**: Real-time notifications for alerts and updates
8. **Multi-language Support**: Internationalization and localization
