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
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobButton, NetzobFrame


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
        self.update()

    def initPanel(self):
        self.panel = gtk.HBox(False, spacing=0)
        self.panel.show()

        self.initPanelSymbol()
        self.initPanelSession()

    def initPanelSymbol(self):
        ## Symbol list box
        symbolBox = gtk.VBox()
        symbolBox.show()
        frame = NetzobFrame("Symbol list")
        frame.add(symbolBox)
        self.panel.pack_start(frame, True, True, 0)

        # Display symbols
        symbols = self.netzob.getCurrentProject().getVocabulary().getSymbols()

        # ListStore format:
        #   str: symbol.id
        #   str: symbol.name
        treeview = gtk.TreeView(gtk.ListStore(str, str))
        treeview.set_size_request(500, 200)
        treeview.show()
        treeview.connect('cursor-changed', self.symbolSelected_cb)

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
        symbolBox.pack_start(scroll)

#        label = NetzobLabel("Symbol name: ")
#        symbolBox.pack_start(label)
#        label = NetzobLabel("Description: ")
#        symbolBox.pack_start(label)

        ## Symbol box messages content
        messages = self.netzob.getCurrentProject().getVocabulary().getMessages()
        # ListStore format:
        #   str: message.id
        #   str: message.data
        self.treeview_symbol_messages = gtk.TreeView(gtk.ListStore(str, str))
        self.treeview_symbol_messages.set_size_request(-1, 300)
        self.treeview_symbol_messages.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Messages")
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.treeview_symbol_messages.append_column(column)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(self.treeview_symbol_messages)
        symbolBox.pack_start(scroll)

    def initPanelSession(self):
        ## Session list
        sessionBox = gtk.VBox()
        sessionBox.show()
        frame = NetzobFrame("Session list")
        frame.add(sessionBox)
        self.panel.pack_start(frame, True, True, 0)

        # Display sessions
        sessions = self.netzob.getCurrentProject().getVocabulary().getSessions()
        # ListStore format:
        #   str: session.id
        #   str: session.name
        treeview = gtk.TreeView(gtk.ListStore(str, str))
        treeview.set_size_request(500, 200)
        treeview.show()
        treeview.connect('cursor-changed', self.sessionSelected_cb)

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
        sessionBox.pack_start(scroll)

#        label = NetzobLabel("Session name: ")
#        sessionBox.pack_start(label)
#        label = NetzobLabel("Description: ")
#        sessionBox.pack_start(label)

        ## Session content messages
        messages = self.netzob.getCurrentProject().getVocabulary().getMessages()
        # ListStore format:
        #   str: message.id
        #   str: message.data
        self.treeview_session_messages = gtk.TreeView(gtk.ListStore(str, str))
        self.treeview_session_messages.set_size_request(-1, 300)
        self.treeview_session_messages.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Messages")
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.treeview_session_messages.append_column(column)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        scroll.add(self.treeview_session_messages)
        sessionBox.pack_start(scroll)

    #+----------------------------------------------
    #| CALLBACKS
    #+----------------------------------------------

    #+----------------------------------------------
    #| symbolSelected_cb:
    #|   callback when the user select a symbol
    #+----------------------------------------------
    def symbolSelected_cb(self, treeview):
        self.treeview_symbol_messages.get_model().clear()

        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project == None:
            NetzobErrorMessage("No project selected.")
            return
        if project.getVocabulary() == None:
            NetzobErrorMessage("The current project doesn't have any referenced vocabulary.")
            return

        # Show messages contained in selected symbol
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                symbol_id = model.get_value(iter, 0)
                symbol = project.getVocabulary().getSymbol(symbol_id)
                if symbol != None:
                    for message in symbol.getMessages():
                        self.treeview_symbol_messages.get_model().append([message.getID(), message.getStringData()])

    #+----------------------------------------------
    #| sessionSelected_cb:
    #|   callback when the user select a session
    #+----------------------------------------------
    def sessionSelected_cb(self, treeview):
        self.treeview_session_messages.get_model().clear()

        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project == None:
            NetzobErrorMessage("No project selected.")
            return
        if project.getVocabulary() == None:
            NetzobErrorMessage("The current project doesn't have any referenced vocabulary.")
            return

        # Show messages contained in selected session
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                session_id = model.get_value(iter, 0)
                session = project.getVocabulary().getSession(session_id)
                if session != None:
                    for message in session.getMessages():
                        self.treeview_session_messages.get_model().append([message.getID(), message.getStringData()])

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
