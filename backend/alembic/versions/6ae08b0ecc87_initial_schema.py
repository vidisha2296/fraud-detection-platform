"""Initial schema

Revision ID: 6ae08b0ecc87
Revises: 
Create Date: 2025-09-06 18:46:30.781984

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '6ae08b0ecc87'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Safely drop old indexes if they exist ---
    for table_name, idx_name in [('actions', 'ix_actions_txn_id'),
                                 ('fraud_alerts', 'ix_fraud_alerts_txn_id')]:
        indexes = inspector.get_indexes(table_name)
        if any(idx['name'] == idx_name for idx in indexes):
            op.drop_index(idx_name, table_name=table_name)

    # --- Create foreign keys if not exist ---
    for table_name, fk_name, ref_table, cols, ref_cols in [
        ('actions', 'fk_actions_txn_id', 'transactions', ['txn_id'], ['txn_id']),
        ('fraud_alerts', 'fk_fraud_alerts_txn_id', 'transactions', ['txn_id'], ['txn_id'])
    ]:
        fks = inspector.get_foreign_keys(table_name)
        if not any(fk['name'] == fk_name for fk in fks):
            op.create_foreign_key(fk_name, table_name, ref_table, cols, ref_cols)

    # --- Drop old non-unique index on transactions if exists ---
    indexes = inspector.get_indexes('transactions')
    if any(idx['name'] == 'ix_transactions_txn_id' for idx in indexes):
        op.drop_index('ix_transactions_txn_id', table_name='transactions')

    # --- Create unique index on transactions.txn_id ---
    if not any(idx['name'] == 'ix_transactions_txn_id' for idx in inspector.get_indexes('transactions')):
        op.create_index(
            'ix_transactions_txn_id',
            'transactions',
            ['txn_id'],
            unique=True
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # --- Drop unique index if exists and recreate old index ---
    indexes = inspector.get_indexes('transactions')
    if any(idx['name'] == 'ix_transactions_txn_id' and idx['unique'] for idx in indexes):
        op.drop_index('ix_transactions_txn_id', table_name='transactions')

    if not any(idx['name'] == 'ix_transactions_txn_id' for idx in inspector.get_indexes('transactions')):
        op.create_index('ix_transactions_txn_id', 'transactions', ['txn_id'], unique=False)

    # --- Drop foreign keys safely ---
    for table_name, fk_name in [('fraud_alerts', 'fk_fraud_alerts_txn_id'),
                                ('actions', 'fk_actions_txn_id')]:
        fks = inspector.get_foreign_keys(table_name)
        if any(fk['name'] == fk_name for fk in fks):
            op.drop_constraint(fk_name, table_name, type_='foreignkey')

    # --- Recreate old non-unique indexes safely ---
    for table_name, idx_name in [('fraud_alerts', 'ix_fraud_alerts_txn_id'),
                                 ('actions', 'ix_actions_txn_id')]:
        indexes = inspector.get_indexes(table_name)
        if not any(idx['name'] == idx_name for idx in indexes):
            op.create_index(idx_name, table_name, ['txn_id'], unique=False)
