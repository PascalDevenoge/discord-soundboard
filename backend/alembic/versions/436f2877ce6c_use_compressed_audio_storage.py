"""Use compressed audio storage

Revision ID: 436f2877ce6c
Revises: 6b54e519c17c
Create Date: 2024-01-02 17:36:16.120696

"""
from io import BytesIO
from typing import Sequence
from typing import Union
import uuid

from alembic import op
from pydub import AudioSegment
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = '436f2877ce6c'
down_revision: Union[str, None] = '6b54e519c17c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class _Base(DeclarativeBase):
    pass


class _ClipModel(_Base):
    __tablename__ = "clips"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    length: Mapped[int]
    volume: Mapped[float]
    samples: Mapped[bytes]
    icon: Mapped[bytes] = mapped_column(nullable=True)


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    for clip in session.scalars(sa.select(_ClipModel)):
        compressed = AudioSegment(
            clip.samples, frame_rate=48000, channels=2, sample_width=2)
        byte_stream = BytesIO()
        compressed.export(byte_stream, format='ogg',
                          codec='libopus', bitrate='160k')
        clip.samples = byte_stream.getvalue()

    session.commit()
    session.close()
    with op.get_context().autocommit_block():
        op.execute(sa.text("VACUUM"))


def downgrade() -> None:
    session = Session(bind=op.get_bind())

    for clip in session.scalars(sa.select(_ClipModel)):
        audio = AudioSegment.from_file(
            BytesIO(clip.samples), format='ogg', codec='libopus')
        clip.samples = audio.raw_data

    session.commit()
    session.close()
