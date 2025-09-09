from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import (
    transaction_router,
    insights_router,
    fraud_router,
    action_router,
    kb_router,
    eval_router,
    monitoring_router
)
from app.core.rate_limiter import rate_limit 

app = FastAPI(title=settings.app_name, debug=settings.debug)

# --- CORS setup ---
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Register routers ---
app.include_router(transaction_router.router, prefix="/transactions", tags=["Transactions"])
app.include_router(insights_router.router, prefix="/insights", tags=["Insights"])
app.include_router(fraud_router.router, prefix="/fraud", tags=["Fraud Alerts"])
app.include_router(action_router.router, prefix="/actions", tags=["Actions"])
app.include_router(kb_router.router, prefix="/kb", tags=["Knowledge Base"])
app.include_router(eval_router.router, prefix="/evals", tags=["Evaluations"])
app.include_router(monitoring_router.router, tags=["Monitoring"])

@app.get("/")
async def root():
    return {
        "app_name": settings.app_name,
        "database_url": settings.database_url,
        "redis_url": settings.redis_url
    }

# --- TEST ENDPOINT FOR RATE LIMITING ---
@app.get("/test")
@rate_limit(max_requests=3, window_seconds=10, key="test_endpoint")  # custom key
async def test_endpoint(request: Request):
    return {"message": "OK"}
