"""BidFeedback added

Revision ID: 7e6fc8bff9d8
Revises: b45b651cf307
Create Date: 2024-09-13 19:52:10.294811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e6fc8bff9d8'
down_revision: Union[str, None] = 'b45b651cf307'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bid_feedback',
    sa.Column('id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('bidId', sa.UUID(), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('createdAt', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['bidId'], ['bid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bid_feedback')
    # ### end Alembic commands ###
