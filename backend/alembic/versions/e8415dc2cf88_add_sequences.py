"""Add sequences

Revision ID: e8415dc2cf88
Revises: 684d8895d567
Create Date: 2023-12-22 22:25:14.240776

"""
from typing import Sequence
from typing import Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision: str = 'e8415dc2cf88'
down_revision: Union[str, None] = '684d8895d567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


Base = declarative_base()


class _TrackModel(Base):
    __tablename__ = "tracks"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True, default=uuid.uuid4)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    samples: orm.Mapped[bytes]
    clip_length: orm.Mapped[float]


class _SequenceModel(Base):
    __tablename__ = "sequences"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(100))
    steps: orm.Mapped[list["_SequenceStepModel"]] = orm.relationship(
        back_populates='_SequenceModel')


class _SequenceStepModel(Base):
    __tablename__ = "sequence_steps"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    sequence_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("sequences.id"))
    step_num: orm.Mapped[int]
    volume: orm.Mapped[float]
    clip_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.ForeignKey("tracks.id"))
    delay: orm.Mapped[int]


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(
        bind=bind, tables=[_SequenceModel.__table__, _SequenceStepModel.__table__])
