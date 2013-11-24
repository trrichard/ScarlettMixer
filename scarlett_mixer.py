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
import wx
import mixer_model
from docopt import docopt
from scarlettgui import MixerConsoleFrame

def unpackMixers(mixerList, scarlett_index):
    """Given a list of mixers, return the logical objects associated
    with each mixer in a format that makes sense.
    TYPES:
        Global Volume Control
        Sample Clock Sync Status
        Sample Clock Source
        Save to HW
        Master Outputs
        Matrix Mixers
        Matrix Inputs
        Input Sources : selects what data source is read by alsa
        Input Adjustments : turns on and off settings for certian inputs"""

    master_re = re.compile(
            r'Master (?P<balance>\w*) \((?P<output>\w*)')
    global_volume_re = re.compile(r'^Master$')
    matrix_re = re.compile(r'Matrix (?P<id>[0-9]+) Mix (?P<mix>\w+)')
    matrix_input_re = re.compile(r'Matrix (?P<id>[0-9]+) Input')
    input_source_re = re.compile(r'Input Source (?P<id>[0-9]+)')
    input_adj_re = re.compile(r'Input (?P<id>[0-9]+) (?P<adjustment>\w+)')
    special_re = re.compile(r'(Save To HW|Sample Clock)')
    
    expressions = {
            master_re: "master_volume",
            matrix_re: "matrix_mixer",
            matrix_input_re: "matrix_source",
            input_source_re: "input_source",
            input_adj_re: "input_adjustment",
            special_re: "special",
            global_volume_re: "master_volume"}

    print "There are {} mixers".format(len(mixerList))

    mixers = {}
    matricies = {}
    for mixer_name in mixerList:
        for expression, catagory in expressions.items():
            m = expression.match(mixer_name)
            if m:
                if catagory not in mixers:
                    mixers[catagory] = []
                mixer = aa.Mixer(
                        control=mixer_name,
                        cardindex=scarlett_index)
                mixers[catagory].append(mixer)
                if catagory == "matrix_mixer":
                    matrix_id = m.group('id')
                    matrix_mix = m.group('mix')
                    if matrix_id not in matricies:
                        matricies[matrix_id] = {}
                    matricies[matrix_id][matrix_mix] = mixer

    print matricies


class ScarlettMixerAdaptor(mixer_model.MixerModel):
    pass


def main(arguments):
    mixer = None
    if arguments["-d"]:
        print "devmode"
        mixer = mixer_model.DevMixerAdaptor()
    else:
        cards = aa.cards()
        scarlett_index = None
        for i in range(0, len(cards)):
            if cards[i] == "USB":
                # it's probably scarlett
                scarlett_index = i
        if not scarlett_index:
            raise Exception("Couldn't find your scarlett usb device!")
        else:
            print "Found Scarlett at index {}".format(scarlett_index)

        scarlett_mixers = aa.mixers(scarlett_index)
        
        print "Found {} scarlett mixers".format(len(scarlett_mixers))
        mixer = unpackMixers(scarlett_mixers,scarlett_index)
        

    # Create a new app, don't redirect stdout/stderr to a window.
    app = wx.App(False)  
    frame = MixerConsoleFrame( None, mixer) 
    # A Frame is a top-level window.
    frame.Show(True)     # Show the frame.
    app.MainLoop()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Scarlett Mixer 0.1')
    main(arguments)
