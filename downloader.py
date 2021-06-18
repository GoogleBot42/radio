#
# Downloads the video/audio as a stream from a provided link using youtube-dl
# does not save the file, only the most recent fragment is held. Thus, this is
# ideal for devices with little memory
# TODO gather video metadata before download
#

import tempfile
import sys
import subprocess
import os
import pip
import signal
from logger import logger
from threading import Thread, main_thread
from time import sleep
from stream import StreamSource

def updateYoutubeDL():
  pip.main(['install', '--target=' + dirpath, '--upgrade', 'youtube_dl'])

def importYoutubeDL():
  return __import__('youtube_dl')

dirpath = tempfile.mkdtemp()
sys.path.append(dirpath)
updateYoutubeDL()

class Downloader(Thread, StreamSource):

  def __init__(self, url, cb):
    Thread.__init__(self)

    # update youtube-dl
    # TODO: do this only every once in a while
    # updateYoutubeDL()

    self.cb = cb
    self.exit = False

    env = dict(os.environ)
    env["PYTHONPATH"] = dirpath
    cmd = [
      sys.executable,
      dirpath + "/bin/youtube-dl",
      "-o", "-",
      "-f", "bestaudio/best",
      # "--audio-format", "mp3", "-x", # cannot do because it requires a tmp file to re-encode
      "--prefer-ffmpeg",
      "--no-mark-watched",
      "--geo-bypass",
      "--no-playlist",
      "--retries", "100",
      "--no-call-home",
      url
    ]
    self.popen = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    logger.add(self.popen.stderr, "youtube-dl.log")
    self.start()

  def isAlive(self):
    return self.popen.poll() is None

  def stop(self):
    if self.isAlive():
      os.killpg(os.getpgid(self.popen.pid), signal.SIGTERM)
    self.popen.stdout.close()
    self.exit = True

  # checks to see if the current download has finished
  # if yes, cleans up and fires callback
  def run(self):
    while main_thread().is_alive() and not self.exit:
      if not self.isAlive():
        self.cb()
      sleep(0.1)

  def getStream(self):
    return self.popen.stdout