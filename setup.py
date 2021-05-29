from setuptools import setup

requires = ["pip","ffmpeg-python"]

setup(
    name='radio',
    version='0.1',
    py_modules=['radio','downloader','logger'],
    entry_points={
        'console_scripts': ['radio = radio:run']
    },
)