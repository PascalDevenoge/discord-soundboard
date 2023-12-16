import multiprocessing
import multiprocessing.managers
import threading
import queue

from abc import ABC
from enum import Enum
from uuid import UUID

import logging

log = logging.getLogger('Event manager')

class EventManager(multiprocessing.managers.BaseManager):
    pass

def event_manager_main():
    log.info('Starting up')
    manager = EventManager(address='discord-soundboard/event-manager')

    listener_queues: list[queue.Queue] = []
    lock = threading.Lock()

    def subscribe() -> queue.Queue:
        log.info('Subscriber added')
        q = queue.Queue()
        with lock:
            listener_queues.append(q)
        return q

    def unsubscribe(q: queue.Queue) -> None:
        with lock:
            listener_queues.remove(q)

    def signal(event: Event) -> None:
        with lock:
            for queue in listener_queues:
                queue.put(event)

    EventManager.register('subscribe', subscribe)
    EventManager.register('unsubscribe', unsubscribe)
    EventManager.register('signal', signal)
    log.info('Ready')
    manager.get_server().serve_forever()


def get_event_manager() -> EventManager:
    manager = EventManager(address='discord-soundboard/event-manager')
    EventManager.register('subscribe')
    EventManager.register('unsubscribe')
    EventManager.register('signal')
    manager.connect()
    return manager


class EventType(Enum):
    PLAY_CLIP = 1,
    PLAY_ALL = 2,
    STOP_ALL = 3,


class Event(ABC):
    def __init__(self, event_type: EventType) -> None:
        self.type = event_type


class PlayClipEvent(Event):
    def __init__(self, id: UUID, volume: float) -> None:
        super().__init__(EventType.PLAY_CLIP)
        self.id = id
        self.volume = volume


class PlayAllClipsEvent(Event):
    def __init__(self) -> None:
        super().__init__(EventType.PLAY_ALL)


class StopAllEvent(Event):
    def __init__(self) -> None:
        super().__init__(EventType.STOP_ALL)
