# -*- coding: utf-8 -*-
#
#       pvg_common.py
#
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

#       Revisions by Caitlin Laughrey and Loretta E Laughrey in 2016.

# %%                                                            for debugging
"""
Prints file, class, and function names and line number for each definition.
- turn this on/off by replacing '# debugprt(' with '# # debugprt(' or vice versa.
"""
from inspect import currentframe        
from db import debugprt                 

# %%                                                             imports
import wx, cv, os        
import pysolovideo as pv
import ConfigParser, threading

"""
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   "Global Variables"
"""
pgm = 'pvg_common.py'

#vDEFAULT_CONFIG = 'pysolo_video.cfg'

# ----------------------------------------------------------------------------
""" 
File I/O is assumed to use the GitHub\LL-DAM-Analysis folder in the current 
 user's documents folder.
"""  
#import ctypes.wintypes   # used to get path to current user's documents folder
#CSIDL_PERSONAL = 5          # My Documents
#SHGFP_TYPE_CURRENT = 0      # Get current, not default value
#buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)  # get user document folder path
#ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

#
#root_dir = 'D:\\LL-DAM-Analysis\\'
#data_dir = root_dir + 'Data\\20160823_135217\\4ROI_pfps\\'
#data_dir = root_dir + 'Data\\Working_files\\'
# %%                                                start & zero datetimes
"""
dates for setting the correct date information for output
 - get datetime for adjusting from 31 Dec 1969 at 19:01:00
 - set start date and time of video
"""
import datetime
t = datetime.time(19, 1, 00)    
d = datetime.date(1969, 12, 31)
zero_dt = datetime.datetime.combine(d, t)
""" - set date and time that video was actually recorded """                    #     <--- can we get this from the filename's datetime stamp?
start_dt = datetime.datetime(2016,8,23,13,52,17)



# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  MyConfig
class myConfig():
    """
    Handles program configuration
    Uses ConfigParser to store and retrieve
    From gg's toolbox
    """
    def __init__(self, filename=None, temporary=False, defaultOptions=None):
        # debugprt(self,currentframe(),pgm,'begin     ')        
        """
        filename    the name of the configuration file
        temporary   whether we are reading and storing values temporarily
        defaultOptions  a dict containing the defaultOptions
        """

        filename = filename or pv.DEFAULT_CONFIG
        pDir = pv.data_dir
#        if not os.access(pDir, os.W_OK): pDir = os.environ['HOME']
        
        self.filename = os.path.join (pDir, filename)
        self.filename_temp = '%s~' % self.filename

        self.config = None

        if defaultOptions != None:
            self.defaultOptions = defaultOptions
        else:
            self.defaultOptions = { "option_1" : [0, "Description"],
                                    }

        self.Read(temporary)
        # debugprt(self,currentframe(),pgm,'end   ')

# %%                                                        New config file
    def New(self, filename):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.filename = filename
        self.Read()
        # debugprt(self,currentframe(),pgm,'end   ')

# %%                                                        Read config file
    def Read(self, temporary=False):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        read the configuration file. Initiate one if does not exist

        temporary       True                Read the temporary file instead
                        False  (Default)     Read the actual file
        """

        if temporary: filename = self.filename_temp
        else: filename = self.filename

        
        print('$$$$$$  pvg_common: myconfig: 133:  read:  filename = ',filename)            # debug
        
        if os.path.exists(filename):
            self.config = ConfigParser.RawConfigParser()                                  
            self.config.read(filename)

        else:
            self.Save(temporary, newfile=True)
        # debugprt(self,currentframe(),pgm,'end   ')


# %%                                                        Save config file
    def Save(self, temporary=False, newfile=False, filename=None):                  # saves options configuration
        # debugprt(self,currentframe(),pgm,'begin     ')        
        """
        """

        if temporary and not filename: filename = self.filename_temp
        elif not temporary and not filename: filename = self.filename

        if newfile:
            self.config = ConfigParser.RawConfigParser()                               
            self.config.add_section('Options')
           
            for key in self.defaultOptions:
                self.config.set('Options', key, self.defaultOptions[key][0])

        with open(filename, 'wb') as configfile:
            self.config.write(configfile)

        if not temporary: self.Save(temporary=True)
        # debugprt(self,currentframe(),pgm,'end   ')


# %%                                                     Set Values in Config
    def SetValue(self, section, key, value):
        # debugprt(self,currentframe(),pgm,'begin     ')                                # debug
        """
        puts configuration values in config file
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, value)
        # debugprt(self,currentframe(),pgm,'end   ')

