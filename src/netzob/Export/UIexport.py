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
import logging

pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
import RawExport
import ScapyExport

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UIexport :
#|     GUI for exporting results
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIexport:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.rawPanel.update()
        self.scapyPanel.update()

    def clear(self):
        self.rawPanel.clear()
        self.scapyPanel.clear()

    def kill(self):
        self.rawPanel.kill()
        self.scapyPanel.kill()
    
    def save(self, file):
        self.rawPanel.save()
        self.scapyPanel.save()
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Export.UIexport.py')
        self.zob = zob
        self.panel = gtk.HPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing panels
        #+----------------------------------------------
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_LEFT)
        self.panel.add(notebook)

        # Network Capturing Panel
        self.rawPanel = RawExport.RawExport(self.zob)
        notebook.append_page(self.rawPanel.getPanel(), gtk.Label("Raw Export"))

        # IPC Capturing Panel
        self.scapyPanel = ScapyExport.ScapyExport(self.zob)
        notebook.append_page(self.scapyPanel.getPanel(), gtk.Label("Scapy dissector"))
