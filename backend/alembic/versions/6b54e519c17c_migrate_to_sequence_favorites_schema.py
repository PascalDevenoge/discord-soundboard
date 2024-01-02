"""Migrate to sequence / favorites schema

Revision ID: 6b54e519c17c
Revises: e8415dc2cf88
Create Date: 2024-01-02 15:51:46.932130

"""
from math import ceil
from typing import Sequence
from typing import Union
import uuid

from alembic import op
from pydub import AudioSegment
import sqlalchemy as sa
from sqlalchemy import Column
from sqlalchemy import exists
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import Table
import sqlalchemy.orm as orm
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


# revision identifiers, used by Alembic.
revision: str = '6b54e519c17c'
down_revision: Union[str, None] = 'e8415dc2cf88'
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


class _SequenceStepModel(_Base):
    __tablename__ = "sequence_steps"

    position: Mapped[int]
    delay: Mapped[int]
    volume: Mapped[float]
    clip: Mapped[_ClipModel] = relationship()
    sequence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sequences.id"), primary_key=True)
    clip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clips.id"), primary_key=True)


class _SequenceModel(_Base):
    __tablename__ = "sequences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    length: Mapped[int]
    icon: Mapped[bytes] = mapped_column(nullable=True)
    steps: Mapped[list[_SequenceStepModel]
                  ] = relationship(cascade='all, delete')


favorite_clips_table = Table(
    "favorite_clips",
    _Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("clip_id", ForeignKey("clips.id"), primary_key=True),
)

favorite_sequence_table = Table(
    "favorite_sequences",
    _Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("sequence_id", ForeignKey("sequences.id"), primary_key=True)
)


class _UsersModel(_Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    favorite_clips: Mapped[list[_ClipModel]] = relationship(
        secondary=favorite_clips_table)
    favorite_sequences: Mapped[list[_SequenceModel]] = relationship(
        secondary=favorite_sequence_table)


class _GlobalSettingsModel(_Base):
    __tablename__ = "global_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    play_all_count: Mapped[int]
    play_join_clip: Mapped[bool]
    join_clip_is_sequence: Mapped[bool]
    join_clip_id: Mapped[uuid.UUID] = mapped_column(nullable=True)
    target_channel_name: Mapped[str]


class _TrackModelOld(_Base):
    __tablename__ = "tracks_old"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True, default=uuid.uuid4)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    samples: orm.Mapped[bytes]
    clip_length: orm.Mapped[float]


class _SequenceModelOld(_Base):
    __tablename__ = "sequences_old"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    steps: orm.Mapped[list["_SequenceStepModelOld"]] = orm.relationship()


class _SequenceStepModelOld(_Base):
    __tablename__ = "sequence_steps_old"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    sequence_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("sequences_old.id"))
    step_num: orm.Mapped[int]
    volume: orm.Mapped[float]
    clip_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.ForeignKey("tracks_old.id"))
    delay: orm.Mapped[int]


def upgrade() -> None:
    session = orm.Session(bind=op.get_bind())

    op.rename_table('tracks', 'tracks_old')
    op.rename_table('sequences', 'sequences_old')
    op.rename_table('sequence_steps', 'sequence_steps_old')

    _Base.metadata.create_all(bind=op.get_bind())

    tracks = session.scalars(select(_TrackModelOld))
    for track in tracks:
        if session.query(exists(_ClipModel).where(_ClipModel.name == track.name)).scalar():
            print(f'Dropping clip {track.name}')
            continue

        audio = AudioSegment(
            track.samples,
            sample_width=2,
            frame_rate=48000,
            channels=2
        )

        clip = _ClipModel(
            id=track.id,
            name=track.name,
            length=ceil(1000 * audio.duration_seconds),
            volume=0.0,
            samples=track.samples,
            icon=None
        )

        session.add(clip)

    for sequence in session.scalars(select(_SequenceModelOld)):
        if session.query(exists(_SequenceModel).where(_SequenceModel.name == sequence.name)).scalar():
            print(f'Dropping sequence {sequence.name}')
            continue

        new_sequence = _SequenceModel(
            id=uuid.uuid4(),
            name=sequence.name,
            icon=None
        )

        length = 0
        steps = []

        for step in sequence.steps:
            track = session.scalar(select(_TrackModelOld).where(
                _TrackModelOld.id == step.clip_id))
            step_end = step.delay + track.clip_length
            if length < step_end:
                length = step_end
            steps.append(_SequenceStepModel(
                position=step.step_num,
                delay=step.delay,
                volume=step.volume,
                clip=session.scalar(select(_ClipModel).where(
                    _ClipModel.id == step.clip_id))
            ))

        new_sequence.length = length
        new_sequence.steps = steps
        session.add(new_sequence)

    op.drop_table('tracks_old')
    op.drop_table('sequences_old')
    op.drop_table('sequence_steps_old')

    settings = _GlobalSettingsModel(
        play_all_count=-1,
        play_join_clip=True,
        join_clip_is_sequence=False,
        join_clip_id=uuid.UUID('acd6229e-3485-4c1a-ab30-b964a39acbd0'),
        target_channel_name='The Lounge'
    )
    session.add(settings)

    session.commit()
    session.close()


def downgrade() -> None:
    _Base.metadata.drop_all(bind=op.get_bind())

    op.rename_table('tracks_old', 'tracks')
    op.rename_table('sequences_old', 'sequences')
    op.rename_table('sequence_steps_old', 'sequence_steps')
