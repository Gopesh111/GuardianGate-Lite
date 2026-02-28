from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="GuardianGate Lite Proxy", version="1.0")

# Include modular routes
app.include_router(api_router, prefix="/v1")

#uvicorn app.main:app --reload