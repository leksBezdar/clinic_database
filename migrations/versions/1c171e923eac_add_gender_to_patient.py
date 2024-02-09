"""Add gender to patient

Revision ID: 1c171e923eac
Revises: a00dfcdf969e
Create Date: 2024-02-09 22:34:38.087794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c171e923eac'
down_revision: Union[str, None] = 'a00dfcdf969e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patients', sa.Column('gender', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patients', 'gender')
    # ### end Alembic commands ###
