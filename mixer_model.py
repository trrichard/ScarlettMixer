
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


class InputChannel():
    """
    Contains the input for the matrix
    """
    def __init__(self):
        pass

    def getCurrentInput(self):
        """
        Returns analog_1 etc.
        """
        pass
    
    def addObserver(self):
        pass

