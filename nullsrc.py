import ffmpeg
from logger import logger
from stream import StreamSource

# A null audio source

class NullSrc(StreamSource):

  def __init__(self):
    self.process = ( ffmpeg
      .input('anullsrc', format='lavfi')
      .output('pipe:', format='opus')
      .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "nullsrc.log")

  def stop(self):
    self.process.stdout.close()
    self.process.stderr.close()

  def getStream(self):
    return self.process.stdout