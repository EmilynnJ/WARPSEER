from alembic import op
import sqlalchemy as sa

revision = '0004_availability_and_session_flags'
down_revision = '0003_billing_and_balances'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('sessions', sa.Column('per_minute', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('sessions', sa.Column('appointment_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_sessions_appointment', 'sessions', 'appointments', ['appointment_id'], ['id'])
    op.create_table('availability_blocks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('reader_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(length=64), nullable=False, server_default='UTC'),
    )


def downgrade():
    op.drop_table('availability_blocks')
    op.drop_constraint('fk_sessions_appointment', 'sessions', type_='foreignkey')
    op.drop_column('sessions', 'appointment_id')
    op.drop_column('sessions', 'per_minute')