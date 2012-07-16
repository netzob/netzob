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
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
import uuid
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.AbstractPluginController import AbstractPluginController


class AbstractImporterController(AbstractPluginController):
    """Abstract controller for importers plugins"""

    def __init__(self, netzob, plugin):
        super(AbstractImporterController, self).__init__(netzob, plugin)
        self.log = logging.getLogger(__name__)
        self.selectedPacketCount = 0

    def run(self):
        self.view.dialog.show_all()
        self.view.hideWarning()

    @property
    def selectedMessages(self):
        return [row[self.COLUMN_ID] for row in self.view.listListStore
                if row[self.COLUMN_SELECTED]]

    def doReadMessages(self):
        raise NotImplementedError("Classes inheriting from AbstractImporterController must implement the doReadMessages method")

    def doGetMessageDetails(self, messageID):
        raise NotImplementedError("Classes inheriting from AbstractImporterController must implement the doGetMessageDetails method")

    def doImportMessages(self, selectedMessages):
        raise NotImplementedError("Classes inheriting from AbstractImporterController must implement the doImportMessages method")

    def readMessages(self, widget=None):
        self.view.hideWarning()
        self.view.clearPacketView()
        self.selectedPacketCount = 0
        self.doReadMessages()
        self.updateCounters()

    def selectAllButton_clicked_cb(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[self.COLUMN_SELECTED] = True
            self.selectedPacketCount += 1
        self.updateCounters()

    def unselectAllButton_clicked_cb(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[self.COLUMN_SELECTED] = False
        self.updateCounters()

    def invertSelectionButton_clicked_cb(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[self.COLUMN_SELECTED] = (not row[self.COLUMN_SELECTED])
            if row[self.COLUMN_SELECTED]:
                self.selectedPacketCount += 1
        self.updateCounters()

    def listTreeViewSelection_changed_cb(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            messageID = uuid.UUID(model[treeiter][self.COLUMN_ID])
            self.view.detailTextView.get_buffer().set_text(
                str(self.doGetMessageDetails(messageID)))

    def selectMessage(self, cellRenderer, path):
        iter = self.view.listListStore.get_iter(path)
        if(self.view.listListStore.iter_is_valid(iter)):
            selected = self.view.listListStore[iter][self.COLUMN_SELECTED]
            newSelectState = (not selected)
            self.view.listListStore[iter][self.COLUMN_SELECTED] = newSelectState
            if newSelectState:
                self.selectedPacketCount += 1
            else:
                self.selectedPacketCount -= 1
        self.updateCounters()

    def importButton_clicked_cb(self, widget):
        selectedMessages = self.selectedMessages
        selectedCount = len(selectedMessages)
        if selectedCount != 0:
            currentProjectName = self.getCurrentProject().getName()
            md = Gtk.MessageDialog(
                self.view.dialog, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
                _("Are you sure to you want to import the {0} selected packets in project {1}").format(selectedCount, currentProjectName))
            result = md.run()
            md.destroy()
            if result == Gtk.ResponseType.YES:
                self.doImportMessages(selectedMessages)
                self.view.dialog.destroy()
                self.netzob.update()

    def updateCounters(self):
        displayedPackets = self.view.listListStore.iter_n_children(None)
        self.view.updateCounters(displayedPackets, self.selectedPacketCount)
