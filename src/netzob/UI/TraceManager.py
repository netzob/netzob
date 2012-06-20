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

#+---------------------------------------------------------------------------+
#| Global Imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
from gi.repository import Gtk
import gi
import logging
import uuid
from gi.repository import GObject
gi.require_version('Gtk', '3.0')
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobLabel, NetzobComboBoxEntry, \
    NetzobButton, NetzobProgressBar
from netzob.Common.Threads.Job import Job
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask
from netzob.Common.Symbol import Symbol
from netzob.Common.Field import Field


#+---------------------------------------------------------------------------+
#| TraceManager:
#|     This class displays the GUI to manage all the manipulated traces in a
#|     workspace
#+---------------------------------------------------------------------------+
class TraceManager():
    #+-----------------------------------------------------------------------+
    #| Constructor:
    #| @param workspace : the current workspace
    #+-----------------------------------------------------------------------+
    def __init__(self, workspace, cb_update):
        self.workspace = workspace

        self.createDialog()

        self.updateContent()
        self.cb_update = cb_update
        self.cb_update()

    def createDialog(self):
        self.dialog = Gtk.Dialog(title=_("Trace Manager"), flags=0, buttons=None)
        self.dialog.set_default_size(800, 600)
        mainTable = Gtk.Table(rows=2, columns=1, homogeneous=False)

        scroll = Gtk.ScrolledWindow()
        self.treestoreTraces = Gtk.TreeStore(str, str, str, str, str, int)  # id, date, type, project name, description, nb message,
        treeview = Gtk.TreeView(self.treestoreTraces)
        treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        treeview.connect('button-press-event', self.button_press_on_treeview_traces)

        cell = Gtk.CellRendererText()
        # Col Date
        column = Gtk.TreeViewColumn(_("Date"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col Type
        column = Gtk.TreeViewColumn(_("Type"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col project name
        column = Gtk.TreeViewColumn(_("Original project"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        # Col Description
        column = Gtk.TreeViewColumn(_("Description"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        treeview.append_column(column)
        # Col Nb message
        column = Gtk.TreeViewColumn(_("Nb messages"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=5)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        mainTable.attach(scroll, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        scroll2 = Gtk.ScrolledWindow()
        self.treestoreMessages = Gtk.TreeStore(str, str, str)  # id, timestamp, data,
        treeviewMessage = Gtk.TreeView(self.treestoreMessages)
        treeviewMessage.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
#        treeview.connect("cursor-changed", self.packet_details)

        cell = Gtk.CellRendererText()
        # Col ID
        column = Gtk.TreeViewColumn(_("ID"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeviewMessage.append_column(column)
        # Col Type
        column = Gtk.TreeViewColumn(_("Timestamp"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeviewMessage.append_column(column)
        # Col project name
        column = Gtk.TreeViewColumn(_("Data"))
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeviewMessage.append_column(column)

        treeviewMessage.show()
        scroll2.add(treeviewMessage)
        scroll2.show()
        scroll2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        mainTable.attach(scroll2, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()

    def updateContentMessage(self, trace=None):
        self.treestoreMessages.clear()
        if trace != None:
            for message in trace.getMessages():
                self.treestoreMessages.append(None, [str(message.getID()), str(message.getTimestamp()), str(message.getData())])

    def updateContent(self):
        self.treestoreTraces.clear()
        for trace in self.workspace.getImportedTraces():
            id = str(trace.getID())
            date = str(trace.getDate())
            type = str(trace.getType())
            name = str(trace.getName())
            description = str(trace.getDescription())
            nbMessage = len(trace.getMessages())
            self.treestoreTraces.append(None, [id, date, type, name, description, nbMessage])

    #+----------------------------------------------
    #| button_press_on_treeview_symbols:
    #|   operation when the user click on the treeview.
    #|   mainly to open a contextual menu
    #+----------------------------------------------
    def button_press_on_treeview_traces(self, treeview, event):
        x = int(event.x)
        y = int(event.y)
        selectedTrace = None

        info = treeview.get_path_at_pos(x, y)

        if info is not None:
            path = info[0]
            iter = treeview.get_model().get_iter(path)
            idTrace = str(treeview.get_model().get_value(iter, 0))
            if idTrace is not None:
                for trace in self.workspace.getImportedTraces():
                    if str(trace.getID()) == idTrace:
                        selectedTrace = trace
        if selectedTrace == None:
            logging.warn("The provided ID do not match any trace.")
            return

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1 and selectedTrace != None:
            self.updateContentMessage(selectedTrace)

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.show_menu_trace(event, selectedTrace)

    #+----------------------------------------------
    #| show_menu_trace:
    #|   Create a menu to display available operations for a trace
    #+----------------------------------------------
    def show_menu_trace(self, event, trace):
        entries = [
                  (Gtk.STOCK_ADD, self.importTrace, (trace != None)),
                  (Gtk.STOCK_REMOVE, self.deleteTrace, (trace != None))
       ]

        menu = Gtk.Menu()
        for stock_id, callback, sensitive in entries:
            item = Gtk.ImageMenuItem(stock_id)

            item.connect("activate", callback, trace)
            item.set_sensitive(sensitive)
            item.show()
            menu.append(item)
        menu.popup(None, None, None, event.button, event.time)

    def importTrace(self, event, trace):
        importDialog = Gtk.Dialog(title=_("Import selected Trace in a project"), flags=0, buttons=None)
        panel = Gtk.Table(rows=4, columns=2, homogeneous=False)
        panel.show()

        # Label
        label = NetzobLabel(_("Trace ID"))
        panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        label2 = NetzobLabel(trace.getID())
        panel.attach(label2, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        label3 = NetzobLabel(_("Select project"))
        panel.attach(label3, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        # Delimiter type
        projectCombo = NetzobComboBoxEntry()
        for project in self.workspace.getProjects():
            projectCombo.append_text(project.getName())

        panel.attach(projectCombo, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Progress bar
        self.progressbarAlignment = NetzobProgressBar()
        panel.attach(self.progressbarAlignment, 0, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Button
        importButton = NetzobButton(_("Import"))
        importButton.connect("clicked", self.importTraceAction, trace, projectCombo, importDialog)
        panel.attach(importButton, 0, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        importDialog.vbox.pack_start(panel, True, True, 0)
        importDialog.show()

    def importTraceAction(self, event, trace, projectCombo, dialog):
        selectedProject = None
        selectedProjectName = projectCombo.get_active_text()
        for project in self.workspace.getProjects():
            if project.getName() == selectedProjectName:
                selectedProject = project

        if selectedProject == None:
            logging.warn("Impossible to retrieve the selected project based on its name " + str(selectedProjectName))
            return

        # Start the import job
        Job(self.startImport(trace, selectedProject, dialog))

    def startImport(self, trace, project, dialog):
        self.currentExecutionOfAlignmentHasFinished = False
        (yield ThreadedTask(self.importTraceInProject, trace, project))
        self.currentExecutionOfAlignmentHasFinished = True
        dialog.destroy()
        (yield ThreadedTask(self.cb_update))

    def importTraceInProject(self, trace, project):
        percent = 0.0
        inc = 1.0 / len(trace.getMessages())
        # We create a symbol dedicated for the trace
        symbol = Symbol(uuid.uuid4(), trace.getType(), project)
        for message in trace.getMessages():
            percent += inc
            symbol.addMessage(message)
            GObject.idle_add(self.progressbarAlignment.set_fraction, float(percent))

        # We create a default field for the symbol
        symbol.addField(Field.createDefaultField())
        # and register the symbol in the vocabulary of the project
        project.getVocabulary().addSymbol(symbol)
        project.saveConfigFile(self.workspace)

    def deleteTrace(self, event, trace):
        questionMsg = _("Click yes to remove selected trace {0} from the Trace Manager").format(trace.getID())
        md = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, questionMsg)
        result = md.run()
        md.destroy()
        if result == Gtk.ResponseType.YES:
            self.workspace.removeImportedTrace(trace)
            self.updateContent()
            self.updateContentMessage()
        else:
            self.log.debug(_("The user didn't confirm the deletion of the trace {0}").format(trace.getID()))
