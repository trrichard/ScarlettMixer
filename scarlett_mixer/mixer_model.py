import subprocess as sp
import select
import alsaaudio as aa
import re 
import os

class MixerModel:
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
    
    def getInputChannels(self):
        pass

    def getMasterChannels(self):
        pass


class InputChannel():
    """
    Contains the input for the matrix.
    Perhaps I should consider something more dynamic?
    """
    def __init__(self):
        pass

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        pass

    def setInput(self):
        """
        Set to analog_xyz 
        """
        pass
    
    def getInputChoices(self):
        pass
    
    def addObserver(self):
        pass

    def getGainRange(self):
        return (0,134)

    def getGain(self, mix_number):
        pass

    def setGain(self, mix_number):
        pass


class MasterChannel():
    """
    Contains the controls for any of the master channels. 
    """
    def __init__(self):
        pass

    def getName(self):
        """
        Returns analog_1 etc.
        """
        pass

    def getGainRange(self):
        return (0,100)

    def getGain(self, mix_number):
        pass

    def setGain(self, mix_number):
        pass
    
    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        pass

    def setInput(self):
        """
        Set to analog_xyz 
        """
        pass

    def getInputChoices(self):
        pass


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
            r'Master (?P<balance>\w*) \((?P<output>.*)\)')
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
    masters = {}
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
                if catagory == "master_volume":
                    if m.groups():
                        balance = m.group('balance')
                        output = m.group('output')
                        if output not in masters:
                            masters[output] = {}
                        masters[output][balance] = mixer
                    else:
                        if None not in masters:
                            masters[None] = {}
                        masters[None][None] = mixer

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

    print masters
    return matricies2, matrix_inputs2, masters

class ScarlettMixerAdaptor(MixerModel):
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
        matricies, matrix_inputs, masters = unpackMixers(
                scarlett_mixers,
                scarlett_index)
        self.input_channels = []
        for i in range(0,len(matricies)):
            self.input_channels.append(
                ScarlettInputChannel(
                    matricies[i],
                    matrix_inputs[i]
                    ))
        self.loadPolls()
        self.master_mixers = []
        for output in masters:
            input_controller = None
            lr_mixers = {}
            for con in masters[output]:
                if len(masters[output][con].getenum()) == 0:
                    input_controller =  masters[output][con]
                else:
                    lr_mixers[con] = masters[output][con]
            self.master_mixers.append(
                    ScarlettInputChannel(lr_mixers,input_controller))

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
    
    def getMasterChannels(self):
        return self.master_mixers
 
class ScarlettInputChannel():
    """
    Contains the input for the matrix and it's outputs...?
    """
    def __init__(self, alsa_mixers, alsa_input):
        self.alsa_mixers = alsa_mixers
        self.alsa_input = alsa_input
        self.observers = []
        self.poll_descriptors = []
        self.registerPolls()

    def registerPolls(self):
        """
        Can be optimized to remove and register only the polls we need
        """
        for pd in self.poll_descriptors:
            self.poller.unregister(pd[0][0])

        self.poll_descriptors = []
        for id, mixer in self.alsa_mixers.items():
            if mixer:
                self.poll_descriptors.append(mixer.polldescriptors()[0])
        if self.alsa_input:
            self.poll_descriptors.append(
                    self.alsa_input.polldescriptors()[0])
    def getMixList(self):
        mixlist = []
        for mixer in self.alsa_mixers:
            mixlist.append(mixer)
        return mixlist

    def getPollDescriptiors(self):
        return self.poll_descriptors

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        if self.isInputSetable():
            return self.alsa_input.getenum()[0]
        print self.alsa_input
        return self.alsa_input.mixer()

    def isInputSetable(self):
        return len(self.alsa_input.getenum())>0

    def setInput(self, input_name):
        """
        Set to analog_xyz 
        TODO: Add this amixer control to the alsaaudio library
        """
        card_index = self.alsa_input.cardname().split(":")[1]
        command = [
            "amixer", 
            "-c", 
            card_index,
            "sset",
            self.alsa_input.mixer(),
            input_name]
        print " ".join(command)
        sp.call(command)
    
    def addObserver(self, toCall):
        self.observers.append(toCall)

    def getGainRange(self,mix_number):
        # alsaaudio hardwires the volume to percentages from
        # 0 to 100 need to patch alsaaudio
        return (0,100)
#        return self.alsa_mixers[mix_number].getrange()

    def getGain(self, mix_number):
        return int(self.alsa_mixers[mix_number].getvolume()[0])

    def setGain(self, mix_number,gain):
        return self.alsa_mixers[mix_number].setvolume(gain)

    def getInputChoices(self):
        return self.alsa_input.getenum()[1]

