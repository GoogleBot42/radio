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
    # "--extract-audio",
    "--audio-format", "wav",
    "--prefer-ffmpeg",
    #"--postprocessor-args", "-re",
    #"--external-downloader", "ffmpeg",
    #"--external-downloader-args", "-re",
    url
  ]
  popen = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, preexec_fn=os.setsid)

  # monitor the stdout and send to callback, if result from callback function is true,
  # then kill the download process
  BUFFER_SIZE = 8096
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
