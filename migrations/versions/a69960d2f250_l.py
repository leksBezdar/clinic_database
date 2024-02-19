"""l

Revision ID: a69960d2f250
Revises: d08364452d3a
Create Date: 2024-02-13 17:59:17.033714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a69960d2f250'
down_revision: Union[str, None] = 'd08364452d3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('refresh_tokens', sa.Column('expires_in', sa.Integer(), nullable=False))
    op.drop_column('refresh_tokens', 'expires_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('refresh_tokens', sa.Column('expires_at', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('refresh_tokens', 'expires_in')
    # ### end Alembic commands ###