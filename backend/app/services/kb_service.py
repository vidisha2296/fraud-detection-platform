from sqlalchemy.orm import Session
from typing import List
from app.models.kb import KBEntry
from app.schemas.kb_schema import KBEntryCreate, KBEntryRead, KBSearchResult
from app.core.sse import sse  # ✅ SSE manager
import asyncio

class KBService:

    @staticmethod
    async def create_entry(db: Session, entry_data: KBEntryCreate) -> KBEntryRead:
        def _create():
            entry = KBEntry(**entry_data.dict())
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return KBEntryRead.from_orm(entry)

        entry_read = await asyncio.to_thread(_create)

        # 🔔 SSE event for frontend
        await sse.publish(
            {
                "event": "kb_entry_created",
                "entry": entry_read.dict()
            },
            type="kb"
        )

        return entry_read

    @staticmethod
    async def search_entries(db: Session, query: str) -> list["KBSearchResult"]:
        """
        Search KB entries for a query.
        Returns an empty list if no entries found or DB is empty.
        """
        def _search():
            results = []
            try:
                entries = db.query(KBEntry).all()
                query_lower = query.lower()
                for entry in entries:
                    anchors = entry.anchors or []
                    if (query_lower in entry.title.lower() or
                        query_lower in entry.snippet.lower() or
                        any(query_lower in str(a).lower() for a in anchors)):
                        results.append(KBSearchResult(
                            id=entry.id,
                            title=entry.title,
                            snippet=entry.snippet,
                            anchors=anchors
                        ))
            except Exception:
                # Any DB errors are ignored
                pass
            return results

        return await asyncio.to_thread(_search)
