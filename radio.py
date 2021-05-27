import downloader
import ffmpeg
import sys

def run():
  # process = (
  #   ffmpeg
  #   .input('pipe:', format='wav')
  #   .output("icecast://source:hackme@localhost:8000/stream.mp3", format='mp3', content_type="audio/mpeg")
  #   .global_args("-re") # argument to act as a live stream
  #   .run_async(pipe_stdin=True)
  # )

  def cb(chunk):
    # process.stdin.write(chunk)
    sys.stdout.write("".join(map(chr, chunk)))
    return False

  downloader.download('https://www.youtube.com/watch?v=BaW_jenozKc', cb)
  # downloader.download('https://www.youtube.com/watch?v=kgBcg4uBd9Q', cb)
  # downloader.download('https://www.youtube.com/watch?v=EbnH3VHzhu8', cb)

if __name__ == "__main__":
  run()