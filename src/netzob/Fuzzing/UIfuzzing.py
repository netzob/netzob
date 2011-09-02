#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import threading

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
import Network
import Ipc
import File

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UIfuzzing :
#|     GUI for fuzzing applications
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIfuzzing:
    def new(self):
        pass

    #+---------------------------------------------- 
    #| Update each sub-panels
    #+----------------------------------------------
    def update(self):
        self.netPanel.update()
        self.ipcPanel.update()
        self.filePanel.update()

    def clear(self):
        pass

    def kill(self):
        pass
    
    def save(self, file):
        pass

    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.UIfuzzing.py')
        self.netzob = netzob
        self.panel = gtk.HPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing panels
        #+----------------------------------------------
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.connect("switch-page", self.notebookFocus)
        self.panel.add(notebook)

        # Network Capturing Panel
        self.netPanel = Network.Network(self.netzob)
        notebook.append_page(self.netPanel.getPanel(), gtk.Label("Network fuzzing"))

        # IPC Capturing Panel
        self.ipcPanel = Ipc.IPC(self.netzob)
        notebook.append_page(self.ipcPanel.getPanel(), gtk.Label("IPC fuzzing"))

        # File Panel
        self.filePanel = File.File(self.netzob)
        notebook.append_page(self.filePanel.getPanel(), gtk.Label("File fuzzing"))

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
