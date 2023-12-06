from queue import Queue
from flask import Flask, Response, send_file, request, redirect
from command import *
from track_manager import TrackManager
from uuid import UUID, uuid4
import os
import librosa
import pathlib

def start_web_app(command_queue : Queue, track_manager : TrackManager, audio_dir_path : str):
  app = Flask(__name__)

  @app.route('/')
  def root_page():
    return send_file('./static/index.html', mimetype='text/html')
  
  @app.route('/play/<string:uuid>')
  def play_sample(uuid : str):
    command_queue.put(RunSampleCommand(UUID(uuid)))
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
    audio, _ = librosa.load(filepath, sr=48000, mono=True)
    track_manager.add_track(uuid, file.filename, audio)
    return redirect("/")

  app.run(host='0.0.0.0', port=5123, threaded=True)