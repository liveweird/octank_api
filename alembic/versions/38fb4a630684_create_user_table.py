"""create user table

Revision ID: 38fb4a630684
Revises: 
Create Date: 2021-03-06 19:56:42.450625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38fb4a630684'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('user', sa.String(64), primary_key=True),
        sa.Column('gender', sa.Integer, nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('state', sa.String(16), nullable=False)
    )


def downgrade():
    op.drop_table('user')
