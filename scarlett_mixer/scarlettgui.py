import wx
# Import the easiest to use scrolledpanel.
import wx.lib.scrolledpanel as scrolled
import math

TASK_RANGE = 50
MIXER_CHANGED = "alsachanged"

class ChannelInputStrip(wx.Panel):
    def __init__(
            self,
            parent,
            channel,
            output_mixes):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.channel = channel
        self.output_mixes = output_mixes

        # TODO: Implement Stereo Mixers/Stereo Binding
        volumeAndMeterBarContainer = wx.BoxSizer(wx.HORIZONTAL)
        height = 250
        width = 75
        decebil_range = 50
        self.pan = wx.Slider(
                self,
                value=0,
                minValue=-100,
                maxValue=100,
                size=(width, -1), 
                style=(wx.SL_HORIZONTAL))
        self.gain = wx.Slider(
                self,
                value=self.channel.getGain(output_mixes[0]),
                minValue=self.channel.getGainRange(output_mixes[0])[0],
                maxValue=self.channel.getGainRange(output_mixes[0])[1],
                size=(-1, height), 
                style=(wx.SL_VERTICAL|wx.SL_INVERSE))

        
        self.gauge = wx.Gauge(
                self, 
                range=decebil_range, 
                size=(25, height),
                style=wx.GA_VERTICAL)

        self.gain.Bind(wx.EVT_SCROLL, self.onAdjustGain)

        volumeAndMeterBarContainer.Add(self.gain)
        volumeAndMeterBarContainer.Add(self.gauge)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if channel.isInputSetable():
            self.select_input = wx.Button(
                    self,
                    label=channel.getCurrentInput(),
                    size=(width,-1))
            self.select_input.Bind(wx.EVT_BUTTON, self.onSelect)
            sizer.Add(self.select_input)
        else:
            self.select_input = wx.StaticText(
                    self,
                    label=channel.getCurrentInput(),
                    size=(width,-1))
            self.select_input.Bind(wx.EVT_BUTTON, self.onSelect)
            sizer.Add(self.select_input)

        sizer.Add(volumeAndMeterBarContainer)
        if len(output_mixes) > 1:
            self.pan.Bind(wx.EVT_SCROLL, self.onAdjustPan)
            sizer.Add(self.pan)

        self.SetSizer(sizer)

    def reloadFromChannel(self):
        self.select_input.SetLabel(self.channel.getCurrentInput())

    def onAdjustGain(self, e):
        if self.output_mixes > 1:
            self.applyGainPan()
        else:
            self.channel.setGain(self.gain.GetValue())

    def onAdjustPan(self, e):
        self.applyGainPan()

    def getGainPan(self):
        left_gain = self.channel.getGain(self.output_mixes[0])
        right_gain = self.channel.getGain(self.output_mixes[1])
        #TODO: reverse the formula in applyGainPan()

    def applyGainPan(self):
        """
        I'm 90% sure I did this math wrong. How to calculate individual
        gains using pan? Also, this logic should be moved elsewhere.
        And, this is probably super inefficent.
        """
        currentGain = self.gain.GetValue()
        currentPan = self.pan.GetValue()/100.0
        pan_radians = (math.pi * (currentPan+1))/4
        pre_gain_l = math.sin(pan_radians)**.25
        pre_gain_r = math.cos(pan_radians)**.25
        gain_l = currentGain * pre_gain_l
        gain_r = currentGain * pre_gain_r 
        self.channel.setGain(self.output_mixes[0],int(gain_l))
        self.channel.setGain(self.output_mixes[1],int(gain_r))


    def onSelect(self, e):
        menu = wx.Menu()
        for item in self.channel.getInputChoices():
            idnumber = wx.NewId()
            menu.Append(idnumber, item, "Select {}".format(item))
            menu.Bind(wx.EVT_MENU, self.onMenuSelect)
        self.PopupMenu(menu,(0,0))
        menu.Destroy()

    def onMenuSelect(self, event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        self.channel.setInput(menuItem.GetItemLabel())


class MixPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, mixer, output_mixes):
        scrolled.ScrolledPanel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mixer = mixer
        self.output_mixes = output_mixes
        self.InitUI()
        self.SetAutoLayout(1)
        self.SetupScrolling()
    
    def OnSelect(self, e):
        pass

    def addMatrixInput(self, panel, channel, output_mixes):
        channelInputStrip = ChannelInputStrip(panel, 
                channel, 
                output_mixes)
        return channelInputStrip

    
    def InitUI(self):
        self.count = 0

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.volumes = wx.BoxSizer(wx.HORIZONTAL)
        
        self.channel_input_strips = []
        for channel in self.mixer.getInputChannels():
            inputer = self.addMatrixInput(
                    self, 
                    channel,
                    self.output_mixes)
            self.channel_input_strips.append(inputer)
        
        for index in range(0,len(self.channel_input_strips),2):
            left = self.channel_input_strips[index]
            right = self.channel_input_strips[index+1]
            strip_pair_top = wx.BoxSizer(wx.HORIZONTAL)
            strip_pair = wx.BoxSizer(wx.VERTICAL)
            strip_pair_top.Add(left)
            strip_pair_top.Add(right)
            strip_pair.Add(strip_pair_top)
            join_stereo_pair = wx.Button(
                    self,label="Join",)
            strip_pair.Add(join_stereo_pair)
            self.volumes.Add(strip_pair)


        vbox.Add((0, 20))
        vbox.Add(self.volumes, proportion=1)

        self.SetSizer(vbox)
        self.Centre()

    def reloadAllChannels(self, e):
        for vol in self.channel_input_strips:
            vol.reloadFromChannel()

class MixerConsoleMixes(wx.Notebook):
    def __init__(self,parent,mixer):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP)
        # TODO: Iterate through list of mixer groups
        self.mixer = mixer
        tabOne = MixPanel(self, mixer, ["A", "B"])
        tabTwo = MixPanel(self, mixer, ["C", "D"])
        tabThree = MixPanel(self, mixer, ["E", "F"])

        self.tabs  = [tabOne, tabTwo,tabThree]
        self.AddPage(tabOne, "A+B Mix")
        self.AddPage(tabTwo, "C+D Mix")
        self.AddPage(tabThree, "E+F Mix")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.timer = wx.Timer(self, wx.NewId())
        self.Bind(
            wx.EVT_TIMER,
            self.reloadAllChannels,
            self.timer)
        self.timer.Start(200)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def reloadAllChannels(self, e):
        if self.mixer.poll():
            for tab in self.tabs:
                tab.reloadAllChannels(e)

class MixerConsoleMasters(wx.Panel):
    def __init__(
            self,
            parent,
            mixer):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.master_mix_strips = []
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for channel in mixer.getMasterChannels():
            # Add that channel as a mixer strip
            mixes = channel.getMixList()
            print mixes
            if len(mixes) < 1:
                print "skip"
                continue
            input_strip = ChannelInputStrip(
                    self,
                    channel,
                    mixes)
            self.master_mix_strips.append(input_strip)
            sizer.Add(input_strip)

        self.SetSizer(sizer)

class MixerConsoleFrame(wx.Frame):
    def __init__(self, parent, mixer):
        wx.Frame.__init__(self, 
                parent, 
                title="Scarlett Mixer",
                size = ( 1000, 450),
                )
        panel = wx.Panel(self)
        self.mixer = mixer
        mixesConsole = MixerConsoleMixes(panel, mixer)
        mastersConsole = MixerConsoleMasters(panel, mixer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(mixesConsole, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(mastersConsole, 1)
        panel.SetSizer(sizer)
        self.Layout()
        self.Show()
