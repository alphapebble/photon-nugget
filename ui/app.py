import gradio as gr
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = os.getenv("BACKEND_CHAT_ENDPOINT", "/chat")
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8501))


def chat_with_bot(user_input):
    try:
        response = requests.post(
            f"{BACKEND_URL}{BACKEND_CHAT_ENDPOINT}",
            json={"prompt": user_input}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"⚠️ Error communicating with the chatbot: {str(e)}"


with gr.Blocks(theme="soft") as app:
    gr.Markdown(
        """
        # ☀️ Photon-Nugget: Private Solar AI Assistant
        _Chat privately with your on-premise solar knowledge base. No cloud involved!_
        """
    )

    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Your Question:",
                                    placeholder="Ask about solar panels, installation, maintenance...", lines=5)
            submit_btn = gr.Button("Submit", variant="primary")
        with gr.Column():
            output = gr.Textbox(label="Chatbot Response:", placeholder="Response will appear here...", lines=10)

    submit_btn.click(fn=chat_with_bot, inputs=[user_input], outputs=[output])

app.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)
