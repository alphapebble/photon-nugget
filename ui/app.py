import gradio as gr
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = os.getenv("BACKEND_CHAT_ENDPOINT", "/ask")
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8501))

def chat_with_bot(user_input):
    try:
        response = requests.post(
            f"{BACKEND_URL}{BACKEND_CHAT_ENDPOINT}",
            json={"query": user_input}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"⚠️ Error communicating with the chatbot: {str(e)}"

iface = gr.Interface(
    fn=chat_with_bot,
    inputs=gr.Textbox(lines=2, placeholder="Ask me anything about solar panels..."),
    outputs="text",
    title="☀️ Photon-Nugget On-Prem AI Chatbot",
    description="Chat with your private solar knowledge assistant. No cloud involved!",
    theme="default"
)

iface.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)
