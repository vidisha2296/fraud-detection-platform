"""Make txn_id + timestamp composite key for FK references

Revision ID: dd76ebab9f55
Revises: 6ae08b0ecc87
Create Date: 2025-09-06 18:57:20.461050
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'dd76ebab9f55'
down_revision: Union[str, None] = '6ae08b0ecc87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Add timestamp columns if they don't exist
    columns_actions = [col['name'] for col in inspector.get_columns('actions')]
    columns_fraud = [col['name'] for col in inspector.get_columns('fraud_alerts')]
    
    if 'timestamp' not in columns_actions:
        op.add_column("actions", sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=True))
    if 'timestamp' not in columns_fraud:
        op.add_column("fraud_alerts", sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=True))
    
    # Get all transaction partitions
    result = conn.execute(sa.text("""
        SELECT inhrelid::regclass AS partition 
        FROM pg_inherits 
        WHERE inhparent = 'transactions'::regclass
    """))
    partition_tables = [row[0] for row in result]

    # Populate timestamp for actions and fraud_alerts from partitions
    for partition in partition_tables:
        op.execute(sa.text(f"""
            UPDATE actions a
            SET timestamp = t.timestamp
            FROM {partition} t
            WHERE a.txn_id = t.txn_id
        """))
        op.execute(sa.text(f"""
            UPDATE fraud_alerts fa
            SET timestamp = t.timestamp
            FROM {partition} t
            WHERE fa.txn_id = t.txn_id
        """))
    
    # Make timestamp columns non-nullable
    op.alter_column("actions", "timestamp", nullable=False)
    op.alter_column("fraud_alerts", "timestamp", nullable=False)
    
    # Drop old txn_id indexes if they exist
    indexes = inspector.get_indexes('transactions')
    if any(idx.get('name') == 'ix_transactions_txn_id' for idx in indexes):
        op.drop_index('ix_transactions_txn_id', table_name='transactions')

    indexes = inspector.get_indexes('actions')
    if any(idx.get('name') == 'ix_actions_txn_id' for idx in indexes):
        op.drop_index('ix_actions_txn_id', table_name='actions')

    indexes = inspector.get_indexes('fraud_alerts')
    if any(idx.get('name') == 'ix_fraud_alerts_txn_id' for idx in indexes):
        op.drop_index('ix_fraud_alerts_txn_id', table_name='fraud_alerts')

    # Create unique constraints for each partition
    for partition in partition_tables:
        op.create_unique_constraint(
            f"uq_{partition}_txn_id_timestamp",
            partition,
            ["txn_id", "timestamp"]
        )
    
    # Create indexes on actions and fraud_alerts
    op.create_index('ix_actions_txn_id_timestamp', 'actions', ['txn_id', 'timestamp'])
    op.create_index('ix_fraud_alerts_txn_id_timestamp', 'fraud_alerts', ['txn_id', 'timestamp'])

    # Create trigger function for FK validation
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION validate_transaction_exists()
        RETURNS TRIGGER AS $$
        DECLARE
            partition_name text;
        BEGIN
            partition_name := 'transactions_' || to_char(NEW.timestamp, 'YYYYMM');
            IF NOT EXISTS (
                SELECT 1 FROM transactions
                WHERE txn_id = NEW.txn_id AND timestamp = NEW.timestamp
            ) THEN
                RAISE EXCEPTION 'Transaction with txn_id % and timestamp % does not exist', NEW.txn_id, NEW.timestamp;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create triggers
    op.execute(sa.text("""
        CREATE TRIGGER validate_action_transaction
        BEFORE INSERT OR UPDATE ON actions
        FOR EACH ROW EXECUTE FUNCTION validate_transaction_exists();
    """))
    
    op.execute(sa.text("""
        CREATE TRIGGER validate_fraud_alert_transaction
        BEFORE INSERT OR UPDATE ON fraud_alerts
        FOR EACH ROW EXECUTE FUNCTION validate_transaction_exists();
    """))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Drop triggers and function
    op.execute(sa.text("DROP TRIGGER IF EXISTS validate_action_transaction ON actions"))
    op.execute(sa.text("DROP TRIGGER IF EXISTS validate_fraud_alert_transaction ON fraud_alerts"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS validate_transaction_exists()"))
    
    # Drop indexes
    indexes = inspector.get_indexes('actions')
    if any(idx.get('name') == 'ix_actions_txn_id_timestamp' for idx in indexes):
        op.drop_index('ix_actions_txn_id_timestamp', table_name='actions')
    
    indexes = inspector.get_indexes('fraud_alerts')
    if any(idx.get('name') == 'ix_fraud_alerts_txn_id_timestamp' for idx in indexes):
        op.drop_index('ix_fraud_alerts_txn_id_timestamp', table_name='fraud_alerts')
    
    # Drop unique constraints from partitions
    result = conn.execute(sa.text("""
        SELECT inhrelid::regclass AS partition 
        FROM pg_inherits 
        WHERE inhparent = 'transactions'::regclass
    """))
    for row in result:
        partition = row[0]
        constraints = inspector.get_unique_constraints(partition)
        constraint_name = f"uq_{partition}_txn_id_timestamp"
        if any(constraint['name'] == constraint_name for constraint in constraints):
            op.drop_constraint(constraint_name, partition, type_="unique")
    
    # Recreate old indexes if missing
    indexes = inspector.get_indexes('transactions')
    if not any(idx.get('name') == 'ix_transactions_txn_id' for idx in indexes):
        op.create_index('ix_transactions_txn_id', 'transactions', ['txn_id'], unique=False)

    indexes = inspector.get_indexes('actions')
    if not any(idx.get('name') == 'ix_actions_txn_id' for idx in indexes):
        op.create_index('ix_actions_txn_id', 'actions', ['txn_id'], unique=False)

    indexes = inspector.get_indexes('fraud_alerts')
    if not any(idx.get('name') == 'ix_fraud_alerts_txn_id' for idx in indexes):
        op.create_index('ix_fraud_alerts_txn_id', 'fraud_alerts', ['txn_id'], unique=False)
    
    # Drop timestamp columns if they exist
    columns_actions = [col['name'] for col in inspector.get_columns('actions')]
    if 'timestamp' in columns_actions:
        op.drop_column("actions", "timestamp")
    
    columns_fraud = [col['name'] for col in inspector.get_columns('fraud_alerts')]
    if 'timestamp' in columns_fraud:
        op.drop_column("fraud_alerts", "timestamp")
