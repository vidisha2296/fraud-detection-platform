# # app/api/monitoring_router.py
# from fastapi import APIRouter
# from app.services.monitoring_service import MonitoringService

# router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# @router.get("/health", summary="Service Health Check")
# def health_check():
#     """
#     Returns status OK if the service is running and DB is reachable.
#     """
#     return MonitoringService.health()

# @router.get("/metrics", summary="Service Metrics")
# def metrics():
#     """
#     Returns metrics such as total transactions, fraud alerts, and evaluation success rates.
#     """
#     return MonitoringService.metrics()


from fastapi import APIRouter, Request
from app.services.monitoring_service import MonitoringService
from app.core.rate_limiter import rate_limit  # Redis rate limiter

router = APIRouter(prefix="", tags=["monitoring"])

@router.get("/health", summary="Service Health Check")
@rate_limit(max_requests=20, window_seconds=60)
async def health_check(request: Request = None):
    """
    Returns status OK if the service is running and DB is reachable.
    """
    return await MonitoringService.health()


@router.get("/metrics", summary="Service Metrics")
@rate_limit(max_requests=10, window_seconds=60)
async def metrics(request: Request = None):
    """
    Returns metrics such as total transactions, fraud alerts, and evaluation success rates.
    """
    return await MonitoringService.metrics()
