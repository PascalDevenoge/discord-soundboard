from sqlalchemy import Engine, create_engine, Uuid, String, BLOB, select, exists
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from pydub import AudioSegment

import uuid

from dataclasses import dataclass


class _Base(DeclarativeBase):
    pass


class _TrackModel(_Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    samples: Mapped[bytes]
    sample_depth: Mapped[int]
    sample_rate: Mapped[int]
    num_channels: Mapped[int]


@dataclass
class Track():
    id: uuid.UUID
    name: str
    samples: AudioSegment


@dataclass
class TrackInfo():
    id: uuid.UUID
    name: str


def init() -> Engine:
    engine = create_engine("sqlite:///instance/data.db")
    _Base.metadata.create_all(engine)
    return engine


def get_track(session: Session, id: uuid.UUID) -> Track | None:
    result = session.scalar(
        select(_TrackModel).where(_TrackModel.id == id))
    if result is None:
        return None

    audio = AudioSegment(result.samples, sample_width=result.sample_depth,
                         frame_rate=result.sample_rate, channels=result.num_channels)
    return Track(result.id, result.name, audio)


def get_all_tracks(session: Session) -> list[Track]:
    result = session.scalars(select(_TrackModel)).all()
    tracks : list[Track] = []
    for row in result:
        tracks.append(Track(
            row.id,
            row.name,
            AudioSegment(
                row.samples,
                sample_width=row.sample_depth,
                frame_rate=row.sample_rate,
                channels=row.num_channels
            )
        ))
    return tracks


def get_all_track_info(session: Session) -> list[TrackInfo]:
    track_infos: list[TrackInfo] = []
    results = session.scalars(select(_TrackModel))
    for track in results:
        track_infos.append(TrackInfo(track.id, track.name))
    return track_infos


def save_track(session: Session, track: Track):
    new_track = _TrackModel(
        id=track.id,
        name=track.name,
        samples=track.samples.raw_data,
        sample_depth=track.samples.sample_width,
        sample_rate=track.samples.frame_rate,
        num_channels=track.samples.channels
    )
    session.add(new_track)
    session.commit()

def track_exists(session: Session, id: uuid.UUID) -> bool:
    return session.query(exists().where(_TrackModel.id == id)).scalar()