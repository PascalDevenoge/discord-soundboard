from abc import ABC
from enum import Enum
import logging
import multiprocessing
import multiprocessing.managers
import queue
import threading
from uuid import UUID


log = logging.getLogger('Event manager')


class EventManager(multiprocessing.managers.BaseManager):
    pass


subscribers: dict[int, queue.Queue] = {}
lock = threading.Lock()
next_id = 0


def event_manager_main():
    log.info('Starting up')
    manager = EventManager(address=("127.0.0.1", 5000))

    class Subscription():
        id: int

        def __init__(self, id) -> None:
            self.id = id

        def get_id(self):
            return self.id

        def listen(self, *, timeout: float):
            global lock
            global subscribers

            q: queue.Queue
            with lock:
                q = subscribers[self.id]
            return q.get(timeout=timeout)

        def unsubscribe(self):
            global lock
            global subscribers

            with lock:
                del subscribers[self.id]
            log.info(f'Removed subscriber with id {self.id}')
            log.info(f'{len(subscribers.keys())} subscribers active')

    def subscribe() -> Subscription:
        global next_id
        global lock
        global subscribers

        id = next_id
        next_id += 1
        q = queue.Queue()
        with lock:
            subscribers[id] = q
        log.info(f'Added subscriber with id {id}')
        log.info(f'{len(subscribers.keys())} subscribers active')
        return Subscription(id)

    def signal(event: Event) -> None:
        global lock
        global subscribers

        with lock:
            for _, queue in subscribers.items():
                queue.put(event)

    EventManager.register('subscribe', subscribe)
    EventManager.register('signal', signal)
    EventManager.register('Subscription', Subscription)
    log.info('Ready')
    manager.get_server().serve_forever()


def get_event_manager() -> EventManager:
    manager = EventManager(address=("127.0.0.1", 5000))
    EventManager.register('subscribe')
    EventManager.register('signal')
    EventManager.register('Subscription')
    manager.connect()
    return manager


class EventType(Enum):
    PLAY_CLIP = 1,
    PLAY_ALL = 2,
    STOP_ALL = 3,
    CLIP_UPLOADED = 4,
    CLIP_DELETED = 5,
    CLIP_UPDATED = 6,
    PLAY_SEQUENCE = 7,
    SEQUENCE_CREATED = 8,
    SEQUENCE_DELETED = 9,
    SEQUENCE_UPDATED = 10,
    STOP_CLIP = 11,


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


class ClipUploadedEvent(Event):
    def __init__(self, id: UUID, name: str, length: float) -> None:
        super().__init__(EventType.CLIP_UPLOADED)
        self.id = id
        self.name = name
        self.length = length


class ClipDeletedEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.CLIP_DELETED)
        self.id = id


class ClipUpdatedEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.CLIP_UPDATED)
        self.id = id


class SequenceCreatedEvent(Event):
    def __init__(self, id: UUID, name: str) -> None:
        super().__init__(EventType.SEQUENCE_CREATED)
        self.id = id
        self.name = name


class SequenceDeletedEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.SEQUENCE_DELETED)
        self.id = id


class PlaySequenceEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.PLAY_SEQUENCE)
        self.id = id


class SequenceUpdatedEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.SEQUENCE_UPDATED)
        self.id = id


class StopClipEvent(Event):
    def __init__(self, id: UUID) -> None:
        super().__init__(EventType.STOP_CLIP)
        self.id = id
