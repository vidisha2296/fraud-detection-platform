# # app/api/kb_router.py
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List

# from app.core.database import get_db
# from app.schemas.kb_schema import KBEntryCreate, KBEntryRead, KBSearchResult
# from app.services.kb_service import KBService

# router = APIRouter(prefix="/kb", tags=["kb"])

# @router.post("/", response_model=KBEntryRead)
# def create_kb_entry(entry_data: KBEntryCreate, db: Session = Depends(get_db)):
#     """
#     Add a new KB entry.
#     """
#     return KBService.create_entry(db, entry_data)

# @router.get("/search", response_model=List[KBSearchResult])
# def search_kb(query: str, db: Session = Depends(get_db)):
#     """
#     Search KB entries by title, snippet, or anchors.
#     """
#     return KBService.search_entries(db, query)


from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.kb_schema import KBEntryCreate, KBEntryRead, KBSearchResult
from app.services.kb_service import KBService
from app.core.rate_limiter import rate_limit  # Redis rate limiter
from app.core.sse import sse  # ✅ SSE manager

router = APIRouter(prefix="", tags=["kb"])

# -------------------------
# Add a new KB entry
# -------------------------
@router.post("/", response_model=KBEntryRead)
@rate_limit(max_requests=5, window_seconds=60)
async def create_kb_entry(
    entry_data: KBEntryCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    entry_read = await KBService.create_entry(db, entry_data)

    # 🔔 SSE event for frontend
    await sse.publish(
        {
            "event": "kb_entry_created",
            "entry": entry_read.dict()
        },
        type="kb"
    )

    return entry_read


# -------------------------
# Search KB entries
# -------------------------
@router.get("/search", response_model=List[KBSearchResult])
@rate_limit(max_requests=10, window_seconds=60)
async def search_kb(
    query: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    results = await KBService.search_entries(db, query)

    # 🔔 SSE event for search results
    await sse.publish(
        {
            "event": "kb_search_performed",
            "query": query,
            "results_count": len(results)
        },
        type="kb"
    )

    return results
