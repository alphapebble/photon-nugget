from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=5, description="The user’s input question.")

class ChatResponse(BaseModel):
    response: str
