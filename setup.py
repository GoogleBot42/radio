from setuptools import setup

setup(
    name='radio',
    version='0.1',
    py_modules=['radio'],
    entry_points={
        'console_scripts': ['radio = radio:run']
    },
)