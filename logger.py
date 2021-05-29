import sys
import fcntl
import os
from subprocess import PIPE, Popen
from threading  import Thread, main_thread
from queue import Queue, Empty
from time import sleep
from pathlib import Path

READ_SIZE = 8096
LOG_DIR = "logs/"

def non_block_read(output):
  fd = output.fileno()
  fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
  try:
    return output.read()
  except:
    return b''

class Logger(Thread):

  def __init__(self):
    Thread.__init__(self)
    self.streams = dict()
    self.files = dict()
    Path(LOG_DIR).mkdir(exist_ok=True)

  def add(self, stream, filename):
    self.files[filename] = open(LOG_DIR + filename, "wb")
    self.streams[filename] = stream

  def run(self):
    while main_thread().is_alive():
      for filename, stream in self.streams.items():
        f = self.files[filename]
        while True:
          output = non_block_read(stream)
          if output == None or output == b'':
            break
          print(output.decode('ascii'))
          f.write(output)
          f.flush()
      sleep(0.1)


logger = Logger()
logger.start()
