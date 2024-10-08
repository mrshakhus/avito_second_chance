"""Added new tables: Bid and BidOldVersion

Revision ID: 868233671b52
Revises: 73f0b0681649
Create Date: 2024-09-12 22:28:23.262989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '868233671b52'
down_revision: Union[str, None] = '73f0b0681649'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bid',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('status', postgresql.ENUM('Created', 'Published', 'Canceled', name='bid_status'), nullable=False),
    sa.Column('tenderId', sa.UUID(), nullable=False),
    sa.Column('authorType', postgresql.ENUM('Organization', 'User', name='author_type'), nullable=False),
    sa.Column('authorId', sa.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('createdAt', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['authorId'], ['employee.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenderId'], ['tender.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid_old_version',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('bidName', sa.String(length=100), nullable=False),
    sa.Column('bidDescription', sa.String(length=500), nullable=False),
    sa.Column('bidId', sa.UUID(), nullable=False),
    sa.Column('bidVersion', sa.Integer(), nullable=False),
    sa.Column('createdAt', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['bidId'], ['bid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bid_old_version')
    op.drop_table('bid')
    op.execute("DROP TYPE IF EXISTS bid_status")
    op.execute("DROP TYPE IF EXISTS author_type")
    # ### end Alembic commands ###
