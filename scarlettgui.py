import wx

TASK_RANGE = 50

class ChannelInputStrip(wx.BoxSizer):
    def __init__(self,panel,inputs,current_input):
        # TODO: Implement Stereo Mixers/Stereo Binding
        wx.BoxSizer.__init__(self,wx.VERTICAL)
        volumeAndMeterBarContainer = wx.BoxSizer(wx.HORIZONTAL)
        height = 250
        decebil_range = 50
        slider = wx.Slider(
                panel,
                value=200,
                minValue=150,
                maxValue=500,
 #               pos=(20, 20),
                size=(-1, height), 
                style=(wx.SL_VERTICAL|wx.SL_INVERSE))
        slider.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        # TODO make the combo_box use current_input to select the
        # right input automaticaly
        combo_box = wx.Choice(
                panel, 
                choices=inputs)
        
        gauge = wx.Gauge(
                panel, 
                range=decebil_range, 
                size=(25, height),
                style=wx.GA_VERTICAL)

        combo_box.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        volumeAndMeterBarContainer.Add(slider)
        volumeAndMeterBarContainer.Add(gauge)
        
        self.Add(combo_box)
        self.Add(volumeAndMeterBarContainer)

    def OnSliderScroll(self, e):
        print e

    def OnSelect(self, e):
        print e

class MixerConsoleFrame(wx.Frame):
    def __init__(self, parent, mixer):
        wx.Frame.__init__(self, parent, title="Scarlett Mixer", size=(200,100))
        self.mixer = mixer
        self.InitUI()

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

        panel = wx.Panel(self)



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
                    panel, 
                    input_channels,
                    current_value)
            self.volumes.Add(inputer)

        vbox.Add((0, 20))
        vbox.Add(self.volumes, proportion=1)

        panel.SetSizer(vbox)
        
        self.SetSize((1000, 1000))
        self.SetTitle('Scarlett Mixer')
        self.Centre()
        self.Show(True)     


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
