# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
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
#| UIfuzzing:
#|     GUI for fuzzing applications
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
    #| Constructor:
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
