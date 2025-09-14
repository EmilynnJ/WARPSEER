from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('clerk_user_id', sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(length=255), nullable=False, index=True),
        sa.Column('role', sa.String(length=16), nullable=False, server_default='client'),
        sa.Column('display_name', sa.String(length=120), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table('reader_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('bio', sa.Text(), nullable=False, server_default=''),
        sa.Column('avatar_url', sa.String(length=512), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='offline'),
        sa.Column('rate_chat_ppm', sa.Integer(), nullable=False, server_default='199'),
        sa.Column('rate_voice_ppm', sa.Integer(), nullable=False, server_default='299'),
        sa.Column('rate_video_ppm', sa.Integer(), nullable=False, server_default='399'),
        sa.Column('rate_scheduled_15', sa.Integer(), nullable=False, server_default='3000'),
        sa.Column('rate_scheduled_30', sa.Integer(), nullable=False, server_default='6000'),
        sa.Column('rate_scheduled_45', sa.Integer(), nullable=False, server_default='9000'),
        sa.Column('rate_scheduled_60', sa.Integer(), nullable=False, server_default='12000'),
    )

    op.create_table('wallets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('balance_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table('ledger_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('kind', sa.String(length=24), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('ref_type', sa.String(length=32), nullable=False),
        sa.Column('ref_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table('sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_uid', sa.String(length=64), nullable=False, unique=True),
        sa.Column('reader_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('mode', sa.String(length=16), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='requested'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('total_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('amount_charged_cents', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table('messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('sessions.id', ondelete='CASCADE'), index=True),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table('appointments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('booking_uid', sa.String(length=64), nullable=False, unique=True),
        sa.Column('reader_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('length_minutes', sa.Integer(), nullable=False),
        sa.Column('mode', sa.String(length=16), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='scheduled'),
    )

    op.create_table('stripe_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('account_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('details_submitted', sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('stripe_product_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('kind', sa.String(length=16), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table('orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_uid', sa.String(length=64), nullable=False, unique=True),
        sa.Column('buyer_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('total_cents', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='created'),
    )


def downgrade():
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('stripe_accounts')
    op.drop_table('appointments')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_table('ledger_entries')
    op.drop_table('wallets')
    op.drop_table('reader_profiles')
    op.drop_table('users')