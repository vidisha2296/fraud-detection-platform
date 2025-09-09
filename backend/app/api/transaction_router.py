from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from typing import List
import csv
import io
from datetime import datetime, timedelta
import time
import asyncio
import json
from pydantic import BaseModel
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.core.sse import sse
from app.schemas.transaction import TransactionIngest, TransactionRead
from app.services.transaction_service import TransactionService
from app.models.transaction import Transaction  # <<<< add this
router = APIRouter(prefix="", tags=["Transactions"])

# -------------------------
# Get transactions for last 90 days with performance logging
# -------------------------
# @router.get("/customer/{customer_id}", response_model=List[TransactionRead])
# async def get_transactions_last_90d(customer_id: str, db: Session = Depends(get_db)):
#     start = time.perf_counter()
#     txns = await TransactionService.get_transactions_by_customer_last_90d(db, customer_id)
#     end = time.perf_counter()
#     duration_ms = (end - start) * 1000
#     print(f"[Performance] GET /customer/{customer_id} last 90d query: {duration_ms:.2f} ms")
#     return txns




class PaginatedTransactions(BaseModel):
    items: List[TransactionRead]
    total: int

@router.get("/customer/{customer_id}", response_model=PaginatedTransactions)
@rate_limit(max_requests=5, window_seconds=60)
async def get_transactions_last_90d(
    request: Request,
    customer_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max number of records to return"),
    db: Session = Depends(get_db)
):
    start = time.perf_counter()
    
    txns = await TransactionService.get_transactions_by_customer_last_90d(
        db, customer_id, skip=skip, limit=limit
    )

    total_count = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.timestamp >= datetime.utcnow() - timedelta(days=90)
    ).count()

    end = time.perf_counter()
    duration_ms = (end - start) * 1000
    print(f"[Performance] GET /customer/{customer_id} last 90d query: {duration_ms:.2f} ms")
    
    return {"items": txns, "total": total_count}

# -------------------------
# JSON ingestion endpoint with performance logging
# -------------------------
@router.post("/ingest", response_model=List[TransactionRead])
@rate_limit(max_requests=5, window_seconds=60)
async def ingest_transactions(
    records: List[TransactionIngest],
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Ingest transactions from JSON.
    Deduplicates by (customer_id, txn_id).
    Risk evaluation + fallback handled in TransactionService.
    """
    start = time.perf_counter()
    result = await TransactionService.ingest_transactions(db, records)
    end = time.perf_counter()
    duration_ms = (end - start) * 1000
    print(f"[Performance] POST /ingest {len(records)} records: {duration_ms:.2f} ms")

    # SSE broadcast for each ingested transaction
    for txn in result:
        await sse.publish(
            {"event": "transaction_ingested", "txn_id": txn.txn_id, "customer_id": txn.customer_id},
            type="transaction"
        )

    return result

# -------------------------
# CSV ingestion endpoint with performance logging
# -------------------------
@router.post("/ingest/csv", response_model=List[TransactionRead])
@rate_limit(max_requests=3, window_seconds=60)
async def ingest_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Ingest transactions from uploaded CSV file.
    CSV headers: customer_id, txn_id, merchant, category, amount, currency, mcc, timestamp
    """
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Upload a CSV file.")

    try:
        decoded_file = await file.read()
        decoded_str = decoded_file.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_str))

        records: List[TransactionIngest] = []
        for row in reader:
            try:
                timestamp_str = row.get("timestamp")
                timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None

                record = TransactionIngest(
                    customer_id=row.get("customer_id") or row.get("customerId"),
                    txn_id=row.get("txn_id") or row.get("txnId"),
                    merchant=row.get("merchant"),
                    category=row.get("category"),
                    amount=float(row.get("amount")),
                    currency=row.get("currency") or "USD",
                    mcc=row.get("mcc"),
                    timestamp=timestamp
                )
                records.append(record)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error parsing row: {row}. {str(e)}")

        start = time.perf_counter()
        result = await TransactionService.ingest_transactions(db, records)
        end = time.perf_counter()
        duration_ms = (end - start) * 1000
        print(f"[Performance] POST /ingest/csv {len(records)} records: {duration_ms:.2f} ms")

        # SSE broadcast for each ingested transaction
        for txn in result:
            await sse.publish(
                {"event": "transaction_ingested", "txn_id": txn.txn_id, "customer_id": txn.customer_id},
                type="transaction"
            )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV file: {str(e)}")

# -------------------------
# SSE Stream Endpoint
# -------------------------
# Example generator function that yields SSE messages
async def event_generator():
    while True:
        # Example: generate a fake transaction
        txn = {
            "id": "txn_" + str(int(time.time() * 1000)),
            "customer_id": "cust_123",
            "amount": 100,
            "timestamp": time.time()
        }

        # SSE format: data: <json>\n\n
        yield f"data: {json.dumps(txn)}\n\n"

        await asyncio.sleep(2)  # send every 2 seconds

@router.get("/stream")
async def transaction_stream():
    """
    SSE endpoint for live transactions.
    """
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "Connection": "keep-alive",
    }
    return StreamingResponse(event_generator(), headers=headers)