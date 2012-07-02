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
from gi.repository import Gtk

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob_plugins.Importers.PCAPImporter.PCAPImporter import PCAPImporter
from netzob_plugins.Importers.PCAPImporter.PCAPImporterView import PCAPImporterView
from netzob.Common.NetzobException import NetzobImportException
from netzob.UI.NetzobWidgets import NetzobErrorMessage
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED

class PCAPImporterController(object):
    """Controller of PCAP importer plugin"""

    def __init__(self, netzob):
        self.netzob = netzob
        self.log = logging.getLogger(__name__)
        self.currentProject = self.netzob.getCurrentProject()
        self.model = PCAPImporter(self.netzob.getCurrentWorkspace(),
                                  self.currentProject)
        self.view = PCAPImporterView(self)
        self.selectedPacketCount = 0

    def run(self):
        self.view.pcapImportDialog.show_all()
        self.view.hideWarning()

    @property
    def selectedPackets(self):
        return [row[0] for row in self.view.listListStore
                           if row[1]]

    def openFile(self, widget):
        chooser = Gtk.FileChooserDialog(title=_("Open PCAP file"),
            parent=self.netzob,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                      Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        chooser.set_filename(self.view.openFileEntry.get_text().strip())
        self.view.hideWarning()
        self.view.clearPacketView()

        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            filePath = chooser.get_filename()
            chooser.destroy()
            try:
                self.model.setSourceFiles([filePath])
                self.view.openFileEntry.set_text(filePath)
            except NetzobImportException, importEx:
                NetzobErrorMessage(importEx.message)
        else:
            chooser.destroy()

    def readMessages(self, widget=None):
        self.view.hideWarning()
        self.view.clearPacketView()
        self.selectedPacketCount = 0

        # Read PCAP file using PCAPImporter
        try:
            self.model.setBPFFilter(self.view.filterEntry.get_text().strip())
            self.model.readMessages()
        except NetzobImportException, importEx:
            if importEx.statusCode == WARNING:
                self.view.showWarning(importEx.message)
            else:
                NetzobErrorMessage(importEx.message)

        # Display all read messages
        for message in self.model.messages:
            self.view.listListStore.append([str(message.getID()), False,
                        str(message.getProtocol()),
                        str(message.getIPSource()), str(message.getIPDestination()),
                        str(message.getL4SourcePort()), str(message.getL4DestinationPort()),
                        str(message.getStringData())])

        # Update packet counters
        self.updateCounters()

    def clickedClearFilterButton(self, widget):
        self.view.filterEntry.clear()

    def clickedSelectAllButton(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[1] = True
            self.selectedPacketCount += 1
        self.updateCounters()

    def clickedUnselectAllButton(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[1] = False
        self.updateCounters()

    def clickedInvertSelectionButton(self, widget):
        self.selectedPacketCount = 0
        for row in self.view.listListStore:
            row[1] = (not row[1])
            if row[1]:
                self.selectedPacketCount += 1
        self.updateCounters()

    def changedListTVSelection(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            messageID = uuid.UUID(model[treeiter][0])
            self.view.detailTextView.get_buffer().set_text(
                    str(self.model.getMessageDetails(messageID)))

    def selectPacket(self, cellRenderer, path):
        iter = self.view.listListStore.get_iter(path)
        if(self.view.listListStore.iter_is_valid(iter)):
            packetID = uuid.UUID(self.view.listListStore[iter][0])
            selected = self.view.listListStore[iter][1]
            newSelectState = (not selected)
            self.view.listListStore[iter][1] = newSelectState
            if newSelectState:
                self.selectedPacketCount += 1
            else:
                self.selectedPacketCount -= 1
        self.updateCounters()

    def clickedImportButton(self, widget):
        selectedPackets = self.selectedPackets
        selectedCount = len(selectedPackets)
        if selectedCount != 0:
            currentProjectName = self.currentProject.getName()
            md = Gtk.MessageDialog(
                    self.view.pcapImportDialog, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
                    _("Are you sure to you want to import the {0} selected packets "
                      + "in project {1}").format(selectedCount, currentProjectName))
            result = md.run()
            md.destroy()
            if result == Gtk.ResponseType.YES:
                self.model.saveMessagesInProject(selectedPackets)
                self.view.pcapImportDialog.destroy()
                self.netzob.update()

    def updateCounters(self):
        displayedPackets = self.view.listListStore.iter_n_children(None)
        self.view.updateCounters(displayedPackets, self.selectedPacketCount)
