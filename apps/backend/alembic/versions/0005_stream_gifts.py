from alembic import op
import sqlalchemy as sa

revision = '0005_stream_gifts'
down_revision = '0004_availability_and_session_flags'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('stream_gifts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('gift_id', sa.Integer(), sa.ForeignKey('gifts.id'), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    # Seed some initial gifts
    op.execute("""
        INSERT INTO gifts (name, price_cents, image_url, active) VALUES
        ('Rose', 100, '🌹', true),
        ('Heart', 500, '❤️', true),
        ('Star', 1000, '⭐', true),
        ('Diamond', 2500, '💎', true),
        ('Crown', 5000, '👑', true)
    """)

def downgrade():
    op.drop_table('stream_gifts')