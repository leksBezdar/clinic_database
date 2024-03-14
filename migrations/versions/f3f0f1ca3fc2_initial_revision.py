"""Initial revision

Revision ID: f3f0f1ca3fc2
Revises: 
Create Date: 2024-03-07 12:33:52.081312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3f0f1ca3fc2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patients',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('birthday', sa.String(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('living_place', sa.String(), nullable=True),
    sa.Column('job_title', sa.String(), nullable=True),
    sa.Column('inhabited_locality', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('role', sa.String(), server_default='explorer', nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hashed_password'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('patient_records',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('diagnosis', sa.String(), nullable=True),
    sa.Column('first_visit', sa.String(), nullable=True),
    sa.Column('last_visit', sa.String(), nullable=True),
    sa.Column('treatment', sa.String(), nullable=True),
    sa.Column('bp', sa.String(), nullable=False),
    sa.Column('ischemia', sa.String(), nullable=False),
    sa.Column('dep', sa.String(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('therapist_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['therapist_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_records_id'), 'patient_records', ['id'], unique=False)
    op.create_table('refresh_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('refresh_token', sa.UUID(), nullable=False),
    sa.Column('expires_in', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_refresh_token'), 'refresh_tokens', ['refresh_token'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_refresh_tokens_refresh_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index(op.f('ix_patient_records_id'), table_name='patient_records')
    op.drop_table('patient_records')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_table('patients')
    # ### end Alembic commands ###