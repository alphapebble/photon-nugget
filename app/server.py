from fastapi import FastAPI
from chatbot_engine import generate_response

app = FastAPI()

@app.post("/chat")
async def chat(prompt: str):
    return {"response": generate_response(prompt)}
