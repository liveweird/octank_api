"""load a bunch of users

Revision ID: fc29a021e8aa
Revises: 029eafb0a7c4
Create Date: 2021-03-06 20:27:27.803741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc29a021e8aa'
down_revision = '029eafb0a7c4'
branch_labels = None
depends_on = None


def upgrade():
    user = sa.table('user',
        sa.Column('user', sa.String(64), primary_key=True),
        sa.Column('gender', sa.Integer, nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('state', sa.String(16), nullable=False)
    )

    op.bulk_insert(
        user,
        [
            {'user': 'Ana-0-20-MZ', 'gender': 0, 'age': 20, 'state': 'MZ'},
            {'user': 'Bob-1-30-SW', 'gender': 1, 'age': 30, 'state': 'SW'},
            {'user': 'Chloe-0-40-MP', 'gender': 0, 'age': 40, 'state': 'MP'},
            {'user': 'Don-1-50-WP', 'gender': 1, 'age': 50, 'state': 'WP'},
            {'user': 'Eve-0-25-SW', 'gender': 0, 'age': 25, 'state': 'SW'},
            {'user': 'Flynn-1-35-MP', 'gender': 1, 'age': 35, 'state': 'MP'},
            {'user': 'Gina-0-45-MZ', 'gender': 0, 'age': 45, 'state': 'MZ'},
            {'user': 'Hugo-1-15-MZ', 'gender': 1, 'age': 15, 'state': 'MZ'}
        ]
    )


def downgrade():
    pass
