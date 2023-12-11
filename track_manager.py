from threading import Lock
from uuid import UUID
import numpy as np
import pathlib
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_leading_silence

from typing import Dict, Tuple, List

FRAME_LENGTH = int(48000 * 0.02)
ALLOWED_FILE_TYPES = ['flac', 'mp4', 'mp3', 'ogg']

class TrackManager():
  def __init__(self, audio_dir_path : str) -> None:
    self.lock = Lock()
    self.tracks : Dict[UUID, Tuple[str, int, np.ndarray]] = {}
    self.audio_dir_path = audio_dir_path

    for file_type in ALLOWED_FILE_TYPES:
      files_to_load = pathlib.Path(audio_dir_path).glob(f"*.{file_type}")
      for file_path in files_to_load:
        print(file_path)
        samples : AudioSegment = AudioSegment.from_file(file_path)
        processed_samples = samples.set_channels(1).set_sample_width(2).set_frame_rate(48000)

        trim_leading = lambda x: x[detect_leading_silence(x) : ]
        trim_end = lambda x: trim_leading(x.reverse()).reverse()

        trimmed_samples = trim_leading(trim_end(processed_samples))

        trimmed_samples = normalize(trimmed_samples, 15.0)
        audio = np.array(trimmed_samples.get_array_of_samples(), dtype=np.int16).T

        file_name = file_path.name
        uuid = UUID(file_name[0 : 36])
        track_name = file_name[36 : -5]
        self.add_track(uuid, track_name, audio)

  def add_track(self, uuid, name, samples) -> None:
    num_pad_samples = FRAME_LENGTH - (samples.shape[0] % FRAME_LENGTH)
    padded_samples = np.pad(samples, (0, num_pad_samples), constant_values=0.)
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