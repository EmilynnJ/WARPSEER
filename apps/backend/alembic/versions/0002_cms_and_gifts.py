from alembic import op
import sqlalchemy as sa

revision = '0002_cms_and_gifts'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('cms_pages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(length=120), unique=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False, server_default=''),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table('gifts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=512), nullable=False, server_default=''),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )

def downgrade():
    op.drop_table('gifts')
    op.drop_table('cms_pages')