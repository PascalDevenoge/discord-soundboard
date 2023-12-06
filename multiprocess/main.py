import os
import argparse
import tomllib
import bot2
import audio_mixer
import web
from multiprocessing import Event, Process, Queue
from threading import Thread
import queue
from track_manager import TrackManager

def main():
  api_token, voice_channel_name, audio_dir_path = load_config()

  track_manager = TrackManager(audio_dir_path)

  audio_queue = Queue(maxsize=5)
  command_queue = queue.Queue()

  audio_mixer_shutdown_event = Event()
  audio_mixer_thread = Thread(
      target=audio_mixer.audio_mixer_thread_main,
      args=[audio_mixer_shutdown_event, command_queue, audio_queue, track_manager]
  )
  audio_mixer_thread.start()

  bot_shutdown_event = Event()
  bot_process = Process(
    target=bot2.bot_process_main, 
    args=[bot_shutdown_event, audio_queue, api_token, voice_channel_name]
  )
  bot_process.start()

  web.start_web_app(command_queue)

  bot_shutdown_event.set()
  bot_process.join()

  audio_mixer_shutdown_event.set()
  audio_mixer_thread.join()

def load_config():
  api_token = os.getenv('DISCORD_SBRD_TOKEN')
  if api_token == None:
    raise RuntimeError("No discord API token set")
  
  argument_parser = argparse.ArgumentParser()
  argument_parser.add_argument("config_file", help="Path to the configuration file", type=argparse.FileType(mode="rb"))
  arguments = argument_parser.parse_args()
  configuration = tomllib.load(arguments.config_file)
  arguments.config_file.close()

  return (api_token, configuration["voice-channel-name"], configuration["tracks-path"])

if __name__ == "__main__":
  main()