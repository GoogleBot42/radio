import ffmpeg
from logger import logger
from stream_listener import StreamListener
from stream import StreamSource
import os

fifoFile = 'transcode-fifo'

# converts the stream to mp3 before sending to the long-lasting mp3 connection
# write to a fifo file instead of directly via stdin to fool ffmpeg into thinking it has seekable input
# https://lists.libav.org/pipermail/ffmpeg-user/2007-May/008917.html
class Transcoder(StreamSource):

  def __init__(self, upstream):
    if os.path.exists(fifoFile):
      os.remove(fifoFile)
    os.mkfifo(fifoFile)
    self.file = open(fifoFile, 'w+b')
    self.process = ( ffmpeg
      .input(fifoFile)
      .output('pipe:', format='mp3')
      .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "transcoder.log")
    self.listener = StreamListener(upstream, self)
    self.listener.start()

  def stop(self):
    self.file.close()
    self.listener.stop()
    self.process.stdout.close()
    self.process.stderr.close()
    os.remove(fifoFile)

  def getStream(self):
    return self.process.stdout

  def write(self, chunk):
    self.file.write(chunk)