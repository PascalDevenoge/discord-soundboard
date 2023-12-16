import logger

import server_event
import audio_server

import multiprocessing

import time
import os
import logging


audio_server_shutdown_event = multiprocessing.Event()
audio_server_process : multiprocessing.Process
broker_process : multiprocessing.Process

logger.setup()
log = logging.getLogger('System startup')

def on_starting(server):
  global audio_server_shutdown_event
  global audio_server_process
  global broker_process

  api_token = os.getenv('DISCORD_SBRD_TOKEN')
  if api_token == None:
    log.error("No discord API token set")
    raise RuntimeError()
  
  voice_channel_name = os.getenv('DISCORD_SBRD_TARGET_CHANNEL')
  if voice_channel_name == None:
    log.error("No target voice channel set")
    raise RuntimeError()

  log.info("Starting event broker")
  broker_process = multiprocessing.Process(
    target=server_event.event_manager_main, name='Event Broker'
  )
  broker_process.start()
  time.sleep(1)

  log.info("Starting audio server")
  audio_server_process = multiprocessing.Process(
    target=audio_server.audio_server_main, name='Audio Server', args=[audio_server_shutdown_event, api_token, voice_channel_name]
  )
  audio_server_process.start()

  log.info("Backend ready")

def on_exit(server):
  log.info("Shutting down backend")

  audio_server_shutdown_event.set()
  audio_server_process.join()
  log.info("Audio server quit")
  
  broker_process.join()
  log.info("Event broker quit")


def post_worker_init(worker):
  import atexit
  from multiprocessing.util import _exit_function
  atexit.unregister(_exit_function)
