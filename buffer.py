from stream import ByteSource
from queue import Queue
from threading import Lock
from time import sleep
from stream_listener import StreamListener

# a simple FIFO buffer for ensuring stream stability
class Buffer(ByteSource):

  def __init__(self, upstream, size=200000):
    self.fifo = Queue()
    self.targetSize = size
    self.size = 0
    self.quit = False
    self.mutex = Lock()
    self.listener = StreamListener(upstream, self)
    self.listener.start()

  def stop(self):
    self.quit = True
    self.listener.stop()

  def peek(self):
    self.mutex.acquire()
    try:
      if self.size > 0 and not self.quit:
        return self.fifo.queue[0]
      else:
        return None
    finally:
      self.mutex.release()

  def read(self):
    self.mutex.acquire()
    try:
      if self.size > 0 and not self.quit:
        out = self.fifo.get_nowait()
        self.size -= len(out)
        return out
      else:
        return None
    finally:
      self.mutex.release()

  def write(self, chunk):
    while not self.quit:
      try:
        self.mutex.acquire()
        if self.size < self.targetSize:
          self.size += len(chunk)
          self.fifo.put(chunk)
          break
      finally:
        self.mutex.release()
      sleep(0.1)