# %%                                                    Get values from config
    def GetValue(self, section, key):
        # debugprt(self,currentframe(),pgm,'begin     ')                                # debug
        """
        get value from config file
        Does some sanity checking to return tuple, integer and strings
        as required.
        """
        r = self.config.get(section, key)

        if type(r) == type(0) or type(r) == type(1.0):  # native int and float
            # debugprt(self,currentframe(),pgm,'end   ')
            return r
        elif type(r) == type(True):                     # native boolean
            # debugprt(self,currentframe(),pgm,'end   ')
            return r
        elif type(r) == type(''):
            r = r.split(',')

        if len(r) == 2:                                 # tuple
            r = tuple([int(i) for i in r]) 

        elif len(r) < 2:                                # string or integer
            try:
                r = int(r[0])                           # int as text
            except:
                if len(r) > 0:
                    r = r[0]                            # string
                else:
                    r = ""

        if r == 'False' or r == 'True':
            r = (r == 'True')                           # bool

        # debugprt(self,currentframe(),pgm,'end   ')
        return r


# %%                                   Get value from options section of config
    def GetOption(self, key):
        # debugprt(self,currentframe(),pgm,'begin     ')        
        """
        """
        a = self.GetValue('Options', key)
        # debugprt(self,currentframe(),pgm,'end   ')
        return a


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Acquire Object        
class acquireObject():
    def __init__(self, monitor, source, resolution, mask_file, track, track_type, dataFolder):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.monitor = monitor
        self.keepGoing = False
        self.verbose = True                                                        # false turns off debug
        self.track = track
        dataFolder = options.GetOption("Data_Folder")
        outputFile = os.path.join(dataFolder, 'Monitor%02d.txt' % monitor)

        self.mon = pv.Monitor()
        self.mon.setSource(source, resolution)
        self.mon.setTracking(True, track_type, mask_file, outputFile)

        if self.verbose: print("$$$$$$ Verbose 247 - Monitor %s, track %s, track type %d, \n source %s, \n mask %s,  \n output file %s  "
                               % (monitor, track, track_type,
                                  source,
                                  mask_file,
                                  outputFile) )
        # debugprt(self,currentframe(),pgm,'end   ')
        
