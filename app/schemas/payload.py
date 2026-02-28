from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    prompt: str
    threshold: float = 0.85
    chaos_mode: bool = False

class ChatResponse(BaseModel):
    status: str
    original_prompt: str
    scrubbed_prompt: str
    llm_response: str
    source: str           # "CACHE" or "LLM_API"
    similarity: float     # 0.0 to 1.0
    circuit_state: str