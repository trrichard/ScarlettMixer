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
import poll_alsa
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
    matrix_inputs = {}
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
                if catagory == "matrix_source":
                    matrix_inputs[m.group('id')] = mixer
                if catagory == "matrix_mixer":
                    matrix_id = m.group('id')
                    matrix_mix = m.group('mix')
                    if matrix_id not in matricies:
                        matricies[matrix_id] = {}
                    matricies[matrix_id][matrix_mix] = mixer

    matricies2 = []
    # convert return values to a list so we have an order gaurentee
    # it sucks but it needs to be done
    for m in matricies:
        matricies2.append(None)
    for id,value in matricies.items():
        matricies2[int(id)-1] = value
    matrix_inputs2 = []
    for m in matrix_inputs:
        matrix_inputs2.append(None)
    for id, value in matrix_inputs.items():
        matrix_inputs2[int(id)-1] = value

    return matricies2, matrix_inputs2


class ScarlettMixerAdaptor(mixer_model.MixerModel):
    def __init__(self):
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
        matricies, matrix_inputs = unpackMixers(
                scarlett_mixers,
                scarlett_index)
        self.input_channels = []
        for i in range(0,len(matricies)):
            self.input_channels.append(
                mixer_model.ScarlettInputChannel(
                    matricies[i],
                    matrix_inputs[i]
                    ))
        self.loadPolls()

    def getInputChannels(self):
        return self.input_channels

    def loadPolls(self):
        self.descriptors = set()
        for channel in self.getInputChannels():
            self.descriptors = self.descriptors.union(
                    self.descriptors,
                    set(channel.getPollDescriptiors()))
        self.poller = select.poll()
        for item in self.descriptors:
            self.poller.register(item[0],item[1])

    def poll(self):
        triggered = self.poller.poll(1)
        if triggered:
            for a,b in triggered:
                # read all from the descriptor,
                # we are doing full reloads right now
                # eventualy this read in data could be used to update
                # the gui more directly
                os.read(a,256)
            return True
        return False

def main(arguments):
    mixer = None
    poller = None
    app = wx.App(False)
    if arguments["-d"]:
        print "devmode"
        mixer = mixer_model.DevMixerAdaptor()
    else:
   #     poller = poll_alsa.PollAlsa()
        mixer = ScarlettMixerAdaptor()
        

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
    arguments = docopt(__doc__, version='Scarlett Mixer 0.1')
    main(arguments)
