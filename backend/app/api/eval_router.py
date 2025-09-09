# # app/api/eval_router.py
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List

# from app.core.database import get_db
# from app.schemas.eval import EvalCaseCreate, EvalResultRead, EvalMetrics
# from app.services.eval_service import EvalService

# router = APIRouter(prefix="/evals", tags=["evals"])

# @router.post("/run", response_model=EvalResultRead)
# def run_eval(case_data: EvalCaseCreate, db: Session = Depends(get_db)):
#     """
#     Run a single eval case and store the result.
#     """
#     result = EvalService.run_eval_case(db, case_data)
#     return result

# @router.get("/results", response_model=List[EvalResultRead])
# def get_all_results(db: Session = Depends(get_db)):
#     return EvalService.get_all_results(db)

# @router.get("/metrics", response_model=EvalMetrics)
# def get_eval_metrics(db: Session = Depends(get_db)):
#     return EvalService.get_metrics(db)


from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.eval import EvalCaseCreate, EvalResultRead, EvalMetrics
from app.services.eval_service import EvalService
from app.core.rate_limiter import rate_limit  # Redis rate limiter
from app.core.sse import sse  # ✅ SSE manager

router = APIRouter(prefix="", tags=["evals"])

# -------------------------
# Run a single eval case
# -------------------------
@router.post("/run", response_model=EvalResultRead)
@rate_limit(max_requests=3, window_seconds=60)
async def run_eval(
    case_data: EvalCaseCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Run a single eval case, store the result, and notify via SSE.
    """
    return await EvalService.run_eval_case(db, case_data)


# -------------------------
# Get all eval results
# -------------------------
@router.get("/results", response_model=List[EvalResultRead])
@rate_limit(max_requests=10, window_seconds=60)
async def get_all_results(
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Fetch all evaluation results and notify via SSE if available.
    """
    results = await EvalService.get_all_results(db)
    
    # Try SSE notification
    try:
        if sse:  # check if sse is initialized
            await sse.publish(
                {"event": "eval_results_fetched", "results_count": len(results)},
                type="eval"
            )
    except Exception as e:
        print(f"[SSE Error] Could not publish eval results: {e}")
    
    return results


# -------------------------
# Get evaluation metrics
# -------------------------
@router.get("/metrics", response_model=EvalMetrics)
@rate_limit(max_requests=5, window_seconds=60)
async def get_eval_metrics(
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Fetch evaluation metrics and notify via SSE.
    """
    return await EvalService.get_metrics(db)
