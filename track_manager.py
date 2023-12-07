from threading import Lock
from uuid import UUID
import numpy as np
import librosa
import os
import pathlib

from typing import Dict, Tuple, List

FRAME_LENGTH = int(48000 * 0.02)

class TrackManager():
  def __init__(self, audio_dir_path : str) -> None:
    self.lock = Lock()
    self.tracks : Dict[UUID, Tuple[str, int, np.ndarray]] = {}
    self.audio_dir_path = audio_dir_path

    files_to_load = pathlib.Path(audio_dir_path).glob("*.flac")
    for file_path in files_to_load:
      audio, _ = librosa.load(file_path, sr=48000, mono=True)
      file_name = file_path.name
      uuid = UUID(file_name[0 : 36])
      track_name = file_name[36 : -5]
      self.add_track(uuid, track_name, audio)

  def add_track(self, uuid, name, samples) -> None:
    num_pad_samples = FRAME_LENGTH - (samples.shape[0] % FRAME_LENGTH)
    padded_samples = np.pad(samples, (0, num_pad_samples), constant_values=0.) * 5000
    num_frames = int(padded_samples.shape[0] / FRAME_LENGTH)
    frames = np.reshape(padded_samples, (num_frames, FRAME_LENGTH))
    track = (name, num_frames, frames)

    with self.lock:
      self.tracks[uuid] = track

  def get_track_ids(self) -> List[UUID]:
    with self.lock:
      return list(self.tracks.keys())

  def get_track_names(self) -> Dict[UUID, str]:
    track_names = {}
    with self.lock:
      for uuid, (name, _, _) in self.tracks.items():
        track_names[uuid] = name
    return track_names
  
  def get_track_length(self, uuid : UUID) -> int:
    with self.lock:
      return self.tracks[uuid][1]
  
  def get_track_frame(self, uuid : UUID, frame_num : int) -> np.ndarray:
    with self.lock:
      track = self.tracks[uuid]
      if frame_num >= track[1]:
        raise ValueError(f"Frame index {frame_num} out of bounds for track {str(uuid)}: {track[0]}")
      return track[2][frame_num]
    
  def track_exists(self, uuid : UUID) -> bool:
    with self.lock:
      return uuid in self.tracks