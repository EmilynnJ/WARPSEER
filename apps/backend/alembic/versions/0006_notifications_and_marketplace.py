from alembic import op
import sqlalchemy as sa

revision = '0006_notifications_and_marketplace'
down_revision = '0005_stream_gifts'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    op.create_table('push_subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', sa.String(length=128), nullable=False, unique=True),
        sa.Column('device_type', sa.String(length=32), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('price_cents', sa.Integer(), nullable=False),
    )
    
    op.create_table('shipping_addresses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address_line1', sa.String(length=255), nullable=False),
        sa.Column('address_line2', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False, server_default='US'),
    )
    
    op.create_table('digital_downloads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('file_url', sa.String(length=512), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('download_limit', sa.Integer(), nullable=False, server_default='0'),
    )
    
    # Add columns to products
    op.add_column('products', sa.Column('description', sa.Text(), nullable=False, server_default=''))
    op.add_column('products', sa.Column('price_cents', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('image_url', sa.String(length=512), nullable=False, server_default=''))
    op.add_column('products', sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='-1'))  # -1 = unlimited
    op.add_column('products', sa.Column('reader_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))

def downgrade():
    op.drop_column('products', 'reader_id')
    op.drop_column('products', 'stock_quantity')
    op.drop_column('products', 'image_url')
    op.drop_column('products', 'price_cents')
    op.drop_column('products', 'description')
    op.drop_table('digital_downloads')
    op.drop_table('shipping_addresses')
    op.drop_table('order_items')
    op.drop_table('push_subscriptions')
    op.drop_table('notifications')