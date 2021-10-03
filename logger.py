import sys
from subprocess import PIPE, Popen
from threading import Thread, main_thread, Lock
from queue import Queue, Empty
from time import sleep
from pathlib import Path
from util import non_block_read

READ_SIZE = 8096
LOG_DIR = "logs/"

class Logger(Thread):

  def __init__(self):
    Thread.__init__(self)
    self.streams = dict()
    self.files = dict()
    self.mutex = Lock()
    Path(LOG_DIR).mkdir(exist_ok=True)

  def add(self, stream, filename):
    self.mutex.acquire()
    try:
      if not filename in self.files.keys():
        self.files[filename] = open(LOG_DIR + filename, "ab")
      self.streams[filename] = stream
    finally:
      self.mutex.release()

  def run(self):
    while main_thread().is_alive():
      self.mutex.acquire()
      try:
        for filename, stream in self.streams.items():
          f = self.files[filename]
          while True:
            output = non_block_read(stream)
            if output == None or output == b'':
              break
            f.write(output)
            f.flush()
            print(output.decode('utf-8'))
      finally:
        self.mutex.release()
      sleep(0.1)


logger = Logger()
logger.start()
