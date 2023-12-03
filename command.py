from abc import ABC
from enum import Enum

class CommandType(Enum):
  RUN_SAMPLE = 1,
  GET_TRACKS = 2,

class Command(ABC):
  def __init__(self, command_type : CommandType):
    self.type = command_type

class RunSampleCommand(Command):
  def __init__(self, id):
    super().__init__(CommandType.RUN_SAMPLE)
    self.id = id

class GetTracksCommand(Command):
  def __init__(self):
    super().__init__(CommandType.GET_TRACKS)