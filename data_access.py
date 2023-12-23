from dataclasses import dataclass
import uuid

from pydub import AudioSegment
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import exists
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


class _Base(DeclarativeBase):
    pass


class _TrackModel(_Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    samples: Mapped[bytes]
    clip_length: Mapped[float]


class _SequenceModel(_Base):
    __tablename__ = "sequences"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    steps: Mapped[list["_SequenceStepModel"]
                  ] = relationship(cascade='all, delete')


class _SequenceStepModel(_Base):
    __tablename__ = "sequence_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_id: Mapped[int] = mapped_column(ForeignKey("sequences.id"))
    step_num: Mapped[int]
    volume: Mapped[float]
    clip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tracks.id"))
    delay: Mapped[int]


@dataclass
class Track():
    id: uuid.UUID
    name: str
    samples: AudioSegment
    length: float


@dataclass
class TrackInfo():
    id: uuid.UUID
    name: str
    length: float


@dataclass
class SequenceStep():
    id: int
    num: int
    clip_id: uuid.UUID
    volume: float
    delay: int


@dataclass
class Sequence():
    id: int
    name: str
    steps: list[SequenceStep]


def init() -> Engine:
    engine = create_engine("sqlite:///instance/data.db")
    _Base.metadata.create_all(engine)
    return engine


def get_track(session: Session, id: uuid.UUID) -> Track | None:
    result = session.scalar(
        select(_TrackModel).where(_TrackModel.id == id))
    if result is None:
        return None

    audio = AudioSegment(result.samples, sample_width=2,
                         frame_rate=48000, channels=2)
    return Track(result.id, result.name, audio, result.clip_length)


def get_all_tracks(session: Session) -> list[Track]:
    result = session.scalars(select(_TrackModel)).all()
    tracks: list[Track] = []
    for row in result:
        tracks.append(Track(
            row.id,
            row.name,
            AudioSegment(
                row.samples,
                sample_width=2,
                frame_rate=48000,
                channels=2
            ),
            row.clip_length
        ))
    return tracks


def get_all_track_info(session: Session) -> list[TrackInfo]:
    track_infos: list[TrackInfo] = []
    results = session.scalars(select(_TrackModel))
    for track in results:
        track_infos.append(TrackInfo(track.id, track.name, track.clip_length))
    return track_infos


def save_track(session: Session, track: Track):
    new_track = _TrackModel(
        id=track.id,
        name=track.name,
        samples=track.samples.raw_data,
        clip_length=track.samples.duration_seconds
    )
    session.add(new_track)
    session.commit()


def track_exists(session: Session, id: uuid.UUID) -> bool:
    return session.query(exists().where(_TrackModel.id == id)).scalar()


def delete_track(session: Session, id: uuid.UUID) -> bool:
    track_to_delete = session.scalar(
        select(_TrackModel).where(_TrackModel.id == id))
    if track_to_delete is None:
        return False

    session.delete(track_to_delete)
    session.commit()
    return True


def update_track_name(session: Session, id: uuid.UUID, new_name: str) -> bool:
    track_to_rename = session.scalar(
        select(_TrackModel).where(_TrackModel.id == id))
    if track_to_rename is None:
        return False

    track_to_rename.name = new_name
    session.commit()
    return True


def get_sequence(session: Session, id: int) -> Sequence | None:
    sequence_model = session.scalar(
        select(_SequenceModel).where(_SequenceModel.id == id))
    if sequence_model is None:
        return None

    return Sequence(
        sequence_model.id,
        sequence_model.name,
        [SequenceStep(step_model.id, step_model.step_num, step_model.clip_id,
                      step_model.volume, step_model.delay) for step_model in sequence_model.steps]
    )


def save_sequence(session: Session, sequence: Sequence) -> int:
    new_sequence = _SequenceModel(
        name=sequence.name
    )

    for step in sequence.steps:
        new_sequence.steps.append(
            _SequenceStepModel(
                step_num=step.num,
                volume=step.volume,
                clip_id=step.clip_id,
                delay=step.delay
            )
        )

    session.add(new_sequence)
    session.flush()
    new_sequence_key = new_sequence.id
    session.commit()
    return new_sequence_key


def delete_sequence(session: Session, id: int) -> bool:
    sequence_to_delete = session.scalar(
        select(_SequenceModel).where(_SequenceModel.id == id))
    if sequence_to_delete is None:
        return False

    session.delete(sequence_to_delete)
    session.commit()
    return True


def sequence_exists(session: Session, id: int) -> bool:
    return session.query(exists().where(_SequenceModel.id == id)).scalar()


def get_all_sequences(session: Session) -> list[Sequence]:
    sequence_models = session.scalars(_SequenceModel).all()
    sequences = []
    for sequence_model in sequence_models:
        sequences.append(
            Sequence(
                sequence_model.id,
                sequence_model.name,
                [SequenceStep(step_model.id, step_model.step_num, step_model.clip_id,
                              step_model.volume, step_model.delay) for step_model in sequence_model.steps]
            )
        )
    return sequences
