import pydub
import sqlalchemy.orm
import data_access
from pathlib import Path

import uuid

pathlist = Path('../data/tracks').glob('*')

engine = data_access.init()

with sqlalchemy.orm.Session(engine) as session:
  for path in pathlist:
    id = uuid.UUID(str(path)[15:51])
    name = str(path)[51:-5]
    audio = pydub.AudioSegment.from_file(path).set_frame_rate(48000).set_sample_width(2).set_channels(2)
    track = data_access.Track(id, name, audio)
    data_access.save_track(session, track)