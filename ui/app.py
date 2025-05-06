import gradio as gr
import requests
import os
from dotenv import load_dotenv

# Load .env settings
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_CHAT_ENDPOINT = os.getenv("BACKEND_CHAT_ENDPOINT", "/chat")
SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 8501))


def ask_model(user_message, history):
    try:
        response = requests.post(
            f"{BACKEND_URL}{BACKEND_CHAT_ENDPOINT}",
            json={"query": user_message}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


with gr.Blocks(theme=gr.themes.Soft()) as app:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### ☀️ **Photon-Nugget**")
            gr.Markdown("_Private Solar AI Assistant_")
            gr.Markdown("📦 Model: `Mistral` via Ollama")
            gr.Markdown("🧠 Knowledge: Custom Ingested Solar Docs")
            gr.Markdown("🔗 [GitHub](https://github.com/balijepalli/photon-nugget)")
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Ask SolarBot 🌞", height=400)
            user_input = gr.Textbox(placeholder="Ask a question about solar...", show_label=False)
            with gr.Row():
                send_btn = gr.Button("🚀 Ask")
                clear_btn = gr.Button("🧹 Clear")

    def respond(message, history):
        reply = ask_model(message, history)
        history.append((message, reply))
        return "", history

    send_btn.click(fn=respond, inputs=[user_input, chatbot], outputs=[user_input, chatbot])
    clear_btn.click(fn=lambda: [], outputs=[chatbot])

app.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)
