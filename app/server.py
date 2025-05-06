from fastapi import FastAPI
from app.prompt import ChatRequest, ChatResponse
from rag.rag_engine import rag_answer

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = rag_answer(request.query)
    return ChatResponse(response=answer)
