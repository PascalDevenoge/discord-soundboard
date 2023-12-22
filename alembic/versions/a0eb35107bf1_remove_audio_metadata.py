"""Remove audio metadata

Revision ID: a0eb35107bf1
Revises:
Create Date: 2023-12-22 14:32:50.297321

"""
from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0eb35107bf1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('tracks', 'sample_depth')
    op.drop_column('tracks', 'sample_rate')
    op.drop_column('tracks', 'num_channels')


def downgrade() -> None:
    op.add_column('tracks', sa.Column(
        'sample_depth', sa.Integer, server_default='2'))
    op.add_column('tracks', sa.Column(
        'sample_rate', sa.Integer, server_default='48000'))
    op.add_column('tracks', sa.Column(
        'num_channels', sa.Integer, server_default='2'))
