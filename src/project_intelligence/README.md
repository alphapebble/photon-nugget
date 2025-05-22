# Project Intelligence Layer

## Overview

The Project Intelligence Layer is an advanced AI-driven system that automatically extracts, processes, and structures project-related information from various communication channels and documents. By leveraging state-of-the-art AI frameworks and distributed processing, it provides real-time insights and monitoring for project management without requiring manual input.

## Key Features

- **Real-time Data Processing**: Automatically parses emails, Slack/Teams messages, and spreadsheets as they arrive
- **Intelligent Information Extraction**: Detects project names, tasks, updates, owners, blockers, and due dates using AI
- **Structured Project Dashboard**: Maps extracted information into a coherent project management dashboard
- **Automated Resource Monitoring**: Tracks inventory, staffing, and overall progress without manual inputs
- **Distributed Processing**: Scales to handle large volumes of data across multiple nodes

## Architecture

The system is built on three core frameworks:

1. **LangGraph**: Orchestrates complex, branching workflows in the extraction and analysis process
2. **CrewAI/AutoGen**: Enables agent teamwork and collaboration in processing project information
3. **Ray**: Provides distributed, scalable processing of data ingestion and analysis tasks

## Components

- **Data Connectors**: Interface with various data sources (Email, Slack, Teams, Spreadsheets)
- **Extraction Agents**: Specialized AI agents for detecting different aspects of project information
- **Processing Layer**: Distributed processing system for handling document analysis
- **Intelligence Layer**: Advanced analytics and insights generation
- **Dashboard**: Real-time visualization of project status and metrics

## Getting Started

### Prerequisites

- Python 3.10+
- Required dependencies (install with `pip install -r requirements.txt`)

### Installation

1. Install the dependencies:
   ```
   cd src/project_intelligence
   pip install -r requirements.txt
   ```

2. Configure the connectors:
   - Create `.env` file with appropriate API keys and credentials
   - Configure connector settings in the configuration file

3. Start the system:
   ```
   python main.py
   ```

### API Usage

The system exposes a REST API for integration with other systems:

- `POST /register_connector`: Register a new data connector
- `POST /process_document`: Process a document manually
- `GET /projects`: Get all projects
- `GET /project/{project_name}`: Get a specific project
- `GET /stats`: Get system statistics
- `POST /poll_connectors`: Poll all connectors for new data

## Configuration

Example configuration for email connector:

```json
{
  "connector_type": "email",
  "config": {
    "provider": "gmail",
    "credentials_file": "path/to/credentials.json",
    "folders": ["INBOX", "Projects"],
    "max_emails": 100
  }
}
```

## Dashboard Access

The dashboard is available at:

- Web UI: `http://localhost:8000/dashboard`
- API Documentation: `http://localhost:8000/docs`

## Agent Crew Configuration

The system uses a crew of specialized agents:

- **Project Detector**: Identifies project names and scopes
- **Task Manager**: Extracts and structures task information
- **Resource Tracker**: Monitors resource allocation and availability
- **Timeline Analyzer**: Identifies dates, deadlines, and schedules
- **Risk Assessor**: Identifies potential blockers and risks
- **Integration Agent**: Maps extracted information to existing project structures

## Extending the System

The modular design allows for easy extension:

1. Create new connector classes by extending `DataSourceConnector`
2. Add new agent types by creating new agent classes
3. Extend the dashboard with additional visualizations
4. Create custom monitors for specific project metrics

## Troubleshooting

Common issues:

- **Connection errors**: Verify API credentials and network connectivity
- **Processing errors**: Check log files for detailed error messages
- **Missing data**: Ensure connectors are properly configured and have access permissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.