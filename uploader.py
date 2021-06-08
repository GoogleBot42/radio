import ffmpeg
from logger import logger
import sys
from stream_listener import StreamListener
import nullsrc

class Uploader(object):

  def __init__(self, host, stream):
    self.host = host
    self.stream = stream
    self.connect()

  def connect(self):
    self.process = ( ffmpeg
      .input('pipe:', re=None)
      .output("icecast://source:hackme@" + self.host + "/" + self.stream, format='mp3', content_type="audio/mpeg")
      .run_async(pipe_stdin=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "uploader.log")
    self.listener = StreamListener(None, self, backupUpstream=nullsrc.NullSrc())
    self.listener.start()
  
  def reconnect(self):
    self.process.stdin.close()
    self.process.wait()
    self.connect()

  def setUpstream(self, upstream):
    self.listener.setUpstream(upstream)

  def stop(self):
    self.listener.stop()
    self.process.stdin.close()
    self.process.stderr.close()
    self.process.wait()

  def write(self, chunk):
    while True:
      try:
        self.process.stdin.write(chunk)
        break
      except:
        print("Unexpected error:", sys.exc_info())
        self.reconnect()