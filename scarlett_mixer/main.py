#!/usr/bin/python
"""
Scarlett Mixer

Usage:
    scarlett_mixer.py [-d]
    scarlett_mixer.py --version
    scarlett_mixer.py --help

Options:
    -d     Development Mode (Fake Mixer)
"""
import alsaaudio as aa
import re
import os
import select
import wx
import mixer_model
from docopt import docopt
from scarlettgui import MixerConsoleFrame


def main():
    arguments = docopt(__doc__, version='Scarlett Mixer 0.1')
    mixer = None
    poller = None
    app = wx.App(False)
    if arguments["-d"]:
        print "devmode"
        mixer = mixer_model.DevMixerAdaptor()
    else:
   #     poller = poll_alsa.PollAlsa()
        mixer = mixer_model.ScarlettMixerAdaptor()

    # Create a new app, don't redirect stdout/stderr to a window.
    frame = MixerConsoleFrame( None, mixer)

    # Stop polling on window close
    if poller:
        print "Binding Stop"
        def HardStop(event):
            poller.stop()
            frame.Destroy()
        frame.Bind(wx.EVT_CLOSE,HardStop)
 
    # A Frame is a top-level window.
    frame.Show(True)     # Show the frame.
    app.MainLoop()


if __name__ == '__main__':
    main()
