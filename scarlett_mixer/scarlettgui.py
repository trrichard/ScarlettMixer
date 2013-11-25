import wx
# Import the easiest to use scrolledpanel.
import wx.lib.scrolledpanel as scrolled
import math
from wx.lib.pubsub import Publisher

TASK_RANGE = 50
MIXER_CHANGED = "alsachanged"


class ChannelInputStrip(wx.Panel):
    def __init__(
            self,
            parent,
            channels,
            output_mixes):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        
        self.channels = channels
        self.output_mixes = output_mixes

        if len(channels) > 2:
            raise "Input Strips with > 2 channels not supported yet"
        # TODO: Implement Stereo Mixers/Stereo Binding
        volumeAndMeterBarContainer = wx.BoxSizer(wx.HORIZONTAL)
        height = 250
        width = 75
        decebil_range = 50
        pan = wx.Slider(
                self,
                value=0,
                minValue=-100,
                maxValue=100,
                size=(width, -1), 
                style=(wx.SL_HORIZONTAL))
        self.gain = wx.Slider(
                self,
                value=self.channels[0].getGain(output_mixes[0]),
                minValue=self.channels[0].getGainRange(output_mixes[0])[0],
                maxValue=self.channels[0].getGainRange(output_mixes[0])[1],
                size=(-1, height), 
                style=(wx.SL_VERTICAL|wx.SL_INVERSE))

        # TODO make the combo_box use current_input to select the
        # right input automaticaly

        self.select_input = wx.Button(
                self,
                label=channels[0].getCurrentInput(),
                size=(width,-1))
        
        self.gauge = wx.Gauge(
                self, 
                range=decebil_range, 
                size=(25, height),
                style=wx.GA_VERTICAL)

        self.select_input.Bind(wx.EVT_BUTTON, self.onSelect)
        self.gain.Bind(wx.EVT_SCROLL, self.onAdjustGain)
        pan.Bind(wx.EVT_SCROLL, self.onAdjustPan)
        self.pan = pan

        volumeAndMeterBarContainer.Add(self.gain)
        volumeAndMeterBarContainer.Add(self.gauge)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.select_input)
        sizer.Add(volumeAndMeterBarContainer)
        sizer.Add(pan)
        self.SetSizer(sizer)
        self.applyGainPan()

    def reloadFromChannel(self):
        for channel in self.channels:
            self.select_input.SetLabel(channel.getCurrentInput())

    def onAdjustGain(self, e):
        self.applyGainPan()

    def onAdjustPan(self, e):
        self.applyGainPan()

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
        #print gain_l,gain_r 
        self.channels[0].setGain(self.output_mixes[0],int(gain_l))
        self.channels[0].setGain(self.output_mixes[1],int(gain_r))


    def onSelect(self, e):
        menu = wx.Menu()
        for item in self.channels[0].getInputChoices():
            idnumber = wx.NewId()
            menu.Append(idnumber, item, "some help text")
            menu.Bind(wx.EVT_MENU, self.onMenuSelect)
        self.PopupMenu(menu, (0,0))
        menu.Destroy()

    def onMenuSelect(self, event):
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        self.channels[0].setInput(menuItem.GetItemLabel())


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

    def addMatrixInput(self, panel, channels, output_mixes):
        channelInputStrip = ChannelInputStrip(panel, 
                channels, 
                output_mixes)
        return channelInputStrip

    
    def InitUI(self):

        # Update using observer pattern or timers??
        # Probably observer 
        # TODO: Strip out timer stuff
        self.timer = wx.Timer(self, 1)
        self.count = 0

        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.volumes = wx.BoxSizer(wx.HORIZONTAL)
        
        self.timer = wx.Timer(self, wx.NewId())
        self.channel_input_strips = []
        for channel in self.mixer.getInputChannels():
            inputer = self.addMatrixInput(
                    self, 
                    [channel],
                    self.output_mixes)
            self.channel_input_strips.append(inputer)
            self.volumes.Add(inputer)
        
        self.Bind(
            wx.EVT_TIMER,
            self.reloadAllChannels,
            self.timer)

        # Poll for controll changes every 200ms
        self.timer.Start(200)

        vbox.Add((0, 20))
        vbox.Add(self.volumes, proportion=1)

        self.SetSizer(vbox)
        self.Centre()

    def reloadAllChannels(self, e):
        if self.mixer.poll():
            for vol in self.channel_input_strips:
                vol.reloadFromChannel()

    def OnOk(self, e):
        
        if self.count >= TASK_RANGE:
            return

        self.timer.Start(100)
        self.text.SetLabel('Task in Progress')

    def OnStop(self, e):
        if self.count == 0 or self.count >= TASK_RANGE or not self.timer.IsRunning():
            return

        self.timer.Stop()
        self.text.SetLabel('Task Interrupted')
        
    def OnTimer(self, e):
        
        self.count = self.count + 1
        self.gauge.SetValue(self.count)
        
        if self.count == TASK_RANGE:

            self.timer.Stop()
            self.text.SetLabel('Task Completed')

class MixerConsoleMixes(wx.Notebook):
    def __init__(self,parent,mixer):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP)
        tabOne = MixPanel(self, mixer, ["A", "B"])
#        tabOne.SetBackgroundColour("Gray")
#        scrollWin.SetScrollbars( 0, x,  0, y+1 )
#       scrollWin.SetScrollRate( 1, 1 )      # Pixels per scroll increment
#        scrollWin.SetBestSize((100,100))

        self.AddPage(tabOne, "A+B Mix")
        self.AddPage(MixPanel(self,mixer, ["C", "D"]), "C+D Mix")
        self.AddPage(MixPanel(self,mixer, ["E", "F"]), "E+F Mix")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

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


class MixerConsoleFrame(wx.Frame):
    def __init__(self, parent, mixer):
        wx.Frame.__init__(self, parent, title="Scarlett Mixer", size=(200,100))
        panel = wx.Panel(self)
        self.mixer = mixer
        mixesConsole = MixerConsoleMixes(panel,mixer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(mixesConsole, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Show()
#        self.InitUI()

