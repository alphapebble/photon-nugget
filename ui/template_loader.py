"""
Template loader for the UI application.
"""
import os
from typing import Dict, Any

# Base path for templates
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def load_template(template_path: str) -> str:
    """
    Load a template file and return its contents.
    
    Args:
        template_path: Path to the template file, relative to the templates directory
        
    Returns:
        The contents of the template file
    """
    full_path = os.path.join(TEMPLATE_DIR, template_path)
    try:
        with open(full_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading template {template_path}: {e}")
        return f"<!-- Error loading template {template_path}: {e} -->"

def render_template(template_path: str, context: Dict[str, Any] = None) -> str:
    """
    Load a template file, render it with the given context, and return the result.
    
    Args:
        template_path: Path to the template file, relative to the templates directory
        context: Dictionary of variables to substitute in the template
        
    Returns:
        The rendered template
    """
    template = load_template(template_path)
    if context:
        # Simple template substitution
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
    return template

def load_js_bundle(*js_files: str) -> str:
    """
    Load multiple JavaScript files and combine them into a single script tag.
    
    Args:
        *js_files: Paths to JavaScript files, relative to the js directory
        
    Returns:
        A script tag containing the combined JavaScript code
    """
    js_code = []
    for js_file in js_files:
        js_path = os.path.join("js", js_file)
        js_code.append(load_template(js_path))
    
    return f"""
    <script>
    {' '.join(js_code)}
    </script>
    """
