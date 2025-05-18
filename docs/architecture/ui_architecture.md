# Solar Sage UI Architecture

This document provides an overview of the Solar Sage UI architecture, explaining the dual UI approach and how the different components interact.

## Overview

Solar Sage has a dual UI architecture:

1. **Next.js Frontend** (`frontend/`): Modern React-based UI with advanced features
2. **Gradio UI** (`ui/`): Simplified conversational interface for quick interactions

This architecture provides flexibility in how users interact with the system, offering both a feature-rich web application and a lightweight conversational interface.

## Dual UI Architecture

The dual UI architecture allows users to choose the interface that best fits their needs:

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Next.js        │     │  Gradio         │
│  Frontend       │     │  UI             │
│                 │     │                 │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│                                         │
│             FastAPI Backend             │
│                                         │
└─────────────────────────────────────────┘
```

Both UIs communicate with the same backend API, ensuring consistent behavior regardless of which UI is used.

## Component Comparison

| Feature                   | Next.js Frontend                | Gradio UI                     |
|---------------------------|--------------------------------|-------------------------------|
| **Primary Purpose**       | Full-featured web application  | Simple conversational interface |
| **Technology Stack**      | Next.js, React, styled-components | Gradio, Python              |
| **Target Users**          | All users                      | Users who prefer simplicity   |
| **Deployment**            | Separate Node.js server        | Embedded in Python backend    |
| **Default Port**          | 3000                           | 7860                          |
| **Evaluation Dashboard**  | Advanced with interactive charts | Basic with static charts     |
| **Solar Forecast**        | Dedicated page with detailed form | Limited integration         |
| **Responsive Design**     | Full support                   | Limited support               |
| **Offline Support**       | Planned (PWA)                  | Not supported                 |

## Why Both UIs?

The dual UI architecture provides several benefits:

1. **Gradio UI**: 
   - Maintained for backward compatibility
   - Provides a simple, lightweight interface for quick interactions
   - Useful for users who prefer a more straightforward experience
   - Easier to extend with custom visualizations for specific use cases
   - Tighter integration with Python-based components

2. **Next.js Frontend**:
   - Provides a modern, responsive web application
   - Offers more advanced features and visualizations
   - Better user experience for complex interactions
   - More customizable and extensible for future features
   - Better support for mobile devices

Users can choose the UI that best fits their needs and preferences.

## Detailed Architecture Documentation

For detailed information about each UI component, please refer to the following documentation:

- [Next.js Frontend Architecture](nextjs_frontend.md) - Detailed documentation for the Next.js frontend
- [Gradio UI Architecture](gradio_ui.md) - Detailed documentation for the Gradio UI

## API Integration

Both UIs communicate with the same backend API, using the `/sage` endpoint for natural language interactions. For detailed information about the API architecture, see the [API Architecture](api_architecture.md) documentation.

## Access URLs

For a comprehensive list of access URLs for both UIs, see the [Shell Commands Reference](../reference/shell_commands.md#access-urls).

## Shell Commands

For detailed information about shell commands for managing the UIs, see the [Shell Commands Reference](../reference/shell_commands.md).

## Future Roadmap

The future roadmap for the UI architecture includes:

1. **Enhanced Integration**: Tighter integration between the two UIs
2. **Shared Components**: Common component library for consistent UI elements
3. **Feature Parity**: Ensuring key features are available in both UIs
4. **Specialized Focus**: Evolving each UI to focus on its strengths
5. **Unified Authentication**: Single sign-on across both UIs
6. **Mobile Support**: Enhanced mobile support for both UIs

## Conclusion

The dual UI architecture of Solar Sage provides flexibility in how users interact with the system. The Next.js frontend offers a modern, feature-rich experience, while the Gradio UI provides a simpler, more focused conversational interface. Both UIs communicate with the same backend API, ensuring consistent behavior regardless of which UI is used.
