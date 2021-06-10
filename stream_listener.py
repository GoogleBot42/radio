from threading import Thread, main_thread
from util import non_block_read, non_block_peek
from time import sleep, time

# time (ms) to wait before switching over to backup source 
FALLBACK_TIME = 500

def current_milli_time():
  return round(time() * 1000)

def empty(output):
  return output == None or output == b''

#
# In a new thread, listens for new data on the stream
# and passes it to the listener when available
#
# Upstreams implement getStream()
# Downstreams implement write() for bytes to be given to
#
class StreamListener(Thread):
  
  def __init__(self, upstream, downstream, backupUpstream=None):
    Thread.__init__(self)
    self.setUpstream(upstream)
    self.setDownstream(downstream)
    self.setBackupUpstream(backupUpstream)
    self.quit = False
    self.lastData = 0

  def setUpstream(self, upstream):
    if not upstream is None:
      self.stream = upstream.getStream()
    else:
      self.stream = None

  def setBackupUpstream(self, upstream):
    if not upstream is None:
      self.backupStream = upstream.getStream()
    else:
      self.backupStream = None

  def setDownstream(self, downstream):
    self.listener = downstream

  # blocks until there is nothing left to read from upstream
  def blockUntilEmpty(self):
    if not self.stream is None:
      while True:
        output = non_block_peek(self.stream)
        if output == None or output == b'':
          break
        sleep(0.1)

  def stop(self):
    self.quit = True

  def run(self):
    while main_thread().is_alive() and not self.quit:
      while True:
        output = None
        if not self.stream is None:
          output = non_block_read(self.stream)
        if empty(output) and not self.backupStream is None and current_milli_time() - self.lastData > FALLBACK_TIME:
          output = non_block_read(self.backupStream)
        else:
          self.lastData = current_milli_time()
        if empty(output):
          break
        self.listener.write(output)
      sleep(0.1)