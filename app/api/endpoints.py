from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio

from app.schemas.payload import ChatRequest
from app.services.pii_service import scrub_pii
from app.core.circuit_breaker import circuit_breaker
from app.services.cache_service import semantic_cache
from app.services.llm_service import stream_llm_response

router = APIRouter()

@router.post("/chat/stream")
async def chat_proxy_stream(request: ChatRequest, background_tasks: BackgroundTasks):
    # 1. Scrub PII
    safe_prompt = scrub_pii(request.prompt)
    
    # 2. Check Cache First (Synchronous)
    # Pass the threshold from the UI request
    cached_response, similarity = semantic_cache.check_cache(safe_prompt, request.threshold)
    
    if cached_response:
        # If found in cache, we fake a stream for UX consistency
        async def fake_stream():
            words = cached_response.split(" ")
            for word in words:
                yield word + " "
                await asyncio.sleep(0.02) # Typewriter effect
        return StreamingResponse(fake_stream(), media_type="text/event-stream")
    
    # 🚨 3. HARD BUDGET ENFORCEMENT (FinOps Guardrail)
    if not semantic_cache.enforce_budget():
        async def budget_error():
            yield "⚠️ SYSTEM GUARDRAIL: Daily LLM Budget ($0.50) exceeded. Operating in Cache-Only mode. Please try a cached query."
        return StreamingResponse(budget_error(), media_type="text/event-stream")

    # 4. Circuit Breaker
    if not circuit_breaker.check_state():
        raise HTTPException(status_code=503, detail="LLM API is unavailable.")
    
    # 5. Stream from Groq AND schedule the background cache save
    circuit_breaker.record_success()
    
    # 🌪️ Pass chaos_mode to test Fallback logic
    return StreamingResponse(
        stream_llm_response(safe_prompt, safe_prompt, background_tasks, request.chaos_mode), 
        media_type="text/event-stream"
    )

@router.get("/health")
def health_check():
    return {
        "status": "active",
        "circuit_breaker": circuit_breaker.state,
        "cache_size": len(semantic_cache.cache_payloads),
        "cache_hits": semantic_cache.cache_hits
    }