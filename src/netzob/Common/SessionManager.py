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
import logging
pygtk.require('2.0')

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------

#+----------------------------------------------
#| SessionManager:
#|     GUI for session manager at a project level
#+----------------------------------------------
class SessionManager:

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

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the main netzob object
    #+----------------------------------------------
    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger('netzob.Common.SessionManager.py')

        self.initPanel()

        self.dialog = gtk.Dialog(title="Session manager", flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(600, 400)
        self.update()

    def initPanel(self):
        # First we create an VPaned which hosts the two main children
        self.panel = gtk.HBox()
        self.panel.show()

        # Display symbols
        symbols = self.netzob.getCurrentProject().getVocabulary().getSymbols()

        ## ListStore format:
        # str: symbol.id
        # str: symbol.name
        treeview = gtk.TreeView(gtk.ListStore(str, str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Symbols")
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)

        for symbol in symbols:
            treeview.get_model().append([symbol.getID(), symbol.getName()])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        self.panel.pack_start(scroll)

        # Display sessions
        sessions = self.netzob.getCurrentProject().getVocabulary().getSessions()

        ## ListStore format:
        # str: session.id
        # str: session.name
        treeview = gtk.TreeView(gtk.ListStore(str, str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Sessions")
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)

        for session in sessions:
            treeview.get_model().append([session.getID(), session.getName()])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        self.panel.pack_start(scroll)

        # Display messages
        messages = self.netzob.getCurrentProject().getVocabulary().getAllMessages()

        ## ListStore format:
        # str: message.id
        # str: message.data
        treeview = gtk.TreeView(gtk.ListStore(str, str))
        treeview.set_size_request(500, 300)
        treeview.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Messages")
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)

        for message in messages:
            treeview.get_model().append([message.getID(), message.getStringData()])

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        self.panel.pack_start(scroll)
        

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
