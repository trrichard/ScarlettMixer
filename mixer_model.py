
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


class InputChannel():
    """
    Contains the input for the matrix.
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
    
    def addObserver(self):
        pass

    def getGainRange(self):
        return (0,134)

    def getGain(self, mix_number):
        pass

    def setGain(self, mix_number):
        pass

    def getInputChoices(self):
        pass


class DevInputChannel():
    """
    Contains the input for the matrix.
    """
    def __init__(self, mixer_number, input_name, outputs):
        self.mixer_number = mixer_number
        self.input_name = input_name
        self.gains = []
        self.outputs = outputs
        for output in outputs:
            self.gains.append(50)

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        return self.input_name

    def setInput(self, input_name):
        """
        Set to analog_xyz 
        """
        print "Setting input to", input_name
        self.input_name = input_name
    
    def addObserver(self):
        print "Adding Observer", input_name

    def getGainRange(self):
        return (0,134)

    def getGain(self, mix_number):
        if mix_number > len(gains) or mix_number < 0:
            raise "Mix number is invalid"
        return self.gains[mix_number]

    def setGain(self, mix_number, gain):
        if mix_number > len(gains) or mix_number < 0:
            raise "Mix number is invalid"
        minGain, maxGain = self.getGainRange()
        if gain < minGain or gain > maxGain:
            raise "Gain is invalid"
        self.gains[mix_number] = gain

    def getInputChoices(self):
        inputMuxChannels = []
        for i in range(0,18):
            inputMuxChannels.append("analog_{}".format(i))
        for i in range(0,6):
            inputMuxChannels.append("pcm_{}".format(i))
        return inputMuxChannels

class DevMixerAdaptor(MixerModel):
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
        matrix_in = 18
        matrix_out = 6
        matrix = []
        channels = []
        outputs = ["A", "B", "C", "D", "E", "F" ]
        for i in range(0,matrix_in):
            channel = DevInputChannel(i, self.getMatrixMuxMap()[i], outputs)
            channels.append(channel)
        return channels

