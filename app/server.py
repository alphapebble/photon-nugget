from fastapi import FastAPI
from app.prompt import ChatRequest, ChatResponse
from rag.runner import rag_answer  # changed from chatbot_engine

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = rag_answer(request.query)
    return {"response": answer}
