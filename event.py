from abc import ABC
from enum import Enum
from uuid import UUID


class EventType(Enum):
    PLAY_CLIP = 1,
    PLAY_ALL = 2,
    STOP_ALL = 3,

class Event(ABC):
    def __init__(self, event_type : EventType) -> None:
        self.type = event_type

class PlayClipEvent(Event):
    def __init__(self, id : UUID, volume : float) -> None:
        super().__init__(EventType.PLAY_CLIP)
        self.id = id
        self.volume = volume

class PlayAllClipsEvent(Event):
    def __init__(self) -> None:
        super().__init__(EventType.PLAY_ALL)

class StopAllEvent(Event):
    def __init__(self) -> None:
        super().__init__(EventType.STOP_ALL)