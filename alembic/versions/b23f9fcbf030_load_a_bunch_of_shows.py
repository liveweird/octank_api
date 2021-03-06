"""load a bunch of shows

Revision ID: b23f9fcbf030
Revises: fc29a021e8aa
Create Date: 2021-03-06 21:01:08.243028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23f9fcbf030'
down_revision = 'fc29a021e8aa'
branch_labels = None
depends_on = None


def upgrade():
    show = sa.table('show',
        sa.Column('show', sa.String(64), primary_key=True),
        sa.Column('origin', sa.String(32), nullable=False),
        sa.Column('genre', sa.Integer, nullable=False),
        sa.Column('pgrating', sa.Integer, nullable=False)
    )

    op.bulk_insert(
        show,
        [
            {'show': 'Avatar', 'origin': 'Austria', 'genre': 1, 'pgrating': '1'},
            {'show': 'Breaking Bad', 'origin': 'Brasil', 'genre': 2, 'pgrating': '2'},
            {'show': 'Chernobyl', 'origin': 'Chile', 'genre': 3, 'pgrating': '3'},
            {'show': 'Dracula', 'origin': 'Denmark', 'genre': 1, 'pgrating': '4'},
            {'show': 'Exorcist', 'origin': 'Austria', 'genre': 1, 'pgrating': '5'},
            {'show': 'Family Guy', 'origin': 'Brasil', 'genre': 2, 'pgrating': '1'},
            {'show': 'Goonies', 'origin': 'Chile', 'genre': 2, 'pgrating': '1'},
            {'show': 'Home Alone', 'origin': 'Denmark', 'genre': 1, 'pgrating': '2'}
        ]
    )


def downgrade():
    pass
