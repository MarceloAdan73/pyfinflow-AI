"""initial_schema

Revision ID: 001
Revises:
Create Date: 2026-07-19

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='USER'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )
    op.create_index('ix_users_username', 'users', ['username'])

    op.create_table(
        'transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('monto', sa.Float(), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fecha', sa.String(length=10), nullable=False),
        sa.Column('moneda', sa.String(length=10), nullable=False, server_default='ARS'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_transactions_user_fecha', 'transactions', ['user_id', 'fecha'])
    op.create_index('idx_transactions_user_tipo', 'transactions', ['user_id', 'tipo'])

    op.create_table(
        'budgets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False),
        sa.Column('limite', sa.Float(), nullable=False),
        sa.Column('mes', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'categoria', 'mes', name='uq_budget_user_cat_mes'),
    )

    op.create_table(
        'goals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('objetivo', sa.Float(), nullable=False),
        sa.Column('ahorrado', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('fecha_limite', sa.String(length=10), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'custom_categories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tipo', 'nombre', name='uq_custom_cat'),
    )

    op.create_table(
        'user_configs',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('moneda_activa', sa.String(length=10), nullable=True, server_default='ARS'),
        sa.Column('filtro_fecha_inicio', sa.String(length=10), nullable=True),
        sa.Column('filtro_fecha_fin', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('user_id'),
    )


def downgrade() -> None:
    op.drop_table('user_configs')
    op.drop_table('custom_categories')
    op.drop_table('goals')
    op.drop_table('budgets')
    op.drop_index('idx_transactions_user_tipo', 'transactions')
    op.drop_index('idx_transactions_user_fecha', 'transactions')
    op.drop_table('transactions')
    op.drop_index('ix_users_username', 'users')
    op.drop_table('users')
