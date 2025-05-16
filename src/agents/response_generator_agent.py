"""
Response Generator Agent for Solar Sage.

This agent is responsible for generating responses based on context and query.
"""
from agents.base_agent import BaseAgent
from rag.prompts.template_loader import load_structured_prompt, render_prompt
from typing import List, Dict, Any, Optional

class ResponseGeneratorAgent(BaseAgent):
    """Agent responsible for generating responses."""

    def __init__(self):
        """Initialize the response generator agent."""
        super().__init__(
            name="ResponseGenerator",
            description="Generates responses based on context and query"
        )

    def generate_response(self, query: str, context: List[str], notes: Optional[List[str]] = None) -> str:
        """
        Generate response based on query and context.

        Args:
            query: User query
            context: Retrieved context documents
            notes: Optional notes or insights to include

        Returns:
            Generated response
        """
        # Load prompt template
        config, prompt_template = load_structured_prompt("dual_agent_rag")

        # Prepare context string
        context_str = "\n\n".join(context)

        # Add notes if available
        notes_str = ""
        if notes and len(notes) > 0:
            notes_str = "\n\n".join(notes)

        # Render prompt
        prompt_vars = {
            "query": query,
            "context": context_str,
        }

        # Add notes if available
        if notes_str:
            prompt_vars["notes"] = notes_str

        prompt = render_prompt(prompt_template, prompt_vars)

        # Generate response using existing LLM
        return self.llm.generate(prompt)

    def run(self, query: str, context: List[str], notes: Optional[List[str]] = None) -> str:
        """
        Run the response generator agent.

        Args:
            query: User query
            context: Retrieved context documents
            notes: Optional notes or insights to include

        Returns:
            Generated response
        """
        return self.generate_response(query, context, notes)