# %%                                                        Run
    def run(self, kbdint=False):
        debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        checks to see if program should keep going.
        """
        while self.keepGoing:
            self.keepGoing = self.mon.GetImage()
        # debugprt(self,currentframe(),pgm,'end   ')

# %%                                                        Start
    def start(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.keepGoing = True
        self.run()
        # debugprt(self,currentframe(),pgm,'end   ')

# %%                                                            Halt
    def halt(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.keepGoing = False
        if self.verbose: print ( "$$$$$$ Verbose: Stopping capture" )
        # debugprt(self,currentframe(),pgm,'end   ')


        
class acquireThread(threading.Thread):

    def __init__(self, monitor, source, resolution, mask_file, track, track_type, dataFolder):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        threading.Thread.__init__(self)
        self.monitor = monitor
        self.keepGoing = False
        self.verbose = True
        self.track = track
        outputFile = os.path.join(dataFolder, 'Monitor%02d.txt' % (monitor+1))   # account for computer indexing diff from humans

        self.mon = pv.Monitor()
        self.mon.setSource(source, resolution)
        self.mon.setTracking(True, track_type, mask_file, outputFile)

        if self.verbose: print("$$$$$$ Verbose 301 - Monitor %s, track %s, track type %d, \n source %s, \n mask %s,  \n output file %s  "
                               % (monitor, track, track_type,
                                  source,
                                  mask_file,
                                  outputFile) )
        # debugprt(self,currentframe(),pgm,'end   ')
        
    def run(self, kbdint=False):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """

        if kbdint:

            while self.keepGoing:
                try:
                    self.mon.GetImage()
                except KeyboardInterrupt:
                    self.halt()

        else:
            while self.keepGoing:
                self.mon.GetImage()
        # debugprt(self,currentframe(),pgm,'end   ')

    def doTrack(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.keepGoing = True
        self.start()
        # debugprt(self,currentframe(),pgm,'end   ')

    def halt(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.keepGoing = False
        if self.verbose: print ( "$$$$$$ Verbose 339: Stopping capture" )
        # debugprt(self,currentframe(),pgm,'end   ')

class pvg_config(myConfig):
    """
    Inheriting from myConfig
    """
    def __init__(self, filename=None, temporary=False):
        # debugprt(self,currentframe(),pgm,'begin     ')                                      # debug

        defaultOptions = { 
            "Monitors" :      [9, "Select the number of monitors connected to this machine"],
            "Webcams"  :      [1, "Select the number of webcams connected to this machine"],
            "ThumbnailSize" : ['320, 240', "Specify the size for the thumbnail previews"],
            "FullSize" :      ['640, 480', "Specify the size for the actual acquisition from the webcams.\nMake sure your webcam supports this definition"],
            "FPS_preview" :   [5, "Refresh frequency (FPS) of the thumbnails during preview.\nSelect a low rate for slow computers"],
            "FPS_recording" : [5, "Actual refresh rate (FPS) during acquisition and processing"],
            "Data_Folder" :   [pv.data_dir, "Folder where the final data are saved"]
             }

        self.monitorProperties = ['sourceType', 'source', 'track', 'maskfile', 'trackType', 'isSDMonitor']

        myConfig.__init__(self, filename, temporary, defaultOptions)
        # debugprt(self,currentframe(),pgm,'end   ')

    def SetMonitor(self, monitor, *args):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        mn = 'Monitor%s' % monitor
        for v, vn in zip( args, self.monitorProperties ):
            self.SetValue(mn, vn, v)
        # debugprt(self,currentframe(),pgm,'end   ')

    def GetMonitor(self, monitor):
        # debugprt(self,currentframe(),pgm,'begin     ')                                           # debug
        """
        """
        mn = 'Monitor%s' % monitor
        md = []
        if self.config.has_section(mn):
            for vn in self.monitorProperties:
                md.append ( self.GetValue(mn, vn) )
        # debugprt(self,currentframe(),pgm,'end   ')
        return md

    def HasMonitor(self, monitor):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        mn = 'Monitor%s' % monitor
        a = self.config.has_section(mn)
        # debugprt(self,currentframe(),pgm,'end   ')
        return a

    def getMonitorsData(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                           # debug
        """
        return a list containing the monitors that we need to track
        based on info found in configfile
        """
        monitors = {}

        ms = self.GetOption('Monitors')
        resolution = self.GetOption('FullSize')
        dataFolder = self.GetOption('Data_Folder')
        
        for mon in range(0,ms):
            if self.HasMonitor(mon):
                _,source,track,mask_file,track_type,isSDMonitor = self.GetMonitor(mon)
                monitors[mon] = {}
                monitors[mon]['source'] = source
                monitors[mon]['resolution'] = resolution
                monitors[mon]['mask_file'] = mask_file
                monitors[mon]['track_type'] = track_type
                monitors[mon]['dataFolder'] = dataFolder
                monitors[mon]['track'] = track
                monitors[mon]['isSDMonitor'] = isSDMonitor

        # debugprt(self,currentframe(),pgm,'end   ')
        return monitors



class previewPanel(wx.Panel):
    """
    A panel showing the video images.
    Used for thumbnails
    """
    def __init__(self, parent, size, keymode=True):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug

        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.WANTS_CHARS)

        self.parent = parent

        self.size = size
        self.SetMinSize(self.size)
        fps = options.GetOption('FPS_preview') or 25
        self.interval = 1000/fps # fps determines refresh interval in ms

        self.SetBackgroundColour('#A9A9A9')

        self.sourceType = 0
        self.source = ''
        self.mon = None
        self.track = False
        self.isSDMonitor = False
        self.trackType = 1
        self.drawROI = True
        self.timestamp = False
        self.camera = None
        self.resolution = None

        self.recording = False
        self.isPlaying = False

        self.allowEditing = True
        self.dragging = None        # Set to True while dragging
        self.startpoints = None     # Set to (x,y) when mouse starts drag
        self.track_window = None    # Set to rect when the mouse drag finishes
        self.selection = None
        self.selROI = -1
        self.polyPoints = []
        self.keymode = keymode

        self.ACTIONS = {
                        "a": [self.AutoMask, "Automatically create the mask"],
                        "c": [self.ClearLast, "Clear last selected area of interest"],
                        "t": [self.Calibrate, "Calibrate the mask after selecting two points distant 1cm from each other"],
                        "x": [self.ClearAll, "Clear all marked region of interest"],
                        "j": [self.SaveCurrentSelection, "Save last marked area of interest"],
                        "s": [self.SaveMask, "Save mask to file"],
                        "q": [self.Stop, "Close connection to camera"]
                        }

        self.Bind( wx.EVT_LEFT_DOWN, self.onLeftDown )
        self.Bind( wx.EVT_LEFT_UP, self.onLeftUp )
        #self.Bind( wx.EVT_LEFT_DCLICK, self.AddPoint )
        self.Bind( wx.EVT_LEFT_DCLICK, self.SaveCurrentSelection )
        self.Bind( wx.EVT_MOTION, self.onMotion )
        self.Bind( wx.EVT_RIGHT_DOWN, self.ClearLast )
        #self.Bind( wx.EVT_MIDDLE_DOWN, self.SaveCurrentSelection )

        if keymode:
            self.Bind( wx.EVT_CHAR, self.onKeyPressed )
            self.SetFocus()
        # debugprt(self,currentframe(),pgm,'end   ')

    def ClearAll(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        Clear all ROIs
        """
        self.mon.delROI(-1)
        # debugprt(self,currentframe(),pgm,'end   ')

    def ClearLast(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        Cancel current drawing
        """

        if self.allowEditing:
            self.selection = None
            self.polyPoints = []

            if self.selROI >= 0:
                self.mon.delROI(self.selROI)
                self.selROI = -1
        # debugprt(self,currentframe(),pgm,'end   ')

    def SaveCurrentSelection(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        save current selection
        """
        if self.allowEditing and self.selection:
            self.mon.addROI(self.selection, 1)
            self.selection = None
            self.polyPoints = []
        # debugprt(self,currentframe(),pgm,'end   ')

    def AddPoint(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        Add point
        """

        if self.allowEditing:
            if len(self.polyPoints) == 4:
                self.polyPoints = []

            #This is to avoid selecting a neigh. area when drawing point
            self.selection = None
            self.selROI = -1

            x = event.GetX()
            y = event.GetY()
            self.polyPoints.append( (x,y) )
        # debugprt(self,currentframe(),pgm,'end   ')


    def onLeftDown(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """

        if self.allowEditing and self.mon:
            x = event.GetX()
            y = event.GetY()
            r = self.mon.isPointInROI ( (x,y) )

            if r < 0:
                self.startpoints = (x, y)
            else:
                self.selection = self.mon.getROI(r)
                self.selROI = r
        # debugprt(self,currentframe(),pgm,'end   ')

    def onLeftUp(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        if self.allowEditing:
            self.dragging = None
            self.track_window = self.selection

            if len(self.polyPoints) == 4:
                self.selection = self.polyPoints
                self.polyPoints = []
        # debugprt(self,currentframe(),pgm,'end   ')

    def onMotion(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                 # debug
        """
        """
        if self.allowEditing:
            x = event.GetX()
            y = event.GetY()

            self.dragging = event.Dragging()

            if self.dragging:
                xmin = min(x, self.startpoints[0])
                ymin = min(y, self.startpoints[1])
                xmax = max(x, self.startpoints[0])
                ymax = max(y, self.startpoints[1])

                x1, y1, x2, y2  = (xmin, ymin, xmax, ymax)
                self.selection = (x1,y1), (x2,y1), (x2,y2), (x1, y2)
        # debugprt(self,currentframe(),pgm,'end   ')

    def prinKeyEventsHelp(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        for key in self.ACTIONS:
            print "%s\t%s" % (key, self.ACTIONS[key][1])
        # debugprt(self,currentframe(),pgm,'end   ')

    def onKeyPressed(self, event):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        Regulates key pressing responses:
        """
        key = chr(event.GetKeyCode())

        if key == "g" and self.mon.writer: self.mon.grabMovie = not self.mon.grabMovie

        if self.ACTIONS.has_key(key):
            self.ACTIONS[key][0]()
        # debugprt(self,currentframe(),pgm,'end   ')

    def Calibrate(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        if len(self.polyPoints) > 2:
            print "You need only two points for calibration. I am going to use the first two"

        if len(self.polyPoints) > 1:
            pt1, pt2 = self.polyPoints[0], self.polyPoints[1]
            r = self.mon.calibrate(pt1, pt2)
            self.polyPoints = []
        else:
            print "You need at least two points for calibration."

        print "%spixels = 1cm" % r
        # debugprt(self,currentframe(),pgm,'end   ')

    def AutoMask(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        if len(self.polyPoints > 1):
            pt1, pt2 = self.polyPoints[0], self.polyPoints[1]
            self.mon.autoMask(pt1, pt2)
        else:
            print "Too few points to automask"
        self.polyPoints = []
        # debugprt(self,currentframe(),pgm,'end   ')

    def SaveMask(self, event=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.mon.saveROIS()
        # debugprt(self,currentframe(),pgm,'end   ')

    def setMonitor(self, camera, resolution=None):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """

        if not resolution: resolution = self.size

        self.camera = camera
        self.resolution = resolution
        self.mon = pv.Monitor()

        frame = cv.CreateMat(self.size[1], self.size[0], cv.CV_8UC3)
        self.bmp = wx.BitmapFromBuffer(self.size[0], self.size[1], frame.tostring())

        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.playTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onNextFrame)
        # debugprt(self,currentframe(),pgm,'end   ')


    def paintImg(self, img):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        if img:
            depth, channels = img.depth, img.nChannels
            datatype = cv.CV_MAKETYPE(depth, channels)
            print('$$$$$$ common, paintimg, ln 675, datatype= ',datatype)

            frame = cv.CreateMat(self.size[1], self.size[0], datatype)
            cv.Resize(img, frame)

            cv.CvtColor(frame, frame, cv.CV_BGR2RGB)
            #cv.CvtColor(frame, frame, cv.CV_GRAY2RGB)

            self.bmp.CopyFromBuffer(frame.tostring())
            self.Refresh()
        # debugprt(self,currentframe(),pgm,'end   ')

    def onPaint(self, evt):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        if self.bmp:
            dc = wx.BufferedPaintDC(self)
            #self.PrepareDC(dc)
            dc.DrawBitmap(self.bmp, 0, 0, True)
        evt.Skip()
        # debugprt(self,currentframe(),pgm,'end   ')

    def onNextFrame(self, evt):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        img = self.mon.GetImage(drawROIs = self.drawROI, selection=self.selection, crosses=self.polyPoints, timestamp=self.timestamp)
        self.paintImg( img )
        if evt: evt.Skip()
        # debugprt(self,currentframe(),pgm,'end   ')

    def Play(self, status=True, showROIs=True):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """

        if self.camera != None and self.resolution != None and not self.mon.hasSource():
            self.mon.setSource(self.camera, self.resolution)

        if self.mon:
            self.drawROI = showROIs
            self.isPlaying = status

            if status:
                self.playTimer.Start(self.interval)
            else:
                self.playTimer.Stop()
        # debugprt(self,currentframe(),pgm,'end   ')

    def Stop(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        self.Play(False)
        self.mon.close()
        # debugprt(self,currentframe(),pgm,'end   ')

    def hasMonitor(self):
        # debugprt(self,currentframe(),pgm,'begin     ')                                            # debug
        """
        """
        a = (self.mon != None)
        # debugprt(self,currentframe(),pgm,'end   ')
        return a

#################
                                                  # DEBUG

options = pvg_config(pv.DEFAULT_CONFIG)