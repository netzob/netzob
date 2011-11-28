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
import pygtk
pygtk.require('2.0')
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Fuzzing.Network import Network
from netzob.Fuzzing.Ipc import Ipc
from netzob.Fuzzing.File import File


#+---------------------------------------------- 
#| UIfuzzing :
#|     GUI for fuzzing applications
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class UIfuzzing:
    def new(self):
        pass

    def update(self):
        self.netPanel.update()
        self.ipcPanel.update()
        self.filePanel.update()

    def clear(self):
        self.netPanel.clear()
        self.ipcPanel.clear()
        self.filePanel.clear()

    def kill(self):
        self.netPanel.kill()
        self.ipcPanel.kill()
        self.filePanel.kill()
    
    def save(self, file):
        self.netPanel.save()
        self.ipcPanel.save()
        self.filePanel.save()

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
        self.panel.add(notebook)

        # Network Capturing Panel
        self.netPanel = Network(self.netzob)
        notebook.append_page(self.netPanel.getPanel(), gtk.Label("Network fuzzing"))

        # IPC Capturing Panel
        self.ipcPanel = Ipc(self.netzob)
        notebook.append_page(self.ipcPanel.getPanel(), gtk.Label("IPC fuzzing"))

        # File Panel
        self.filePanel = File(self.netzob)
        notebook.append_page(self.filePanel.getPanel(), gtk.Label("File fuzzing"))
