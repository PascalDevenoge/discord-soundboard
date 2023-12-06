from queue import Queue
from flask import Flask, Response, send_file
from command import *
from track_manager import TrackManager

def start_web_app(command_queue : Queue, track_manager : TrackManager):
  app = Flask(__name__)

  @app.route('/')
  def root_page():
    return send_file('./static/index.html', mimetype='text/html')
  
  @app.route('/play/<int:track_id>')
  def play_sample(track_id : int):
    command_queue.put(RunSampleCommand(track_id))
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
    return track_manager.get_track_names()

  app.run(host='0.0.0.0', port=5123)