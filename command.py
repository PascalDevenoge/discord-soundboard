from abc import ABC
from enum import Enum
from uuid import UUID

class CommandType(Enum):
  PLAY_SAMPLE = 1,
  GET_TRACKS = 2,
  PLAY_ALL = 3,
  STOP_ALL = 4,

class Command(ABC):
  def __init__(self, command_type : CommandType):
    self.type = command_type

class RunSampleCommand(Command):
  def __init__(self, id : UUID, volume : float):
    super().__init__(CommandType.PLAY_SAMPLE)
    self.id = id
    self.volume = volume

class GetTracksCommand(Command):
  def __init__(self):
    super().__init__(CommandType.GET_TRACKS)

class RunAllCommand(Command):
  def __init__(self):
    super().__init__(CommandType.PLAY_ALL)

class StopAllCommand(Command):
  def __init__(self):
    super().__init__(CommandType.STOP_ALL)