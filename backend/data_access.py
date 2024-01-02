from dataclasses import dataclass
import uuid

from pydub import AudioSegment
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import event
from sqlalchemy import exists
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


class ClipUsedException(Exception):
    def __init__(self, sequence_id) -> None:
        super().__init__(f'Clip still used in sequence {sequence_id}')
        self.sequence_id = sequence_id


class NameDuplicateException(Exception):
    pass


class ClipDoesNotExistException(Exception):
    def __init__(self, clip_id):
        super().__init__(f'Clip {clip_id} does not exist')
        self.clip_id = clip_id


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


@dataclass
class Clip():
    id: uuid.UUID
    name: str
    length: int
    volume: float
    samples: AudioSegment


@dataclass
class ClipInfo():
    id: uuid.UUID
    name: str
    length: int
    volume: float


@dataclass
class SequenceStep():
    position: int
    delay: int
    volume: float
    clip_id: uuid.UUID


@dataclass
class Sequence():
    id: uuid.UUID
    name: str
    length: int
    steps: list[SequenceStep]


@dataclass
class GlobalSettings():
    play_all_count: int
    play_join_clip: bool
    join_clip_is_sequence: bool
    join_clip_id: uuid.UUID | None
    target_channel_name: str


def init() -> Engine:
    engine = create_engine("sqlite:///instance/data.db")

    @event.listens_for(engine, 'connect')
    def foreign_key_pragma_on_connect_callback(connection, _):
        connection.execute('pragma foreign_keys=ON')

    _Base.metadata.create_all(engine)
    return engine


def get_clip(session: Session, id: uuid.UUID) -> Clip | None:
    clip_model = session.scalar(select(_ClipModel).where(_ClipModel.id == id))
    if clip_model is None:
        return None

    samples = AudioSegment(
        clip_model.samples,
        sample_width=2,
        frame_rate=48000,
        channels=2
    )

    return Clip(
        id,
        clip_model.name,
        clip_model.length,
        clip_model.volume,
        samples
    )


def get_all_clips(session: Session) -> list[Clip]:
    results = session.scalars(select(_ClipModel))
    clips = []
    for clip_model in results:
        samples = AudioSegment(
            clip_model.samples,
            sample_width=2,
            frame_rate=48000,
            channels=2
        )

        clips.append(
            Clip(
                clip_model.id,
                clip_model.name,
                clip_model.length,
                clip_model.volume,
                samples
            )
        )

    return clips


def get_clip_info(session: Session, id: uuid.UUID) -> ClipInfo | None:
    result = session.execute(select(_ClipModel.id, _ClipModel.name,
                             _ClipModel.length, _ClipModel.volume).where(_ClipModel.id == id)).first()
    if result is None:
        return False
    return ClipInfo(result.id, result.name, result.length, result.volume)


def get_all_clip_infos(session: Session) -> list[ClipInfo]:
    results = session.execute(select(
        _ClipModel.id, _ClipModel.name, _ClipModel.length, _ClipModel.volume)).all()
    clip_infos = []
    for row in results:
        clip_infos.append(
            ClipInfo(
                row.id,
                row.name,
                row.length,
                row.volume
            )
        )

    return clip_infos


def save_clip(session: Session, clip: Clip) -> None:
    if session.query(exists(_ClipModel).where(_ClipModel.name == clip.name)).scalar():
        raise NameDuplicateException()

    clip_model = _ClipModel(
        id=clip.id,
        name=clip.name,
        length=clip.length,
        volume=clip.volume,
        samples=clip.samples.raw_data
    )
    session.add(clip_model)
    session.commit()


def clip_exists(session: Session, id: uuid.UUID) -> bool:
    return session.query(exists(_ClipModel).where(_ClipModel.id == id)).scalar


def delete_clip(session: Session, id: uuid.UUID) -> None:
    clip_to_delete = session.scalar(
        select(_ClipModel).where(_ClipModel.id == id))
    if clip_to_delete is None:
        return False

    still_used = session.query(exists(_SequenceStepModel).where(
        _SequenceStepModel.clip == clip_to_delete)).scalar()
    if still_used:
        raise ClipUsedException(id)

    session.delete(clip_to_delete)
    session.commit()
    return True


