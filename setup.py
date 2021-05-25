from setuptools import setup

requires = ["pip"]

setup(
    name='radio',
    version='0.1',
    py_modules=['radio','downloader'],
    entry_points={
        'console_scripts': ['radio = radio:run']
    },
)