# Solar Sage Frontend

This is the frontend for Solar Sage, an intelligent solar energy assistant. It's built with Next.js, React, and styled-components.

## Features

- **Home Page**: Welcome screen with navigation to key features
- **Solar Forecast**: Form for inputting location and system details, displaying forecast results
- **Chat**: Chat interface for interacting with the RAG system
- **About**: Information about the system

## Getting Started

### Prerequisites

- Node.js 16.x or higher
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
```

2. Create a `.env.local` file in the root directory with the following content:

```
API_URL=http://localhost:3001/api
```

### Development

Run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Building for Production

Build the application for production:

```bash
npm run build
# or
yarn build
```

Start the production server:

```bash
npm run start
# or
yarn start
```

## Project Structure

- `public/`: Static assets
- `src/`
  - `api/`: API client
  - `components/`: React components
    - `Layout/`: Layout components
    - `SolarForecast/`: Solar forecast components
    - `Chat/`: Chat components
    - `common/`: Common UI components
  - `hooks/`: Custom React hooks
  - `pages/`: Next.js pages
  - `styles/`: CSS/SCSS styles
  - `utils/`: Utility functions

## API Integration

The frontend communicates with the backend API through the API client in `src/api/apiClient.ts`. The API client provides methods for:

- Chat: `chat()`
- Solar Forecast: `getSolarForecast()`
- Cost Savings: `getCostSavings()`
- RAG: `getRagResponse()`

API requests are proxied through Next.js API routes in `src/pages/api/[...path].ts`, which forward the requests to the FastAPI backend. This approach:

1. Avoids CORS issues
2. Provides a consistent API URL
3. Allows for request/response transformation if needed
4. Simplifies authentication and error handling

## Styling

The application uses styled-components for styling. Global styles are defined in `src/pages/_app.tsx`.

## License

This project is licensed under the MIT License.
