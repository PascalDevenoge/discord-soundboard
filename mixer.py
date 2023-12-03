import discord
import queue
import command
import numpy as np

from typing import List

FRAME_LENGTH = int(48000 * 0.02)

class SoundboardTrack():
  def __init__(self, name, samples : np.ndarray) -> None:
    assert samples.dtype == np.int16

    num_pad_samples = FRAME_LENGTH - (samples.shape[0] % FRAME_LENGTH)

    padded_samples = np.pad(samples, (0, num_pad_samples), constant_values=0)

    assert padded_samples.shape[0] % FRAME_LENGTH == 0

    self.num_frames = int(padded_samples.shape[0] / FRAME_LENGTH)
    self.samples = np.reshape(padded_samples, (self.num_frames, FRAME_LENGTH))
    self.next_frame = 0
    self.active = False
    self.name = name

  def read_frame(self):
    assert self.next_frame <= self.num_frames and self.active
    
    frame = self.samples[self.next_frame]
    self.next_frame += 1

    if self.next_frame == self.num_frames:
      self.active = False

    return frame

  def play(self):
    self.active = True
    self.next_frame = 0

class SoundboardMixer():
  def __init__(self, command_queue : queue.Queue, response_queue : queue.Queue):
    self.audio_source = None
    self.tracks : List[SoundboardTrack] = []
    self.command_queue = command_queue
    self.response_queue = response_queue

  def registerTrack(self, track : SoundboardTrack):
    self.tracks.append(track)

  def readFrame(self):
    while True:
      try:
        cmd : command.Command = self.command_queue.get_nowait()
        match cmd.type:
          case command.CommandType.RUN_SAMPLE:
            id = cmd.id
            self.tracks[id].play()
          case command.CommandType.GET_TRACKS:
            track_names = [track.name for track in self.tracks]
            print(len(track_names))
            self.response_queue.put(track_names)
          case _:
            print('Unknown command received')
      except queue.Empty as _:
        break

    mixed_frame = np.zeros(FRAME_LENGTH, dtype=np.int16)
    
    for track in self.tracks:
      if (track.active):
        track_frame = track.read_frame()
        mixed_frame = mixed_frame + track_frame

    return np.dstack((mixed_frame, mixed_frame)).flatten()
  
  def play_track(self, track_index):
    self.tracks[track_index].play()

  def get_audio_source(self):
    return SoundboardAudioSource(self)
      

class SoundboardAudioSource(discord.AudioSource):
  def __init__(self, mixer : SoundboardMixer):
    self.mixer = mixer

  def read(self):
    return self.mixer.readFrame().tobytes()