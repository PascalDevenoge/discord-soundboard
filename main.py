import os
import argparse
import tomllib
import bot
import audio_mixer
import web
from multiprocessing import Event, Process, Queue
from threading import Thread
import queue
from track_manager import TrackManager
import atexit
import logging
import logger

log = logging.getLogger('main')

def main():
  logger.setup()

  api_token, voice_channel_name, audio_dir_path, num_mixer_channels = load_config()

  track_manager = TrackManager(audio_dir_path)

  audio_queue = Queue(maxsize=5)
  command_queue = queue.Queue()

  audio_mixer_shutdown_event = Event()
  audio_mixer_thread = Thread(
      target=audio_mixer.audio_mixer_thread_main,
      args=[audio_mixer_shutdown_event, command_queue, audio_queue, num_mixer_channels, track_manager],
      daemon=True
  )
  audio_mixer_thread.start()

  bot_shutdown_event = Event()
  bot_process = Process(
    target=bot.bot_process_main, 
    args=[bot_shutdown_event, audio_queue, api_token, voice_channel_name],
    daemon=True
  )
  bot_process.start()

  @atexit.register
  def shutdown_handler():
    bot_shutdown_event.set()
    bot_process.join()
    log.info("Bot shutdown")
    audio_mixer_shutdown_event.set()
    audio_mixer_thread.join()
    log.info("Audio mixer shutdown")

  web.start_web_app(command_queue, track_manager, audio_dir_path)
  log.info("Web app shutdown")

def load_config():
  api_token = os.getenv('DISCORD_SBRD_TOKEN')
  if api_token == None:
    raise RuntimeError("No discord API token set")
  
  argument_parser = argparse.ArgumentParser()
  argument_parser.add_argument("config_file", help="Path to the configuration file", type=argparse.FileType(mode="rb"))
  arguments = argument_parser.parse_args()
  configuration = tomllib.load(arguments.config_file)
  arguments.config_file.close()

  voice_channel_name = configuration["voice-channel-name"]
  samples_files_path = configuration["tracks-path"]
  num_mixer_channels = configuration["num-mixer-channels"]

  log.info("Config loaded:")
  log.info(f"Target voice channel name:      {voice_channel_name}")
  log.info(f"Samples audio file path:        {samples_files_path}")
  log.info(f"Number of audio mixer channels: {num_mixer_channels}")

  return (api_token, voice_channel_name, samples_files_path, num_mixer_channels)

if __name__ == "__main__":
  main()