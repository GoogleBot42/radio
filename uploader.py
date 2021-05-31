import ffmpeg
from logger import logger
import sys
from stream_listener import StreamListener

class Uploader(object):

  def __init__(self):
    self.connect()

  def connect(self):
    self.process = ( ffmpeg
      .input('pipe:', re=None)
      .output("icecast://source:hackme@localhost:8000/stream.mp3", format='mp3', content_type="audio/mpeg")
      .run_async(pipe_stdin=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "uploader.log")
    self.listener = StreamListener(None, self)
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