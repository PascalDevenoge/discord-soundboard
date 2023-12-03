import discord
import os
import logging
import mixer

class SoundboardClient(discord.Client):
  def __init__(self, mixer : mixer.SoundboardMixer, config):
    intents = discord.Intents.default()
    intents.message_content = True
    super().__init__(intents=intents)

    self.audio_mixer = mixer

    target_channel_name = config['voice-channel-name']
    if (target_channel_name == None):
      raise RuntimeError('No target voice channel name set')
    self.target_channel_name = target_channel_name

    self.target_voice_channel = None
    self.voice_client = None
    self._update_target_channel()

  def _update_target_channel(self):
    all_channels = self.get_all_channels()
    target_channels = [c for c in all_channels if c.name == self.target_channel_name]

    if len(target_channels) == 0:
      self.target_voice_channel = None
      logging.info(f'No target voice channel currently available')
    else:
      self.target_voice_channel = target_channels[0]
      print(f'Set target voice channel to {self.target_voice_channel.name} : {self.target_voice_channel.id}')

  async def _join_leave_channel(self):
    if self.target_voice_channel == None:
      return
        
    if len(self.target_voice_channel.members) == 1 and self.voice_client != None:
      logging.info('Disconnecting from target channel')
      await self.voice_client.disconnect()
      self.voice_client = None
      return
    
    if len(self.target_voice_channel.members) != 0 and self.voice_client == None:
      logging.info('Joining target channel')
      self.voice_client = await self.target_voice_channel.connect()
      self.voice_client.play(self.audio_mixer.get_audio_source())
      return

  async def on_ready(self):
    print(f'Bot logged in as {self.user}')
    self._update_target_channel()
    await self._join_leave_channel()

  async def on_voice_state_update(self, member, previous, next):
    if member == self.user:
      return

    await self._join_leave_channel()

  async def on_guild_channel_create(self, _):
    self._update_target_channel()

  async def on_guild_channel_delete(self, _):
    self._update_target_channel()
