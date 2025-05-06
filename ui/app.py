import gradio as gr
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configurable environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = os.getenv("BACKEND_CHAT_ENDPOINT", "/chat")
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8501))


def chat_with_bot(user_input: str) -> str:
    try:
        response = requests.post(
            f"{BACKEND_URL}{BACKEND_CHAT_ENDPOINT}",
            json={"query": user_input}
        )
        response.raise_for_status()
        return response.json().get("response", "[No response returned]")
    except Exception as e:
        return f"Error: Could not connect to the backend. Details: {str(e)}"


with gr.Blocks(title="Photon Nugget Assistant") as app:
    gr.Markdown("""
    ## Photon Nugget: Private Solar AI Assistant  
    Ask questions about solar energy, systems, and installations.
    """)

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(
                label="Your Question",
                placeholder="Ask something about solar installations, maintenance, or components...",
                lines=4
            )
            submit_btn = gr.Button("Ask")
        with gr.Column():
            output = gr.Textbox(
                label="Chatbot Response",
                placeholder="Response will appear here...",
                lines=8
            )

    submit_btn.click(fn=chat_with_bot, inputs=[user_input], outputs=[output])

# Launch Gradio app
app.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)
