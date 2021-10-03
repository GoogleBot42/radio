import downloader
import uploader
import transcoder
import torrent
import buffer
from time import sleep
from flask import Flask, request
from queue import Queue
import json
import requests
import sys

app = Flask(__name__)

host = sys.argv[1]
stream = sys.argv[2]

class Radio(object):
  def __init__(self):
    self.downloader = None
    self.transcoder = None
    self.buffer = None
    self.uploader = uploader.Uploader(host, stream)
    self.playingUrl = None
    self.queue = Queue()

  # plays the next song in the queue 
  def play(self):
    self.playingUrl = self.queue.get()

    # determine what downloader needs to be used and create the downloader
    if self.playingUrl.startswith("magnet:?"):
      # it's a torrent
      torrent.mountTorrent(self.playingUrl)
      self.playingUrl = torrent.getTorrentMedia()
      if self.playingUrl is None:
        # this torrent is unplayable, skip it
        torrent.umountTorrent()
        return self.play()
      else:
        self.downloader = downloader.DirectDownloader(self.playingUrl, self.downloadFinished)
    else:
      # assume http/https
      info = downloader.getVideoInfo(self.playingUrl)
      if info is None:
        # this url is unplayable, skip it
        return self.play()
      elif ("direct" in info and info["direct"] == True) or ("format_id" in info and info["format_id"] == "rtmp"): # stdout for rtmp in ytdl is broken
        # direct source
        self.downloader = downloader.DirectDownloader(self.playingUrl, self.downloadFinished)
      else:
        # requires youtube-dl
        self.downloader = downloader.YtdlpDownloader(self.playingUrl, self.downloadFinished)

    self.transcoder = transcoder.Transcoder(self.downloader)
    self.buffer = buffer.Buffer(self.transcoder)
    self.uploader.setUpstream(self.buffer)

  def isPlaying(self):
    return not self.playingUrl is None

  # blocks the caller until the uploader and trancoder recieve no more data
  # if this is a livestream, the end might never come!
  def blockUntilDonePlaying(self):
    self.transcoder.listener.blockUntilEmpty()
    self.uploader.listener.blockUntilEmpty()

  # add to queue or play right now if queue is empty
  def addToQueue(self,url):
    self.queue.put(url)

  def playIfSongAvailable(self):
    if not self.isPlaying() and not self.queue.empty():
      self.play()
 
  # stops playing immediately and cleans up
  def stopPlaying(self):
    self.downloader.stop()
    self.transcoder.stop()
    self.buffer.stop()
    self.playingUrl = None
    torrent.umountTorrent() # make sure torrent is unmounted

  # downloader callback function, called when the downloader is finished
  # but may still have bytes left that need to be read and played
  def downloadFinished(self):
    self.blockUntilDonePlaying()
    self.stopPlaying()
    self.playIfSongAvailable()

  def listenerCount(self):
    r = requests.get("http://" + host + "/status-json.xsl")
    return json.loads(r.text)['icestats']['source']['listeners']

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

@app.route('/listeners', methods=['GET'])
def listeners():
  return str(r.listenerCount())

def run():
  app.run(host="0.0.0.0", port=int(sys.argv[3]))

if __name__ == "__main__":
  run()