"""add_fraud_cases_table

Revision ID: 7f6b9b878efc
Revises: 7cf815b387c2
Create Date: 2024-12-22 04:22:47.368022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f6b9b878efc'
down_revision: Union[str, None] = '7cf815b387c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('merchant_risk_score', sa.Float(), nullable=True))
    op.add_column('transactions', sa.Column('location_risk_score', sa.Float(), nullable=True))
    op.add_column('transactions', sa.Column('amount_risk_score', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transactions', 'amount_risk_score')
    op.drop_column('transactions', 'location_risk_score')
    op.drop_column('transactions', 'merchant_risk_score')
    # ### end Alembic commands ###