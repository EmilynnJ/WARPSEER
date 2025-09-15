"""Update product fields

Revision ID: 20250107_product_fields
Revises: 20250107_notifications
Create Date: 2025-01-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250107_product_fields'
down_revision: Union[str, None] = '20250107_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing fields to products table
    op.add_column('products', sa.Column('description', sa.Text(), server_default='', nullable=False))
    op.add_column('products', sa.Column('price_cents', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('image_url', sa.String(512), server_default='', nullable=False))
    op.add_column('products', sa.Column('stock_quantity', sa.Integer(), server_default='-1', nullable=False))
    op.add_column('products', sa.Column('reader_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_products_reader', 'products', 'users', ['reader_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_products_reader', 'products', type_='foreignkey')
    op.drop_column('products', 'reader_id')
    op.drop_column('products', 'stock_quantity')
    op.drop_column('products', 'image_url')
    op.drop_column('products', 'price_cents')
    op.drop_column('products', 'description')