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
from gettext import gettext as _
from gi.repository import Gtk
import gi
import logging
gi.require_version('Gtk', '3.0')

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

        self.dialog = Gtk.Dialog(title=_("Session manager"), flags=0, buttons=None)
        self.dialog.set_default_size(800, 600)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.update()

    def initPanel(self):
        self.panel = Gtk.HBox(False, spacing=0)
        self.panel.show()

        self.initPanelSymbol()
        self.initPanelSession()

    def initPanelSymbol(self):
        ## Symbol list box
        symbolBox = Gtk.VBox()
        symbolBox.show()
        frame = NetzobFrame(_("Symbol list"))
        frame.add(symbolBox)
        self.panel.pack_start(frame, True, True, 0)

        # Display symbols
        symbols = self.netzob.getCurrentProject().getVocabulary().getSymbols()

        # ListStore format:
        #   str: symbol.id
        #   str: symbol.name
        treeview = Gtk.TreeView(Gtk.ListStore(str, str))
        treeview.set_size_request(500, 200)
        treeview.show()
        selection = treeview.get_selection()
        selection.connect("changed", self.symbolSelected_cb)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Symbols"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        treeview.append_column(column)

        for symbol in symbols:
            treeview.get_model().append([symbol.getID(), symbol.getName()])

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        symbolBox.pack_start(scroll, True, True, 0)

#        label = NetzobLabel("Symbol name: ")
#        symbolBox.pack_start(label, True, True, 0)
#        label = NetzobLabel("Description: ")
#        symbolBox.pack_start(label, True, True, 0)

        ## Symbol box messages content
        messages = self.netzob.getCurrentProject().getVocabulary().getMessages()
        # ListStore format:
        #   str: message.id
        #   str: message.data
        self.treeview_symbol_messages = Gtk.TreeView(Gtk.ListStore(str, str))
        self.treeview_symbol_messages.set_size_request(-1, 300)
        self.treeview_symbol_messages.show()

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Messages"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        self.treeview_symbol_messages.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(self.treeview_symbol_messages)
        symbolBox.pack_start(scroll, True, True, 0)

    def initPanelSession(self):
        ## Session list
        sessionBox = Gtk.VBox()
        sessionBox.show()
        frame = NetzobFrame(_("Session list"))
        frame.add(sessionBox)
        self.panel.pack_start(frame, True, True, 0)

        # Display sessions
        sessions = self.netzob.getCurrentProject().getVocabulary().getSessions()
        # ListStore format:
        #   str: session.id
        #   str: session.name
        treeview = Gtk.TreeView(Gtk.ListStore(str, str))
        treeview.set_size_request(500, 200)
        treeview.show()
        selection = treeview.get_selection()
        selection.connect("changed", self.sessionSelected_cb)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Sessions"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        treeview.append_column(column)

        for session in sessions:
            treeview.get_model().append([session.getID(), session.getName()])

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(treeview)
        sessionBox.pack_start(scroll, True, True, 0)

#        label = NetzobLabel("Session name: ")
#        sessionBox.pack_start(label, True, True, 0)
#        label = NetzobLabel("Description: ")
#        sessionBox.pack_start(label, True, True, 0)

        ## Session content messages
        messages = self.netzob.getCurrentProject().getVocabulary().getMessages()
        # ListStore format:
        #   str: message.id
        #   str: message.data
        self.treeview_session_messages = Gtk.TreeView(Gtk.ListStore(str, str))
        self.treeview_session_messages.set_size_request(-1, 300)
        self.treeview_session_messages.show()

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Messages"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        self.treeview_session_messages.append_column(column)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.show()
        scroll.add(self.treeview_session_messages)
        sessionBox.pack_start(scroll, True, True, 0)

    #+----------------------------------------------
    #| CALLBACKS
    #+----------------------------------------------

    #+----------------------------------------------
    #| symbolSelected_cb:
    #|   callback when the user select a symbol
    #+----------------------------------------------
    def symbolSelected_cb(self, selection):
        self.treeview_symbol_messages.get_model().clear()

        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if project.getVocabulary() is None:
            NetzobErrorMessage(_("The current project doesn't have any referenced vocabulary."))
            return

        # Show messages contained in selected symbol
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                symbol_id = model.get_value(iter, 0)
                symbol = project.getVocabulary().getSymbol(symbol_id)
                if symbol is not None:
                    for message in symbol.getMessages():
                        self.treeview_symbol_messages.get_model().append([message.getID(), message.getStringData()])

    #+----------------------------------------------
    #| sessionSelected_cb:
    #|   callback when the user select a session
    #+----------------------------------------------
    def sessionSelected_cb(self, selection):
        self.treeview_session_messages.get_model().clear()

        # Sanity checks
        project = self.netzob.getCurrentProject()
        if project is None:
            NetzobErrorMessage(_("No project selected."))
            return
        if project.getVocabulary() is None:
            NetzobErrorMessage(_("The current project doesn't have any referenced vocabulary."))
            return

        # Show messages contained in selected session
        (model, iter) = selection.get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                session_id = model.get_value(iter, 0)
                session = project.getVocabulary().getSession(session_id)
                if session is not None:
                    for message in session.getMessages():
                        self.treeview_session_messages.get_model().append([message.getID(), message.getStringData()])

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
