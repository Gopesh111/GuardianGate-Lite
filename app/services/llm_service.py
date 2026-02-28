import os
from groq import AsyncGroq
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("🚨 WARNING: GROQ_API_KEY not found in .env file! Using dummy key to prevent crash.")
    client = AsyncGroq(api_key="dummy_key_to_prevent_startup_crash")
else:
    client = AsyncGroq(api_key=api_key)

# SMART SYSTEM PROMPT (To prevent over-refusal)
SYSTEM_PROMPT = """You are an AI assistant behind a strict enterprise security gateway.
Any sensitive user data in the prompt has already been removed and replaced with [REDACTED].
CRITICAL INSTRUCTION: Do NOT mention, infer, acknowledge, or explain the existence of redacted, missing, or sensitive content.
Act as if the redacted content never existed. Answer ONLY the remaining valid query directly and concisely."""

async def stream_llm_response(prompt: str, original_prompt: str, background_tasks, chaos_mode: bool = False):
    if not api_key or client.api_key == "dummy_key_to_prevent_startup_crash":
        yield "Error: GROQ_API_KEY is missing. Please check your .env file."
        return

    stream = None

    try:
        if chaos_mode:
            print("🌪️ CHAOS MODE ACTIVE: Simulating Primary LLM Failure...")
            raise Exception("Chaos Engineering: Simulated 503 Timeout")

        stream = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            stream=True
        )
    except Exception as primary_e:
        print(f"⚠️ Primary Model Failed ({primary_e}). Auto-switching to Fallback Model...")
        
        try:
            # 🔄 NEW FALLBACK: Groq's most stable current flagship model
            stream = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", # Highly available fallback
                temperature=0.5,
                stream=True
            )
        except Exception as fallback_e:
            # 🛡️ THE ULTIMATE GRACEFUL DEGRADATION (No more trial & error!)
            print(f"🚨 Critical Upstream Failure: {fallback_e}")
            yield "⚠️ SYSTEM GUARDRAIL: All live AI models are currently down or decommissioned by the provider. The proxy is operating in Cache-Only mode. Please try a previously cached question."
            return

    try:
        full_response_accumulator = ""
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                full_response_accumulator += token
                yield token 
                
        from app.services.cache_service import semantic_cache
        background_tasks.add_task(semantic_cache.add_to_cache, original_prompt, full_response_accumulator)
        print("✅ Background Task: Saved full streamed response to cache.")
        
    except Exception as e:
        yield f"\n[Stream Interrupted Error]: {str(e)}"
