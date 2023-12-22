"""Add clip length data to db

Revision ID: 684d8895d567
Revises: a0eb35107bf1
Create Date: 2023-12-22 14:46:50.914673

"""
from typing import Sequence
from typing import Union
import uuid

from alembic import op
import pydub
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision: str = '684d8895d567'
down_revision: Union[str, None] = 'a0eb35107bf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


Base = declarative_base()


class TrackModel(Base):
    __tablename__ = "tracks"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True, default=uuid.uuid4)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    samples: orm.Mapped[bytes]
    clip_length: orm.Mapped[float]


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.add_column('tracks', sa.Column('clip_length', sa.Float,
                  nullable=False, server_default='0.0'))

    for track in session.query(TrackModel):
        audio = pydub.AudioSegment(
            track.samples, sample_width=2, frame_rate=48000, channels=2)
        track.clip_length = audio.duration_seconds

    session.commit()
    session.close()


def downgrade() -> None:
    op.drop_column('tracks', 'clip_length')