class ScarlettMasterChannel():
    """
    Contains the mixer for a master channel.
    """
    def __init__(self, alsa_mixer, alsa_inputs):
        self.alsa_mixer = alsa_mixers
        self.alsa_inputs = alsa_input
        self.observers = []
        self.poll_descriptors = []
        self.registerPolls()

    def registerPolls(self):
        """
        Can be optimized to remove and register only the polls we need
        """
        for pd in self.poll_descriptors:
            self.poller.unregister(pd[0][0])

        self.poll_descriptors = []
        for id, mixer in self.alsa_mixers.items():
            if mixer:
                self.poll_descriptors.append(mixer.polldescriptors()[0])
        if self.alsa_input:
            self.poll_descriptors.append(
                    self.alsa_input.polldescriptors()[0])
    def getMixList(self):
        mixlist = []
        for mixer in self.alsa_mixers:
            mixlist.append(mixer)
        return mixlist

    def getPollDescriptiors(self):
        return self.poll_descriptors

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        if len(self.alsa_input.getenum())>0:
            return self.alsa_input.getenum()[0]
        return None

    def setInput(self, input_name):
        """
        Set to analog_xyz 
        TODO: Add this amixer control to the alsaaudio library
        """
        card_index = self.alsa_input.cardname().split(":")[1]
        command = [
            "amixer", 
            "-c", 
            card_index,
            "sset",
            self.alsa_input.mixer(),
            input_name]
        print " ".join(command)
        sp.call(command)

    def getGainRange(self,mix_number):
        # alsaaudio hardwires the volume to percentages from
        # 0 to 100 need to patch alsaaudio
        return (0,100)
#        return self.alsa_mixers[mix_number].getrange()

    def getGain(self, mix_number):
        return int(self.alsa_mixers[mix_number].getvolume()[0])

    def setGain(self, mix_number,gain):
        return self.alsa_mixers[mix_number].setvolume(gain)

    def getInputChoices(self):
        return self.alsa_input.getenum()[1]
class DevInputChannel():
    """
    Contains the input for the matrix.
    """
    def __init__(self, mixer_number, input_name, outputs):
        self.mixer_number = mixer_number
        self.input_name = input_name
        self.gains = {}
        self.outputs = outputs
        self.changed = False
        for output in outputs:
            self.gains[output] = 50

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        return self.input_name

    def setInput(self, input_name):
        """
        Set to analog_xyz 
        """
        self.input_name = input_name
        self.changed = True
    

    def getGainRange(self, mix_index):
        return (0,134)

    def getGain(self, mix_number):
        if mix_number not in self.gains:
            print "Mix number {} is invalid".format(mix_number)
            raise "err"
        return self.gains[mix_number]

    def setGain(self, mix_number, gain):
        if mix_number not in self.gains:
            raise "Mix number is invalid"
        minGain, maxGain = self.getGainRange(mix_number)
        if gain < minGain or gain > maxGain:
            raise "Gain is invalid"
        print "Mixer:{} Mix:{} Gain:{}".format(
                self.mixer_number,
                mix_number,
                gain)
        self.gains[mix_number] = gain
        self.changed = True

    def getInputChoices(self):
        inputMuxChannels = []
        for i in range(0,18):
            inputMuxChannels.append("analog_{}".format(i))
        for i in range(0,6):
            inputMuxChannels.append("pcm_{}".format(i))
        return inputMuxChannels

    def ifChangedResetState(self):
        if self.changed:
            self.changed = False
            return True
        return False
    
    def getMixList(self):
        return self.outputs

class DevMixerAdaptor(MixerModel):
    def __init__(self):
        self.matrix_in = 18
        self.matrix_out = 6
        self.matrix = []
        self.channels = []
        self.outputs = ["A", "B", "C", "D", "E", "F" ]
        for i in range(0,self.matrix_in):
            channel = DevInputChannel(i, 
                    self.getMatrixMuxMap()[i], 
                    self.outputs)
            self.channels.append(channel)

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
            7:"analog_7",
            8:"analog_8",
            9:"pcm_0",
            10:"pcm_1",
            11:"pcm_2",
            12:"pcm_3",
            13:"pcm_4",
            14:"pcm_5",
            15:"pcm_6",
            16:"pcm_7",
            17:"spdif_1",
            18:"spdif_2",
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

    def getInputChannels(self):
        return self.channels

    def poll(self):
        changed = False
        for c in self.channels:
            if c.ifChangedResetState():
                changed = True
        return changed
    
    def getMasterChannels(self):
        masters = [DevInputChannel(1,"BadAss",["L","R"])]
        return masters
