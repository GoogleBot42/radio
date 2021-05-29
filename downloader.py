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

def updateYoutubeDL():
  pip.main(['install', '--target=' + dirpath, '--upgrade', 'youtube_dl'])

def importYoutubeDL():
  return __import__('youtube_dl')

dirpath = tempfile.mkdtemp()
sys.path.append(dirpath)
updateYoutubeDL()

def executeYoutubeDL(url, cb):
  env = dict(os.environ)
  env["PYTHONPATH"] = dirpath
  cmd = [
    sys.executable,
    dirpath + "/bin/youtube-dl",
    "-o", "-",
    "-f", "bestaudio/best",
    "--audio-format", "mp3",
    "--prefer-ffmpeg",
    "--no-mark-watched",
    "--geo-bypass",
    "--no-playlist",
    "--retries", "100",
    "--buffer-size", "1M"
    "--no-call-home"
    url
  ]
  popen = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

  # monitor the stdout and send to callback, if result from callback function is true,
  # then kill the download process
  BUFFER_SIZE = 8096
  logger.add(popen.stderr, "youtube-dl.log")
  for chunk in iter(lambda: popen.stdout.read(BUFFER_SIZE), b''):
    if cb(chunk):
      os.killpg(os.getpgid(popen.pid), signal.SIGTERM)
      break
  popen.stdout.close()
  popen.wait()

def download(url, cb):
  # update youtube-dl
  # TODO: do this only every once in a while
  # updateYoutubeDL()

  # start downloader so that it's stdout (with fragments) may be captured
  executeYoutubeDL(url, cb)
