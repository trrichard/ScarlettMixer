import wx
# Import the easiest to use scrolledpanel.
import wx.lib.scrolledpanel as scrolled

TASK_RANGE = 50

class ChannelInputStrip(wx.Panel):
    def __init__(
            self,
            parent,
            inputs,
            current_input,
            channel_count=1,
            ):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        if channel_count > 2:
            raise "Input Strips with > 2 channels not supported yet"
        # TODO: Implement Stereo Mixers/Stereo Binding
        volumeAndMeterBarContainer = wx.BoxSizer(wx.HORIZONTAL)
        height = 250
        width = 100
        decebil_range = 50
        pan = wx.Slider(
                self,
                value=50,
                minValue=0,
                maxValue=100,
#               pos=(20, 20),
                size=(width, -1), 
                style=(wx.SL_HORIZONTAL))
        gain = wx.Slider(
                self,
                value=200,
                minValue=150,
                maxValue=500,
#               pos=(20, 20),
                size=(-1, height), 
                style=(wx.SL_VERTICAL|wx.SL_INVERSE))
        gain.Bind(wx.EVT_SCROLL, self.OnSliderScroll)

        # TODO make the combo_box use current_input to select the
        # right input automaticaly
        combo_box = wx.ComboBox(
                self, 
                choices=inputs,
                size=(width,-1))
        if current_input:
            combo_box.SetStringSelection(current_input)
        
        gauge = wx.Gauge(
                self, 
                range=decebil_range, 
                size=(25, height),
                style=wx.GA_VERTICAL)

        combo_box.Bind(wx.EVT_COMBOBOX, self.OnSelect)

        volumeAndMeterBarContainer.Add(gain)
        volumeAndMeterBarContainer.Add(gauge)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(combo_box)
        sizer.Add(volumeAndMeterBarContainer)
        sizer.Add(pan)
        self.SetSizer(sizer)

    def OnSliderScroll(self, e):
        pass

    def OnSelect(self, e):
        pass


class MixPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, mixer):
        scrolled.ScrolledPanel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.mixer = mixer
        self.InitUI()
        self.SetAutoLayout(1)
        self.SetupScrolling()
    
    def OnSelect(self, e):
        pass

    def addMatrixInput(self, panel, inputs, current_input):
        channelInputStrip = ChannelInputStrip(panel, inputs, current_input)
        return channelInputStrip

    
    def InitUI(self):
        matrix_inputs = len(self.mixer.getMatrix())

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
        input_channels = self.mixer.getHardwareInputMuxChannels()
        input_channels.extend(self.mixer.getSoftwareInputMuxChannels())

        for i in range(0,matrix_inputs):
            current_value = None
            if i in self.mixer.getMatrixMuxMap():
                current_value = self.mixer.getMatrixMuxMap()[i]
            inputer = self.addMatrixInput(
                    self, 
                    input_channels,
                    current_value)
            self.volumes.Add(inputer)

        vbox.Add((0, 20))
        vbox.Add(self.volumes, proportion=1)

        self.SetSizer(vbox)
        
#        self.SetSize((1000, 1000))
#        self.SetTitle('Scarlett Mixer')
        self.Centre()
#        self.Show(True)     


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
        tabOne = MixPanel(self, mixer)
#        tabOne.SetBackgroundColour("Gray")
#        scrollWin.SetScrollbars( 0, x,  0, y+1 )
#       scrollWin.SetScrollRate( 1, 1 )      # Pixels per scroll increment
#        scrollWin.SetBestSize((100,100))

        self.AddPage(tabOne, "A+B Mix")
        self.AddPage(MixPanel(self,mixer), "C+D Mix")
        self.AddPage(MixPanel(self,mixer), "E+F Mix")

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

