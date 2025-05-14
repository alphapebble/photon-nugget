# Solar Sage Agentic RAG Chatbot Quick Start Guide

This guide provides step-by-step instructions for developers to quickly get started with implementing the Solar Sage Agentic RAG Chatbot.

## Prerequisites

Before starting implementation, ensure you have:

1. A working Solar Sage installation
2. Python 3.8+ environment
3. Access to the OpenWeather API
4. Basic understanding of RAG systems and LLMs

## Setup Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/solar-sage.git
   cd solar-sage
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file to add your API keys and configuration
   ```

## Implementation Steps

### Step 1: Implement Tool Registry

1. Create the Tool Registry file:
   ```bash
   mkdir -p agents
   touch agents/tool_registry.py
   ```

2. Implement the Tool Registry class based on the implementation guide:
   ```python
   # agents/tool_registry.py
   """
   Tool Registry for Solar Sage Agent.
   """
   from typing import Dict, Any, Callable, List, Optional

   class ToolRegistry:
       """Registry for agent tools."""
       
       def __init__(self):
           """Initialize an empty tool registry."""
           self.tools: Dict[str, Dict[str, Any]] = {}
       
       def register_tool(
           self, 
           tool_name: str, 
           tool_function: Callable, 
           tool_description: str,
           required_params: List[str],
           optional_params: Optional[List[str]] = None,
           authorization_required: bool = False
       ) -> None:
           """Register a new tool in the registry."""
           self.tools[tool_name] = {
               "function": tool_function,
               "description": tool_description,
               "required_params": required_params,
               "optional_params": optional_params or [],
               "authorization_required": authorization_required
           }
       
       # Add remaining methods from implementation guide
   ```

3. Create a test for the Tool Registry:
   ```bash
   mkdir -p tests/agents
   touch tests/agents/test_tool_registry.py
   ```

   ```python
   # tests/agents/test_tool_registry.py
   import unittest
   from agents.tool_registry import ToolRegistry

   class TestToolRegistry(unittest.TestCase):
       def test_register_tool(self):
           registry = ToolRegistry()
           
           def dummy_tool(param1, param2):
               return {"result": param1 + param2}
           
           registry.register_tool(
               "dummy_tool",
               dummy_tool,
               "A dummy tool for testing",
               ["param1", "param2"]
           )
           
           self.assertIn("dummy_tool", registry.tools)
           self.assertEqual(registry.tools["dummy_tool"]["description"], "A dummy tool for testing")
       
       # Add more tests
   ```

### Step 2: Implement Memory System

1. Create the Memory System file:
   ```bash
   touch agents/memory_system.py
   ```

2. Implement the Memory System class based on the implementation guide:
   ```python
   # agents/memory_system.py
   """
   Memory System for Solar Sage Agent.
   """
   from typing import Dict, Any, List, Optional
   import json
   import os
   from datetime import datetime

   class MemorySystem:
       """Memory system for agent conversations and user preferences."""
       
       def __init__(self, storage_dir: str = "./data/memory"):
           """Initialize the memory system."""
           self.storage_dir = storage_dir
           os.makedirs(storage_dir, exist_ok=True)
       
       # Add remaining methods from implementation guide
   ```

3. Create a test for the Memory System:
   ```bash
   touch tests/agents/test_memory_system.py
   ```

### Step 3: Implement Agent Engine

1. Create the Agent Engine file:
   ```bash
   touch agents/agent_engine.py
   ```

2. Implement the Agent Engine class based on the implementation guide:
   ```python
   # agents/agent_engine.py
   """
   Agent Engine for Solar Sage.
   """
   from typing import Dict, Any, List, Optional, Tuple
   import re
   from llm.base import LLMInterface
   from agents.tool_registry import ToolRegistry
   from agents.memory_system import MemorySystem
   from rag.rag_engine import rag_answer
   from rag.weather_enhanced_rag import weather_enhanced_rag_answer

   class AgentEngine:
       """Core agent logic for Solar Sage."""
       
       def __init__(
           self, 
           llm: LLMInterface,
           tool_registry: ToolRegistry,
           memory_system: MemorySystem,
           require_authorization: bool = True
       ):
           """Initialize the agent engine."""
           self.llm = llm
           self.tool_registry = tool_registry
           self.memory_system = memory_system
           self.require_authorization = require_authorization
       
       # Add remaining methods from implementation guide
   ```

### Step 4: Implement Weather Tools

1. Create the Weather Tools directory and file:
   ```bash
   mkdir -p tools
   touch tools/weather_tools.py
   ```

2. Implement the Weather Tools based on the sample implementation:
   ```python
   # tools/weather_tools.py
   """
   Weather tools for Solar Sage Agent.
   """
   from typing import Dict, Any, List, Optional
   from datetime import datetime, timedelta
   import pandas as pd
   import numpy as np

   from agents.weather_integration import (
       get_weather_for_location,
       extract_solar_relevant_weather,
       estimate_irradiance,
       estimate_production_impact,
       generate_weather_insights
   )

   def get_production_forecast(
       lat: float, 
       lon: float, 
       system_capacity_kw: float = 5.0,
       days_ahead: int = 7
   ) -> Dict[str, Any]:
       """Get solar production forecast based on weather."""
       # Implementation from sample file
   ```

### Step 5: Initialize Agent

1. Create the Agent Initialization file:
   ```bash
   touch agents/initialize.py
   ```

2. Implement the Agent Initialization based on the implementation guide:
   ```python
   # agents/initialize.py
   """
   Initialize the Solar Sage Agent.
   """
   from llm.llm_factory import get_llm
   from agents.tool_registry import ToolRegistry
   from agents.memory_system import MemorySystem
   from agents.agent_engine import AgentEngine
   from tools.weather_tools import get_production_forecast

   def initialize_agent(require_authorization: bool = True) -> AgentEngine:
       """Initialize the agent with tools and configuration."""
       # Implementation from implementation guide
   ```

### Step 6: Update API Server

1. Update the server file to include agent capabilities:
   ```bash
   # Edit app/server.py to add agent endpoints
   ```

2. Add the following imports and code:
   ```python
   # Add to app/server.py
   from agents.initialize import initialize_agent
   from pydantic import BaseModel

   class AgentChatRequest(BaseModel):
       query: str
       user_id: str
       lat: Optional[float] = None
       lon: Optional[float] = None
       system_size_kw: Optional[float] = None
       panel_type: Optional[str] = None
       authorized: Optional[bool] = False

   class AgentChatResponse(BaseModel):
       response: str
       tools_used: List[str] = []
       requires_authorization: bool = False

   # Initialize agent
   agent = initialize_agent(require_authorization=True)

   @app.post("/agent_chat", response_model=AgentChatResponse)
   async def agent_chat(request: AgentChatRequest):
       """Process a chat request using the agent."""
       # Implementation from implementation guide
   ```

## Testing Your Implementation

1. Run unit tests:
   ```bash
   python -m unittest discover tests
   ```

2. Start the server:
   ```bash
   python -m app.server
   ```

3. Test the agent chat endpoint:
   ```bash
   curl -X POST http://localhost:8000/agent_chat \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What will my solar production be like tomorrow?",
       "user_id": "test_user",
       "lat": 37.7749,
       "lon": -122.4194,
       "system_size_kw": 5.0
     }'
   ```

## Next Steps

After implementing the core components, you can:

1. Implement additional tools in the `tools/` directory
2. Update the UI to support agent interactions
3. Add user authentication and authorization
4. Implement monitoring and logging for agent actions

## Troubleshooting

### Common Issues

1. **LLM Not Responding**
   - Check that Ollama is running (if using Ollama)
   - Verify the model is correctly loaded

2. **Tool Execution Errors**
   - Check that all required parameters are provided
   - Verify API keys are correctly set in environment variables

3. **Memory System Errors**
   - Ensure the storage directory is writable
   - Check file permissions

## Resources

- Full implementation guide: `docs/agent_implementation_guide.md`
- Architecture overview: `docs/agentic_rag_chatbot.md`
- Project roadmap: `docs/agentic_rag_roadmap.md`
- Implementation status: `docs/implementation_status.md`

## Conclusion

This quick start guide provides the essential steps to begin implementing the Solar Sage Agentic RAG Chatbot. By following these steps, you can quickly set up the core agent framework and start adding tools to enhance the chatbot's capabilities.

For more detailed information, refer to the comprehensive documentation in the `docs/` directory.
