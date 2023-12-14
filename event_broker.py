import threading
import multiprocessing
import multiprocessing.connection

import event

import logging

log = logging.getLogger('event-broker')

def event_broker_main(shutdown_event: multiprocessing.Event):
    connection_list: list[multiprocessing.connection.Connection] = []
    connection_list_lock = threading.Lock()

    log.info('Starting up')
    listener_thread = threading.Thread(
        target=connection_listener_main, name='Connection listener', args=[shutdown_event, connection_list, connection_list_lock], daemon=True
    )
    listener_thread.start()

    while not shutdown_event.is_set():
        with connection_list_lock:
            for c_in in multiprocessing.connection.wait(connection_list, timeout=0):
                try:
                    e : event.Event = c_in.recv()
                    for c_out in connection_list:
                        c_out.send(e)
                except (EOFError, BrokenPipeError, ConnectionResetError, ConnectionError):
                    log.info(f'Connection with fileno: {c_in.fileno()} closed')
                    c_in.close()
                    connection_list.remove(c_in)

    log.info('Shutting down')

def connection_listener_main(shutdown_event: multiprocessing.Event, connection_list: list[multiprocessing.connection.Connection], connection_list_lock: threading.Lock):
    log.info('Starting up')
    listener = multiprocessing.connection.Listener('discord-soundboard/event-broker')
    while not shutdown_event.is_set():
        connection = listener.accept()
        log.info(f'Connection opened with fileno: {connection.fileno()}')
        with connection_list_lock:
            connection_list.append(connection)
    listener.close()
    log.info('Shutting down')
