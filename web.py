from queue import Queue
from flask import Flask, Response, send_file
from command import *
from track_manager import TrackManager
from uuid import UUID

def start_web_app(command_queue : Queue, track_manager : TrackManager):
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

  app.run(host='0.0.0.0', port=5123)