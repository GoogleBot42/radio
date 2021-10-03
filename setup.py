from setuptools import setup

requires = ["pip","ffmpeg-python","flask"]

setup(
  name='radio',
  version='0.1',
  py_modules=[
    'radio',
    'downloader',
    'uploader',
    'logger',
    'util',
    'stream_listener',
    'transcoder',
    'nullsrc',
    'buffer',
    'stream',
    'torrent'
    ],
  entry_points={
    'console_scripts': ['radio = radio:run']
  },
)