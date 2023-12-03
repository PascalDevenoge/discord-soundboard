from flask import Flask, Response, send_file
from threading import Thread
import queue
import command

app = Flask(__name__)
app_thread = None
command_queue : queue.Queue = None
response_queue : queue.Queue = None

def run_flask_app(cmd_queue : queue.Queue, rspns_queue : queue.Queue):
  global command_queue
  global response_queue
  command_queue = cmd_queue
  response_queue = rspns_queue
  app_thread = Thread(
    target=lambda: app.run(debug=True, use_reloader=False)
  )
  app_thread.start()

@app.route('/')
def root_page():
  return send_file('./static/index.html', mimetype='text/html')

@app.route("/play/<int:track_id>")
def play_sample(track_id):
  command_queue.put(command.RunSampleCommand(track_id))
  return Response('', 204)

@app.route("/tracks")
def get_tracks():
  command_queue.put(command.GetTracksCommand())
  tracks = response_queue.get()
  return {id: name for id, name in enumerate(tracks)}