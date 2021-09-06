import ffmpeg
from logger import logger
from stream_listener import StreamListener
from stream import StreamSource

# converts the stream to mp3 before sending to the long-lasting mp3 connection
class Transcoder(StreamSource):

  def __init__(self, upstream):
    self.process = ( ffmpeg
      .input('pipe:')
      .output('pipe:', format='opus', **{'b:a': 96000})
      .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "transcoder.log")
    self.listener = StreamListener(upstream, self)
    self.listener.start()

  def stop(self):
    self.listener.stop()
    self.process.stdin.close()
    self.process.stdout.close()
    self.process.stderr.close()

  def getStream(self):
    return self.process.stdout

  def write(self, chunk):
    self.process.stdin.write(chunk)