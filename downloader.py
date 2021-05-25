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
import pip
import sys
import youtube_dl
import subprocess

dirpath = tempfile.mkdtemp()
sys.path.append(dirpath)

BUFFER_SIZE = 1024

def execute(cmd):
  popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  # monitor the stdout
  for chunk in iter(lambda: popen.stdout.read(BUFFER_SIZE), b''):
    yield chunk
  popen.stdout.close()
  popen.wait()

def updateYoutubeDL():
  pip.main(['install', '--target=' + dirpath, '--upgrade', package])

def download(url):
  # update youtube-dl
  # TODO: do this only every once in a while
  #updateYoutubeDL()

  # start downloader so that it's stdout (with fragments) may be captured
  for s in execute(["python3","downloader.py",url]):
    print(s)

def runYoutubeDL(url):
  ydl_opts = {
    'logtostderr': True,
    'outtmpl': '-',
  }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

if __name__ == "__main__":
  runYoutubeDL(sys.argv[1])