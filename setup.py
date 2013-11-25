import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "scarlett_mixer",
    version = "0.0.1",
    author = "Tyler",
    author_email = "trrichard@gmail.com",
    description = ("A mixer for the Focusrite Scarlett devices"),
    license = "TODO",
    keywords = "mixer audio focusrite scarlett 18i8",
    url = "https://github.com/trrichard/ScarlettMixer",
    packages=['scarlett_mixer'],
    long_description=read('README'),
    classifiers=[],
    entry_points = {
        'console_scripts': ['scarlett_mixer = scarlett_mixer.main:main']
    },
    install_requires=['docopt','pyalsaaudio'],
)
