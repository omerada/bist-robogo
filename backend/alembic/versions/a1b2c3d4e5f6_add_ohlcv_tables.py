"""add_ohlcv_tables

Revision ID: a1b2c3d4e5f6
Revises: 622228031e14
Create Date: 2026-03-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '622228031e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Günlük OHLCV tablosu
    op.create_table(
        'ohlcv_1d',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('open', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('high', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('low', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('close', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False, server_default='0'),
    )
    op.create_index('ix_ohlcv_1d_symbol_time', 'ohlcv_1d', ['symbol', 'time'], unique=True)
    op.create_index('ix_ohlcv_1d_time', 'ohlcv_1d', ['time'])

    # Dakikalık OHLCV tablosu
    op.create_table(
        'ohlcv_1m',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('open', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('high', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('low', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('close', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False, server_default='0'),
    )
    op.create_index('ix_ohlcv_1m_symbol_time', 'ohlcv_1m', ['symbol', 'time'], unique=True)
    op.create_index('ix_ohlcv_1m_time', 'ohlcv_1m', ['time'])

    # TimescaleDB hypertable'a dönüştür (extension varsa)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                PERFORM create_hypertable('ohlcv_1d', 'time', if_not_exists => TRUE);
                PERFORM create_hypertable('ohlcv_1m', 'time', if_not_exists => TRUE);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_index('ix_ohlcv_1m_time', table_name='ohlcv_1m')
    op.drop_index('ix_ohlcv_1m_symbol_time', table_name='ohlcv_1m')
    op.drop_table('ohlcv_1m')
    op.drop_index('ix_ohlcv_1d_time', table_name='ohlcv_1d')
    op.drop_index('ix_ohlcv_1d_symbol_time', table_name='ohlcv_1d')
    op.drop_table('ohlcv_1d')
