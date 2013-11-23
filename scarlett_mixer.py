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

class MixerAdaptor:
    """
    Adapts from mixer hardware to gui.
    """
    def __init__(self):
        print "init mixer"
        self.observers = []
    
    def addObserver(self, observer):
        """
        Implementation of the observer pattern for the mixer,
        calls the observer function with some parameters 
        I haven't decided on yet. This is used to handle the
        metering
        """
        self.observers.append(observer)

    def notifyObservers(self, delta):
        for observer in self.observers:
            observer(delta)

    def saveRouting():
        pass

    def getHardwareOutputMuxChannels(self):
        "[ list of names? ]"
        pass

    def getSoftwareOutputMuxChannels(self):
        "[ list of names? ] "
        pass

    def getHardwareInputMuxChannels(self):
        "[ list of names? ]"
        pass

    def getSoftwareInputMuxChannels(self):
        " [ list of names? ] "
        pass

    def getMatrixMuxInputChannels(self):
        "[ number of channels? ] "
        pass

    def getMatrixMuxOutputChannels(self):
        "[ number of channels? ] "
        pass

    def getMatrixMuxMap(self):
        "{ from hw/sw input channels to matrix numbers }"
        pass

    def getMatrix(self):
        "[input(18)][output(6)] => gain"
        pass

class ScarlettMixerAdaptor(MixerAdaptor):
    pass

class DevMixerAdaptor(MixerAdaptor):
    def getHardwareOutputMuxChannels(self):
        "[ list of names? ]"
        return [ 
                "monitor_left",
                "monitor_right",
                "headphones_1_left",
                "headphones_1_right",
                "headphones_2_left",
                "headphones_2_right",
                "spdif_left",
                "spdif_right",
                ]

    def getSoftwareOutputMuxChannels(self):
        "[ list of names? ] "
        outputMuxChannels = []
        for i in range(0,18):
            outputMuxChannels.append("pcm_{}".format(i))
        return outputMuxChannels

    def getHardwareInputMuxChannels(self):
        "[ list of names? ]"
        inputMuxChannels = []
        for i in range(0,18):
            inputMuxChannels.append("analog_{}".format(i))
        return inputMuxChannels

    def getSoftwareInputMuxChannels(self):
        " [ list of names? ] "
        inputMuxChannels = []
        for i in range(0,6):
            inputMuxChannels.append("pcm_{}".format(i))
        return inputMuxChannels

    def getMatrixMuxInputChannels(self):
        "[ number of channels? ] may be unnecessary"
        pass

    def getMatrixMuxOutputChannels(self):
        "[ number of channels? ] may be unnecessary"
        pass

    def getMatrixMuxMap(self):
        "{ from hw/sw input channels to matrix input numbers } no this is necessary "
        return {
            0:"analog_0",
            1:"analog_1",
            2:"analog_2",
            3:"analog_3",
            4:"analog_4",
            5:"analog_5",
            6:"analog_6",
        }

    def getMatrix(self):
        "[matrix input number input(18)][matrix output number output(6)] => gain"
        matrix_in = 18
        matrix_out = 6
        matrix = []
        for i in range(0,matrix_in):
            matrix.append([])
            for j in range(0,matrix_out):
                matrix[i].append(0)
        return matrix

def main(arguments):
    mixer = None
    if arguments["-d"]:
        print "devmode"
        mixer = DevMixerAdaptor()
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
