#
# Downloads the video/audio as a stream from a provided link using youtube-dl
# does not save the file, only the most recent fragment is held. Thus, this is
# ideal for devices with little memory
# TODO gather video metadata before download
#

# dirpath = tempfile.mkdtemp()
# sys.path.append(dirpath)
# def import_from_pip(package):
#   pip.main(['install', '--target=' + dirpath, '--upgrade', package])
#   return __import__(package)
# youtube_dl = import_from_pip('youtube_dl')

import tempfile
import sys
import subprocess
import os

youtube_dl = None

def execute(cmd):
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  # monitor the stdout
  BUFFER_SIZE = 1024
  for chunk in iter(lambda: popen.stdout.read(BUFFER_SIZE), b''):
    yield chunk
  popen.stdout.close()
  popen.wait()

def updateYoutubeDL():
  pip.main(['install', '--target=' + dirpath, '--upgrade', 'youtube_dl'])

def importYoutubeDL():
  global youtube_dl
  youtube_dl = __import__('youtube_dl')

def download(url):
  # update youtube-dl
  # TODO: do this only every once in a while
  #updateYoutubeDL()

  # start downloader so that it's stdout (with fragments) may be captured
  for s in execute([sys.executable, os.path.realpath(__file__), dirpath,url]):
    print(s)

def runYoutubeDL(url):
  ydl_opts = {
    'logtostderr': True,
    'outtmpl': '-',
  }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

if __name__ == "__main__":
  dirpath = sys.argv[1]
  sys.path.append(dirpath)
  importYoutubeDL()
  runYoutubeDL(sys.argv[2])
else:
  import pip
  dirpath = tempfile.mkdtemp()
  sys.path.append(dirpath)
  updateYoutubeDL()