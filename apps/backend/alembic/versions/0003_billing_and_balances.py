from alembic import op
import sqlalchemy as sa

revision = '0003_billing_and_balances'
down_revision = '0002_cms_and_gifts'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('reader_balances',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('balance_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table('reader_ledger_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reader_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('kind', sa.String(length=24), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('ref_type', sa.String(length=32), nullable=False),
        sa.Column('ref_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table('reader_ledger_entries')
    op.drop_table('reader_balances')