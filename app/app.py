import gradio as gr
import requests

def chat_with_bot(user_input):
    response = requests.post(
        "http://localhost:8000/chat",
        params={"prompt": user_input}
    )
    return response.json()["response"]

# Create a simple chat interface
iface = gr.Interface(
    fn=chat_with_bot,
    inputs="text",
    outputs="text",
    title="On-Prem AI Chatbot",
    description="Ask anything to your private chatbot!",
)

iface.launch(server_name="0.0.0.0", server_port=8501)