def update_clip_info(session: Session, info: ClipInfo) -> bool:
    clip_to_update = session.scalar(
        select(_ClipModel).where(_ClipModel.id == id))
    if clip_to_update is None:
        return False

    clip_to_update.name = info.name
    clip_to_update.volume = info.volume
    session.commit()
    return True


def get_sequence(session: Session, id: uuid.UUID) -> Sequence | None:
    sequence_model = session.scalar(
        select(_SequenceModel).where(_SequenceModel.id == id))
    if sequence_model is None:
        return None

    return Sequence(
        sequence_model.id,
        sequence_model.name,
        sequence_model.length,
        [SequenceStep(
            step_model.position,
            step_model.delay,
            step_model.volume,
            step_model.clip_id
        ) for step_model in sequence_model.steps]
    )


def save_sequence(session: Session, sequence: Sequence) -> None:
    if session.query(exists(_SequenceModel).where(_SequenceModel.name == sequence.name)).scalar():
        raise NameDuplicateException()

    new_sequence_model = _SequenceModel(
        id=sequence.id,
        name=sequence.name,
        length=sequence.length,
    )
    for step in sequence.steps:
        clip_model = session.scalar(
            select(_ClipModel).where(_ClipModel.id == step.clip_id))
        if clip_model is None:
            raise ClipDoesNotExistException(step.clip_id)
        new_sequence_model.steps.append(
            _SequenceStepModel(
                position=step.position,
                delay=step.delay,
                volume=step.volume,
                clip=clip_model
            )
        )

    session.add(new_sequence_model)
    session.commit()


def delete_sequence(session: Session, id: uuid.UUID) -> bool:
    sequence_to_delete = session.scalar(
        select(_SequenceModel).where(_SequenceModel.id == id))
    if sequence_to_delete is None:
        return False

    session.delete(sequence_to_delete)
    session.commit()
    return True


def sequence_exists(session: Session, id: int) -> bool:
    return session.query(exists(_SequenceModel).where(_SequenceModel.id == id)).scalar()


def get_all_sequences(session: Session) -> list[Sequence]:
    sequence_models = session.scalars(select(_SequenceModel))
    sequences = []
    for sequence_model in sequence_models:
        sequences.append(
            Sequence(
                sequence_model.id,
                sequence_model.name,
                sequence_model.length,
                [
                    SequenceStep(
                        step_model.position,
                        step_model.delay,
                        step_model.volume,
                        step_model.clip_id
                    ) for step_model in sequence_model.steps
                ]
            )
        )


def get_global_settings(session: Session) -> GlobalSettings:
    settings_model = session.scalar(select(_GlobalSettingsModel))
    if settings_model is None:
        return GlobalSettings(
            -1,
            False,
            False,
            None,
            ''
        )

    return GlobalSettings(
        settings_model.play_all_count,
        settings_model.play_join_clip,
        settings_model.join_clip_is_sequence,
        settings_model.join_clip_id,
        settings_model.target_channel_name
    )


def save_global_settings(session: Session, settings: GlobalSettings) -> None:
    settings_model = session.scalar(select(_GlobalSettingsModel))
    if settings_model is None:
        settings_model = _GlobalSettingsModel(
            play_all_count=settings.play_all_count,
            play_join_clip=settings.play_join_clip,
            join_clip_is_sequence=settings.join_clip_is_sequence,
            join_clip_id=settings.join_clip_id,
            target_channel_name=settings.target_channel_name
        )
        session.add(settings_model)
    else:
        settings_model.play_all_count = settings.play_all_count
        settings_model.play_join_clip = settings.play_join_clip
        settings_model.join_clip_is_sequence = settings.join_clip_is_sequence
        settings_model.join_clip_id = settings.join_clip_id
        settings_model.target_channel_name = settings.target_channel_name
    session.commit()
