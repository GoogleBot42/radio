import downloader
import ffmpeg
import sys
from logger import logger

def run():
  process = ( ffmpeg
    .input('pipe:', re=None)
    .output("icecast://source:hackme@localhost:8000/stream.mp3", format='mp3', content_type="audio/mpeg")
    .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
  )

  logger.add(process.stdout, "ffmpeg.out.log")
  logger.add(process.stderr, "ffmpeg.err.log")

  def cb(chunk):
    process.stdin.write(chunk)
    return False

  downloader.download('https://www.youtube.com/watch?v=BaW_jenozKc', cb)
  downloader.download('https://www.youtube.com/watch?v=EbnH3VHzhu8', cb)
  # downloader.download('https://www.youtube.com/watch?v=kgBcg4uBd9Q', cb)
  # downloader.download('https://www.youtube.com/watch?v=EbnH3VHzhu8', cb)

if __name__ == "__main__":
  run()