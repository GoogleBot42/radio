import downloader
import uploader
import transcoder
from time import sleep

def cb():
  global d
  global t
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

#def run():
  # up = uploader.Uploader()
  # t = transcoder.Transcoder(up)
  # downloader.download('https://www.youtube.com/watch?v=BaW_jenozKc', t.callback)
  # t = transcoder.Transcoder(up)
  # downloader.download('https://www.youtube.com/watch?v=EbnH3VHzhu8', t.callback)
  # downloader.download('https://www.youtube.com/watch?v=kgBcg4uBd9Q', cb)
  # downloader.download('https://www.youtube.com/watch?v=EbnH3VHzhu8', cb)

if __name__ == "__main__":
  #run()
  while True:
    sleep(1)