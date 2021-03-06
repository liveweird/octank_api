"""create show table

Revision ID: 029eafb0a7c4
Revises: 38fb4a630684
Create Date: 2021-03-06 20:20:08.153086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '029eafb0a7c4'
down_revision = '38fb4a630684'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'show',
        sa.Column('show', sa.String(64), primary_key=True),
        sa.Column('origin', sa.String(32), nullable=False),
        sa.Column('genre', sa.Integer, nullable=False),
        sa.Column('pgrating', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('show')
