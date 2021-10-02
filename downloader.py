#
# Downloads the video/audio as a stream from a provided link using yt-dlp
# does not save the file, only the most recent fragment is held. Thus, this is
# ideal for devices with little memory
#

import ffmpeg
import tempfile
import sys
import subprocess
import os
import pip
import signal
import json
import shutil
import glob
from logger import logger
from threading import Thread, main_thread
from time import sleep
from stream import StreamSource

def updateYtdlp():
  pip.main(['install', '--target=' + dirpath, '--upgrade', 'yt-dlp'])

def importYoutubeDL():
  return __import__('yt-dlp')

dirpath = tempfile.mkdtemp()
sys.path.append(dirpath)
updateYtdlp()

baseOpts = [
  "-f", "bestaudio/best", # select for best audio
  # "--audio-format", "mp3", "-x", # cannot do because it requires a tmp file to re-encode
  "--prefer-ffmpeg",
  "--no-mark-watched",
  "--geo-bypass",
  "--no-playlist",
  "--retries", "100",
  "--extractor-retries", "100",
#      "--throttled-rate", "100K", # get around youtube throttling; probably not needed anymore
  "--no-call-home",
  "--sponsorblock-remove", "sponsor,intro,selfpromo,interaction,preview,music_offtopic",
]

def runYtdlp(opts):
  # update yt-dlp
  # TODO: do this only every once in a while
  # updateYtdlp()

  env = dict(os.environ)
  env["PYTHONPATH"] = dirpath
  cmd = [
    sys.executable,
    dirpath + "/bin/yt-dlp"
  ] + baseOpts + opts
  popen = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
  logger.add(popen.stderr, "yt-dlp.log")
  return popen

def getVideoInfo(url):
  popen = runYtdlp([
    "-j", # dump all metadata as json
    "--playlist-items", "1", # don't go through every single item in playlist
    url
  ])

  j = popen.communicate()[0]

  # make sure the ytdlp instance is closed
  if popen.poll() is None: # is alive?
    os.killpg(os.getpgid(popen.pid), signal.SIGTERM) # kill
  popen.stdout.close()

  # keys of interest (but not always present)
  # title, direct, extractor, upload_date
  # format_id (machine readable)
  # view_count, uploader, duration, view_count, average_rating
  # age_limit, like_count, dislike_count, thumbnail,

  try:
    return json.loads(j)
  except:
    return None

fuseTorrentLocation = "torrent"
btfsDataLocation = "btfs-data"

def mountTorrent(magnet):
  print("mounting torrent...")
  umountTorrent()
  os.mkdir(fuseTorrentLocation)

  env = dict(os.environ)
  env["PATH"] = "/run/wrappers/bin:" + env["PATH"] 
  o = subprocess.Popen([
    "btfs",
    "-o", "auto_unmount", # unmount if process is killed
    "--data-directory=" + btfsDataLocation,
    magnet,
    fuseTorrentLocation
  ], env=env)
  o.communicate() # wait for it to finish
  sleep(5) # uhhh I guess I need to sleep?

def umountTorrent():
  print("unmounting torrent...")
  if os.path.isdir(fuseTorrentLocation):
    env = dict(os.environ)
    env["PATH"] = "/run/wrappers/bin:" + env["PATH"] 
    o = subprocess.Popen([
      "fusermount",
      "-u", fuseTorrentLocation
    ], env=env)
    o.communicate() # wait for it to finish
    os.rmdir(fuseTorrentLocation)
  if os.path.isdir(btfsDataLocation):
    shutil.rmtree(btfsDataLocation)

def getTorrentMedia():
  print("Getting torrent media...")
  files = glob.glob(fuseTorrentLocation + '/**/*', recursive=True)
  print(files)
  files = [f for f in files if f.endswith(".acc") or f.endswith(".avi") or f.endswith(".mid") or f.endswith(".midi") or f.endswith(".mp3") or f.endswith(".mp4") or f.endswith(".mpeg") or f.endswith(".oga") or f.endswith(".ogv") or f.endswith(".opus") or f.endswith(".ts") or f.endswith(".wav") or f.endswith(".weba") or f.endswith(".webm") or f.endswith(".3gp") or f.endswith(".3g2")]
  if len(files) == 0:
    return None
  return files[0] # just the first one I guess...

# Downloads using yt-dlp
class YtdlpDownloader(Thread, StreamSource):
  def __init__(self, url, cb):
    Thread.__init__(self)

    self.cb = cb
    self.exit = False

    self.popen = runYtdlp([
      "-o", "-", # output stream to stdout
      url
    ])
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

# Downloads the file and plays it (must be a direct URL, ex: cannot be a yt link)
class DirectDownloader(Thread, StreamSource):
  def __init__(self, url, cb):
    Thread.__init__(self)

    self.cb = cb
    self.exit = False

    self.process = ( ffmpeg
      .input(url)
      .output('pipe:', format='mp3')
      .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    logger.add(self.process.stderr, "direct-downloader.log")

    self.start()

  def isAlive(self):
    return self.process.poll() is None

  # checks to see if the current download has finished
  # if yes, cleans up and fires callback
  def run(self):
    while main_thread().is_alive() and not self.exit:
      if not self.isAlive():
        self.cb()
      sleep(0.1)

  def stop(self):
    self.process.stdout.close()
    self.process.stderr.close()
    self.exit = True

  def getStream(self):
    return self.process.stdout