from flask import Flask, Response, send_file
from threading import Thread, Event
import queue
import command
from flask_apscheduler import APScheduler

app = Flask(__name__)
app_thread = None
scheduler = APScheduler()
command_queue : queue.Queue = None
response_queue : queue.Queue = None
shutdown_event : Event

def executor():
  global scheduler
  global app
  scheduler.init_app(app)
  scheduler.start()
  app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5123)

def run_flask_app(cmd_queue : queue.Queue, rspns_queue : queue.Queue, shutdown_ev : Event):
  global command_queue
  global response_queue
  global shutdown_event
  command_queue = cmd_queue
  response_queue = rspns_queue
  shutdown_event = shutdown_ev
  app_thread = Thread(
    target=executor
  )
  app_thread.start()
  return app_thread

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

@app.route("/play/all")
def play_all():
  command_queue.put(command.RunAllCommand())
  return Response('', 204)

@app.route("/stop")
def stop_tracks():
  command_queue.put(command.StopAllCommand())
  return Response('', 204)

# @scheduler.task('interval', id='shutdown_task', seconds=5)
# def shutdown_task():
#     if shutdown_event.is_set():
#       print('Shutting down flask')
#       scheduler.shutdown()
#       raise KeyboardInterrupt
