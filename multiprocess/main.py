import os
import argparse
import tomllib
import bot2
from multiprocessing import Event, Pipe, Process

def main():
  api_token, voice_channel_name = load_config()

  (audio_stream, remote_connection) = Pipe()
  bot_shutdown_event = Event()

  bot_process : Process = Process(
    target=bot2.bot_process_main, 
    args=[bot_shutdown_event, audio_stream, api_token, voice_channel_name]
  ).start()

  bot_shutdown_event.set() # Signal bot process to shutdown
  bot_process.join()

def load_config():
  api_token = os.getenv('DISCORD_SBRD_TOKEN')
  if api_token == None:
    raise RuntimeError("No discord API token set")
  
  argument_parser = argparse.ArgumentParser()
  argument_parser.add_argument("config_file", help="Path to the configuration file", type=argparse.FileType(mode="rb"))
  arguments = argument_parser.parse_args()
  configuration = tomllib.load(arguments.config_file)
  arguments.config_file.close()

  return (api_token, configuration["voice-channel-name"])

if __name__ == "__main__":
  main()