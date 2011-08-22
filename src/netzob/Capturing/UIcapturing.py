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
import gobject
import pygtk
pygtk.require('2.0')
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
import network
import pcap
import api
import ipc
import fileImport

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UIcapturing :
#|     GUI for capturing messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIcapturing:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        pass

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
    def __init__(self, zob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.UIseqMessage.py')
        self.zob = zob
        self.panel = gtk.HPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing types
        #+----------------------------------------------
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.connect("switch-page", self.notebookFocus)
        self.panel.add(notebook)

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing panels
        #+----------------------------------------------
        # Network Capturing Panel
        netPanel = network.Network(self.zob)
        notebook.append_page(netPanel.getPanel(), gtk.Label("Network Capturing"))

        # IPC Capturing Panel
        ipcPanel = ipc.IPC(self.zob)
        notebook.append_page(ipcPanel.getPanel(), gtk.Label("IPC Capturing"))

        # API Panel
        apiPanel = api.Api(self.zob)
        notebook.append_page(apiPanel.getPanel(), gtk.Label("API capturing"))

        # PCAP Panel
        pcapPanel = pcap.Pcap(self.zob)
        notebook.append_page(pcapPanel.getPanel(), gtk.Label("PCAP import"))

        # File Panel
        filePanel = fileImport.FileImport(self.zob)
        notebook.append_page(filePanel.getPanel(), gtk.Label("File import"))

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        
