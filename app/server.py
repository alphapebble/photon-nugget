from fastapi import FastAPI
from pydantic import BaseModel
from model.chatbot_engine import generate_response

app = FastAPI()

# Define a request body
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = generate_response(request.prompt)
    return {"response": response}
