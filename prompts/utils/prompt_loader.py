import os
import yaml
from jinja2 import Template

def load_structured_prompt(prompt_name, prompts_dir="prompts"):
    """
    Load a structured .prompt file (YAML config + prompt body).
    Returns a tuple (config_dict, prompt_body_str).
    """
    prompt_path = os.path.join(prompts_dir, f"{prompt_name}.prompt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split YAML front matter and prompt body
    try:
        _, yaml_content, prompt_body = content.split('---', 2)
        config = yaml.safe_load('---' + yaml_content)
    except ValueError:
        raise ValueError(f"Invalid prompt file format for {prompt_path}. Make sure it has YAML front matter.")

    return config, prompt_body.strip()

def render_prompt(prompt_body, variables):
    """
    Render the prompt body by replacing variables using Jinja2 template engine.
    """
    template = Template(prompt_body)
    return template.render(**variables)

# Example usage:
if __name__ == "__main__":
    config, prompt_body = load_structured_prompt("greet_guest")
    filled_prompt = render_prompt(prompt_body, {
        "location": "Cafe Mirage",
        "name": "Preetam",
        "style": "Shakespearean"
    })

    print("Model config:", config)
    print("Filled Prompt:\n", filled_prompt)
