# app/services/customer_service.py
from sqlalchemy.orm import Session, selectinload
from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerRead
import asyncio

class CustomerService:
    @staticmethod
    async def create_customer(db: Session, customer_data: CustomerCreate) -> CustomerRead:
        """
        Creates a new customer and returns it as CustomerRead schema.
        """
        def _create():
            customer = Customer(**customer_data.dict())
            db.add(customer)
            db.commit()
            db.refresh(customer)
            return CustomerRead.from_orm(customer)

        return await asyncio.to_thread(_create)

    @staticmethod
    async def get_customer(db: Session, customer_id: str) -> CustomerRead | None:
        """
        Fetches a customer by ID, including related transactions, actions, fraud alerts, and insights.
        """
        def _get():
            customer = (
                db.query(Customer)
                .options(
                    selectinload(Customer.transactions),
                    selectinload(Customer.actions),
                    selectinload(Customer.fraud_alerts),
                    selectinload(Customer.insights),
                )
                .filter_by(customer_id=customer_id)
                .first()
            )
            return CustomerRead.from_orm(customer) if customer else None

        return await asyncio.to_thread(_get)
