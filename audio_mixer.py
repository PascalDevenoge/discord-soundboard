from multiprocessing import Queue
from threading import Event
import queue
import numpy as np
from typing import Tuple, List
from command import *
from track_manager import TrackManager, FRAME_LENGTH
from uuid import UUID

NUM_CHANNELS = 20

_channels : List[Tuple[bool, UUID, int]] = [(False, None, 0)] * NUM_CHANNELS

def _pick_channel():
  longest_played_channel = 0
  longest_played_frame_num = 0
  for i, (active, _, next_frame) in enumerate(_channels):
    if next_frame > longest_played_frame_num:
      longest_played_frame_num = next_frame
      longest_played_channel = i
    if not active:
      return i
  return longest_played_channel
    
def audio_mixer_thread_main(shutdown_event : Event, command_queue : queue.Queue, audio_queue : Queue, track_manager : TrackManager):
  while True:
    if shutdown_event.is_set():
      print("Audio mixer shutdown")
      return
    
    while True:
      try:
        cmd : Command = command_queue.get_nowait()
        match cmd.type:
          case CommandType.RUN_SAMPLE:
            _channels[_pick_channel()] = (True, cmd.id, 0)
          case CommandType.RUN_ALL:
            for uuid, channel_id in zip(track_manager.get_track_ids(), range(len(_channels))):
              _channels[channel_id] = (True, uuid, 0)
          case CommandType.STOP_ALL:
            for i in range(len(_channels)):
              _channels[i] = (False, None, 0)
      except queue.Empty:
        break

    mixed_frame = np.zeros(FRAME_LENGTH, dtype=np.float32)

    for i, (active, uuid, next_frame) in enumerate(_channels):
      if not active:
        continue
        
      if next_frame >= track_manager.get_track_length(uuid):
        _channels[i] = (False, None, 0)
        continue

      mixed_frame += track_manager.get_track_frame(uuid, next_frame)
      _channels[i] = (_channels[i][0], _channels[i][1], _channels[i][2] + 1)

    finished_frame = mixed_frame.astype(np.int16)

    try:
      audio_queue.put(np.dstack((finished_frame, finished_frame)).flatten().tobytes(), timeout=1)
    except queue.Full:
      pass