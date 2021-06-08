from threading import Thread, main_thread
from util import non_block_read, non_block_peek
from time import sleep

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
        if not self.stream is None:
          output = non_block_read(self.stream)
          if output == None or output == b'':
            if not self.backupStream is None:
              output = non_block_read(self.backupStream)
              if output == None or output == b'':
                break
            else:
              break
          self.listener.write(output)
      sleep(0.1)