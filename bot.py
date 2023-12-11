import discord
from discord.ext import tasks
from multiprocessing import Event, Queue
import logging

log = logging.getLogger('discord bot')

def bot_process_main(shutdown_event : Event, 
                  audio_queue : Queue, 
                  api_token : str, 
                  voice_channel_name : str):
  SoundboardBotClient(
    shutdown_event, 
    audio_queue, 
    voice_channel_name
  ).run(api_token, log_handler=None)

class SoundboardBotClient(discord.Client):
  def __init__(self, shutdown_event : Event, audio_queue : Queue, voice_channel_name : str):
    self.shutdown_event = shutdown_event
    self.audio_stream = audio_queue
    self.voice_channel_name = voice_channel_name
    self.voice_channel = None
    self.audio_client = None

    super().__init__(intents=discord.Intents.default())

  async def _join_leave(self):
    if self.audio_client == None or not self.audio_client.is_connected():
      # Not connected to channel
      target_channels = [ch for ch in self.get_all_channels() if ch.type == discord.ChannelType.voice and ch.name == self.voice_channel_name]
      if len(target_channels) == 0:
        # No target channel present
        return
      else:
        # Target channel found
        if len(target_channels) > 1:
          log.warning(f'Unexpected number of channels with name {self.voice_channel_name} found')
        self.voice_channel = target_channels[0]
        if len(self.voice_channel.members) == 0:
          # No members in target voice channel
          return
        else:
          # Activate audio stream
          self.audio_client = await self.voice_channel.connect()
          self.audio_client.play(SoundboardStreamAudioSource(self.audio_stream))
    else:
      # Connected to channel
      if len(self.voice_channel.members) == 1:
        # Alone in channel
        await self.audio_client.disconnect()
      else:
        # Clients connected to channel
        if self.audio_client.is_playing():
          # Stream online
          return
        else:
          # Audio stream is not playing
          self.audio_client.play(SoundboardStreamAudioSource(self.audio_stream))

  async def on_ready(self):
    log.info("Bot starting up")
    await self._join_leave()
    self.stream_replay_task.start()
    self.shutdown_task.start()

  async def on_voice_state_update(self, member, _, __):
    if member == self.user:
      return
    await self._join_leave()

  @tasks.loop(seconds=1)
  async def stream_replay_task(self):
    await self._join_leave()

  @tasks.loop(seconds=1)
  async def shutdown_task(self):
    if self.shutdown_event.is_set():
      raise KeyboardInterrupt

class SoundboardStreamAudioSource(discord.AudioSource):
  def __init__(self, audio_queue : Queue):
    self.audio_queue = audio_queue

  def read(self) -> bytes:
    return self.audio_queue.get()