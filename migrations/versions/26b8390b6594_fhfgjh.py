"""fhfgjh

Revision ID: 26b8390b6594
Revises: c9ab5231c7f3
Create Date: 2024-03-11 16:20:26.001710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26b8390b6594'
down_revision: Union[str, None] = 'c9ab5231c7f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('patient_records', 'visit',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('patient_records', 'ischemia')
    op.drop_column('patient_records', 'dep')
    op.drop_column('patient_records', 'bp')
    op.add_column('patients', sa.Column('bp', sa.String(), nullable=False))
    op.add_column('patients', sa.Column('ischemia', sa.String(), nullable=False))
    op.add_column('patients', sa.Column('dep', sa.String(), nullable=False))
    op.add_column('patients', sa.Column('therapist_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'patients', 'users', ['therapist_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'patients', type_='foreignkey')
    op.drop_column('patients', 'therapist_id')
    op.drop_column('patients', 'dep')
    op.drop_column('patients', 'ischemia')
    op.drop_column('patients', 'bp')
    op.add_column('patient_records', sa.Column('bp', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('patient_records', sa.Column('dep', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('patient_records', sa.Column('ischemia', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.alter_column('patient_records', 'visit',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###