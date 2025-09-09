# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.services.customer_service import CustomerService
# from app.schemas.customer_schema import CustomerCreate, CustomerRead

# router = APIRouter(prefix="/customers", tags=["Customers"])

# @router.post("/", response_model=CustomerRead)
# def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
#     return CustomerService.create_customer(db, customer.dict())

# @router.get("/{customer_id}", response_model=CustomerRead)
# def get_customer(customer_id: str, db: Session = Depends(get_db)):
#     return CustomerService.get_customer(db, customer_id)


from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer_schema import CustomerCreate, CustomerRead
from app.core.rate_limiter import rate_limit  # Redis rate limiter

router = APIRouter(prefix="", tags=["Customers"])

# -------------------------
# Create a customer
# -------------------------
@router.post("/", response_model=CustomerRead)
@rate_limit(max_requests=5, window_seconds=60)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    return await CustomerService.create_customer(db, customer.dict())


# -------------------------
# Get customer by ID
# -------------------------
@router.get("/{customer_id}", response_model=CustomerRead)
@rate_limit(max_requests=10, window_seconds=60)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    return await CustomerService.get_customer(db, customer_id)
