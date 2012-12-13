import wx
import socket
import wx.richtext
from datetime import datetime
from wx.lib.pubsub import Publisher
from threading import Thread
import hashlib
from time import sleep
import getpass

MAX_MESSAGE_LENGTH = 1024

[
wxID_FRAME1, wxID_FRAME1BUTTON1, wxID_FRAME1LISTBOX1, wxID_FRAME1STATICTEXT1,
wxID_FRAME1TEXTCTRL1,wxID_FRAME1HOMEPANEL
] = [wx.NewId() for _init_ctrls in range(6)]

def create(parent):
    return Frame1(parent, '127.0.0.1', 12581)


class SendMsg(Thread):
    def __init__(self, s, message, username):
        self.s = s
        self.message = message
        self.username = username
        Thread.__init__(self)

    def run(self):
        try:
            if self.message!="":
                self.message = " " + self.username + " : " + self.message + '\n'
                self.s.send(self.message)

        except Exception, e:
            exit(1)
            wx.MutexGuiEnter()
            Publisher().sendMessage("PrintMsg", str(e))
            wx.MutexGuiLeave()


class ReceiveMsg(Thread):
    def __init__(self, s):
        self.s = s
        Thread.__init__(self)

    def run(self):
        while 1:
            try:
                data = self.s.recv(MAX_MESSAGE_LENGTH)
                wx.MutexGuiEnter()
                if data:
                    Publisher().sendMessage("PrintMsg", data)
                wx.MutexGuiLeave()
            except:
                exit(1)

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):

        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(183, 110), size=wx.Size(793, 597),
              style=wx.DEFAULT_FRAME_STYLE, title='Chat')

        self.SetClientSize(wx.Size(785, 570))

        #PANELS
        self.homepanel = wx.Panel(id=wxID_FRAME1HOMEPANEL, name=u'homepanel',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(793,
              597), style=wx.TAB_TRAVERSAL)

        image_file = 'background.png'

        bmp = wx.Bitmap(image_file)
        ##FOR THE BG : (I changed the parent from self.panel1 => self.bitmap)
        self.bitmap1 = wx.StaticBitmap(self.homepanel, wx.ID_ANY, bmp, (0, 0))

        self.textCtrl1 = wx.richtext.RichTextCtrl(id=wxID_FRAME1TEXTCTRL1, name='textCtrl1',
              parent=self.homepanel, pos=wx.Point(24, 496), size=wx.Size(600, 60),
            value='', style=wx.TE_MULTILINE)
        #self.textCtrl1.SetBackgroundColour((0,0,0))
        self.textCtrl1.SetEditable(1)
        self.textCtrl1.Bind(wx.EVT_KEY_DOWN, self.onKeyPressed)


        self.content = wx.richtext.RichTextCtrl(id=wxID_FRAME1LISTBOX1,
              name='content', parent=self.homepanel, pos=wx.Point(24, 56),
              size=wx.Size(736, 424), style=wx.TE_MULTILINE)
        self.content.SetEditable(0)
        self.content.BeginFontSize(9)
        #self.content.BeginTextColour((244,225,173))
        #self.content.SetBackgroundColour((0,0,0))

        self.button1 = wx.Button(id=wxID_FRAME1BUTTON1, label='Send',
              name='button1', parent=self.homepanel, pos=wx.Point(640, 503),
              size=wx.Size(92, 47), style=0)
        self.button1.SetForegroundColour((230,225,173))
        self.button1.SetBackgroundColour((71,71,71))

        self.button1.Bind(wx.EVT_BUTTON, self.SendMessage)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label='Chat Logs', name='staticText1', parent=self.homepanel,
              pos=wx.Point(328, 16), size=wx.Size(92, 25), style=0)
        self.staticText1.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL,
              False, 'Envy Code R'))
        self.staticText1.SetForegroundColour((230,225,173))
        self.staticText1.SetBackgroundColour((71,71,71))

        Publisher().subscribe(self.AppendListBox, "PrintMsg")

    def __init__(self, parent, host, port):
        self.s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.passwd   = getpass.getpass(prompt='Enter Room Password:\n=> ',stream=None)
        self.username = raw_input("Enter Your Username:\n=> ")
        salt=""
        while(not salt.startswith("[+]") ):
            salt = self.s.recv(MAX_MESSAGE_LENGTH)
        salt = salt.replace("[+]","")
        self.s.send("[+]"+str(hashlib.sha512( ((hashlib.sha512(self.passwd)).hexdigest())+salt).hexdigest()  )        )
        sleep(2)
        try:
            self.s.send("[*] "+self.username+" Has join the chat\n\n")
        except:
            exit(1)
        self._init_ctrls(parent)
        ReceiveMsg(self.s).start()



    def AppendListBox(self, result):
        try:
            now = datetime.now()
            self.content.WriteText("{0:<1} {1}".format(now.strftime("[%H:%M:%S]") , result.data))
        except wx.PyDeadObjectError:
            sys.exit(0)


    def onKeyPressed(self, evt):
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_RETURN and evt.ShiftDown():
            self.textCtrl1.WriteText('\n')

        elif keycode == wx.WXK_RETURN:
            message = self.textCtrl1.GetValue()
            SendMsg(self.s, message, self.username).start()
            self.textCtrl1.SetValue("")

        else:
            evt.Skip()

    def SendMessage(self, evt):
        message = self.textCtrl1.GetValue()
        SendMsg(self.s, message, self.username).start()
        self.textCtrl1.SetValue("")


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()
