from threading import Thread, main_thread
from util import non_block_read, non_block_peek
from time import sleep, time
from stream import toByteSource

# time (ms) to wait before switching over to backup source 
FALLBACK_TIME = 100

def current_milli_time():
  return round(time() * 1000)

#
# In a new thread, listens for new data on the stream
# and passes it to the listener when available
#
# Upstreams implement class StreamSource or ByteSource
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
    self.src = toByteSource(upstream)

  def setBackupUpstream(self, upstream):
    self.backupSrc = toByteSource(upstream)

  def setDownstream(self, downstream):
    self.listener = downstream

  # blocks until there is nothing left to read from upstream
  def blockUntilEmpty(self):
    if not self.src is None:
      while True:
        output = self.src.peek()
        if output == None:
          break
        sleep(0.1)

  def stop(self):
    self.quit = True

  def run(self):
    while main_thread().is_alive() and not self.quit:
      while True:
        output = None
        if not self.src is None:
          output = self.src.read()
        if output == None and not self.backupSrc is None and current_milli_time() - self.lastData > FALLBACK_TIME:
          output = self.backupSrc.read()
        else:
          self.lastData = current_milli_time()
        if output == None:
          break
        self.listener.write(output)
      sleep(0.1)