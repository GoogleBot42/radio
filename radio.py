import downloader
import uploader
import transcoder
import nullsrc
from time import sleep
from flask import Flask, request
from queue import Queue

app = Flask(__name__)

class Radio(object):
  def __init__(self):
    self.downloader = None
    self.transcoder = None
    self.uploader = uploader.Uploader()
    self.playingUrl = None
    self.nullsrc = False
    self.queue = Queue()

  # plays the next song in the queue 
  def play(self):
    self.stopPlaying()
    self.nullsrc = False
    self.playingUrl = self.queue.get()
    self.downloader = downloader.Downloader(self.playingUrl, self.downloadFinished)
    self.transcoder = transcoder.Transcoder(self.downloader)
    self.uploader.setUpstream(self.transcoder)

  def playNullSrc(self):
    self.stopPlaying()
    self.nullsrc = True
    self.playingUrl = None
    self.downloader = nullsrc.NullSrc()
    self.transcoder = transcoder.Transcoder(self.downloader)
    self.uploader.setUpstream(self.transcoder)

  def isPlaying(self):
    return not self.playingUrl is None

  # blocks the caller until the uploader and trancoder recieve no more data
  # if this is a livestream, the end might never come!
  def blockUntilDonePlaying(self):
    if not self.nullsrc:
      self.transcoder.listener.blockUntilEmpty()
      self.uploader.listener.blockUntilEmpty()

  # add to queue or play right now if queue is empty
  def addToQueue(self,url):
    self.queue.put(url)

  def playIfSongAvailable(self):
    if not self.isPlaying():
      if self.queue.empty():
        self.playNullSrc()
      else:
        self.play()
 
  # stops playing immediately and cleans up
  def stopPlaying(self):
    if not self.downloader is None:
      self.downloader.stop()
    if not self.transcoder is None:
      self.transcoder.stop()
    self.playingUrl = None

  # downloader callback function, called when the downloader is finished
  # but may still have bytes left that need to be read and played
  def downloadFinished(self):
    self.blockUntilDonePlaying()
    self.stopPlaying()
    self.playIfSongAvailable()

r = Radio()

@app.route('/play', methods=['POST'])
def queueNext():
  next = request.form['url']
  r.addToQueue(next)
  r.playIfSongAvailable()
  return "Added"

@app.route('/skip', methods=['POST'])
def skipCurrent():
  r.stopPlaying()
  r.playIfSongAvailable()
  return "Skipped"

@app.route('/current', methods=['GET'])
def current():
  return r.playingUrl or 'nothing'

@app.route('/queue', methods=['GET'])
def queue():
  return str(list(r.queue.queue))

def run():
  r.addToQueue('https://www.youtube.com/watch?v=BaW_jenozKc')
  r.playIfSongAvailable()
  app.run(host="0.0.0.0")

if __name__ == "__main__":
  run()