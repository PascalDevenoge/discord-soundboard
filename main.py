import os
from bot import SoundboardClient
from flask_app import run_flask_app
import queue
import mixer
import numpy as np
import librosa
import argparse
import tomllib

parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="Path to the configuration file", type=argparse.FileType(mode='rb'))
args = parser.parse_args()
config = tomllib.load(args.config_file)
args.config_file.close()

TOKEN = os.getenv('DISCORD_SBRD_TOKEN')
if (TOKEN == None):
  raise RuntimeError('No discord API token set')

command_queue = queue.Queue()
response_queue = queue.Queue()

audio_mixer = mixer.SoundboardMixer(command_queue, response_queue)
for file in [file for file in os.listdir(config['tracks-path']) if file.endswith('.flac')]:
  audio, _ = librosa.load(f'{config["tracks-path"]}/{file}', sr=48000, mono=True)
  audio = (audio * 2000).astype(np.int16)
  audio_mixer.registerTrack(mixer.SoundboardTrack(file, audio))

discord_client = SoundboardClient(audio_mixer)
run_flask_app(command_queue, response_queue)
discord_client.run(TOKEN)
