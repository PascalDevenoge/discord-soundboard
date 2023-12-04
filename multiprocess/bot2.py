import discord
from discord.ext import tasks
from multiprocessing import Process, Event
from multiprocessing.connection import Connection

def bot_process_main(shutdown_event : Event, 
                  audio_stream : Connection, 
                  api_token : str, 
                  voice_channel_name : str):
  SoundboardBotClient(
    shutdown_event, 
    audio_stream, 
    voice_channel_name
  ).run(api_token)

class SoundboardBotClient(discord.Client):
  def __init__(self, shutdown_event : Event, audio_stream : Connection, voice_channel_name : str):
    self.shutdown_event = shutdown_event
    self.audio_stream = audio_stream
    self.voice_channel_name = voice_channel_name
    self.audio_client = None

    super().__init__(intents=discord.Intents.default())

  async def on_ready(self):
    print("Bot starting up")

    target_channels = [ch for ch in self.get_all_channels() if ch.name == self.voice_channel_name]
    if len(target_channels) != 1:
      print(f'Unexpected number of channels with name {self.voice_channel_name} found')
    if len(target_channels == 0):
      raise RuntimeError()
    selected_channel = target_channels[0]
    print(f'Selected channel with id {selected_channel.id}')

    self.audio_client = await selected_channel.connect()
    self.audio_client.play(SoundboardStreamAudioSource())

  @tasks.loop(seconds=5)
  async def shutdown_task(self):
    if self.shutdown_event.is_set():
      if self.audio_client:
        self.audio_client.disconnect()
      raise KeyboardInterrupt # Trigger shutdown of the bot

class SoundboardStreamAudioSource(discord.AudioSource):
  def __init__(self, audio_stream : Connection):
    self.audio_stream = audio_stream

  def read(self) -> bytes:
    return self.audio_stream.recv_bytes()