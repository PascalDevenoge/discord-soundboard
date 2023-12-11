from queue import Queue
from flask import Flask, Response, send_file, request, redirect
from command import *
from track_manager import TrackManager
from uuid import UUID, uuid4
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import detect_leading_silence
import pathlib

def start_web_app(command_queue : Queue, track_manager : TrackManager, audio_dir_path : str):
  app = Flask(__name__)

  @app.route('/')
  def root_page():
    return send_file('./static/index.html', mimetype='text/html')
  
  @app.route('/play/<string:uuid>/<float(max=15):volume>')
  def play_sample(uuid : str, volume : float):
    id = UUID(uuid)
    if not track_manager.track_exists(id):
      return Response(f'Track {uuid} does not exist', 404)
    
    if volume < 0.0 or volume > 10.0:
      return Response(f'Volume {volume} is out of range', 400)

    command_queue.put(RunSampleCommand(UUID(uuid), volume))
    return Response('', 204)
  
  @app.route('/play/all')
  def play_all_samples():
    command_queue.put(RunAllCommand())
    return Response('', 204)
  
  @app.route('/stop')
  def stop_playback():
    command_queue.put(StopAllCommand())
    return Response('', 204)
  
  @app.route('/tracks')
  def get_tracks():
    return {str(id): name for id, name in track_manager.get_track_names().items()}
  
  @app.route('/upload', methods=['POST'])
  def upload_sample():
    if 'file' not in request.files:
      print('no file')
      return Response('', 400)
    file = request.files['file']
    if file.filename == '':
      print('no filename')
      return Response('', 400)
    
    uuid = uuid4()
    filepath = pathlib.Path(audio_dir_path) / (str(uuid) + file.filename)
    file.save(filepath)

    samples : AudioSegment = AudioSegment.from_file(filepath)
    processed_samples = samples.set_channels(1).set_sample_width(2).set_frame_rate(48000)

    trim_leading = lambda x: x[detect_leading_silence(x) : ]
    trim_end = lambda x: trim_leading(x.reverse()).reverse()

    trimmed_samples = trim_leading(trim_end(processed_samples))

    trimmed_samples = normalize(trimmed_samples, 15.0)
    audio = np.array(trimmed_samples.get_array_of_samples(), dtype=np.int16).T
    
    track_manager.add_track(uuid, file.filename[0 : -5], audio)
    return redirect("/")

  app.run(host='0.0.0.0', port=5123, threaded=True)