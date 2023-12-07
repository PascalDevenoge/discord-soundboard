import threading
import atexit
import time

e = threading.Event()

def thread_main():
  while not e.is_set():
    print("Thread")
    time.sleep(1)
  print("Stopping")

thread = threading.Thread(target=thread_main, daemon=True)
thread.start()

@atexit.register
def cleanup():
  e.set()
  thread.join()
  print("Thread stoped")

while True:
  print("Main")
  time.sleep(0.5)