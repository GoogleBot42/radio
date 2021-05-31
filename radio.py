import downloader
import uploader
import transcoder
from time import sleep

def run():
  def cb():
    global d
    global t
    global u
    print("----------------FINISHED-----------")
    t.listener.blockUntilEmpty()
    u.listener.blockUntilEmpty()
    d.stop()
    t.stop()
    d = downloader.Downloader('https://www.youtube.com/watch?v=BQQ3qZ9FC70', cb)
    t = transcoder.Transcoder(d)
    u.setUpstream(t)

  u = uploader.Uploader()
  d = downloader.Downloader('https://www.youtube.com/watch?v=kgBcg4uBd9Q', cb)
  t = transcoder.Transcoder(d)
  u.setUpstream(t)

  while True:
    sleep(1)

if __name__ == "__main__":
  run()