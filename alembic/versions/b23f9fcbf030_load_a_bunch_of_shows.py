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
            {'show': 'Avatar-AU-1-1', 'origin': 'Austria', 'genre': 1, 'pgrating': '1'},
            {'show': 'Breaking Bad-BR-2-2', 'origin': 'Brasil', 'genre': 2, 'pgrating': '2'},
            {'show': 'Chernobyl-CH-3-3', 'origin': 'Chile', 'genre': 3, 'pgrating': '3'},
            {'show': 'Dracula-DE-1-4', 'origin': 'Denmark', 'genre': 1, 'pgrating': '4'},
            {'show': 'Exorcist-AU-1-5', 'origin': 'Austria', 'genre': 1, 'pgrating': '5'},
            {'show': 'Family Guy-BR-2-1', 'origin': 'Brasil', 'genre': 2, 'pgrating': '1'},
            {'show': 'Goonies-CH-2-1', 'origin': 'Chile', 'genre': 2, 'pgrating': '1'},
            {'show': 'Home Alone-DE-1-2', 'origin': 'Denmark', 'genre': 1, 'pgrating': '2'}
        ]
    )


def downgrade():
    pass
