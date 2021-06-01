import ffmpeg
from logger import logger

# A null audio source

class NullSrc(object):

  def __init__(self):
    self.process = ( ffmpeg
      .input('anullsrc', format='lavfi')
      .output('pipe:', format='mp3')
      .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "nullsrc.log")

  def stop(self):
    self.process.stdout.close()
    self.process.stderr.close()
    # self.process.wait()

  def getStream(self):
    return self.process.stdout