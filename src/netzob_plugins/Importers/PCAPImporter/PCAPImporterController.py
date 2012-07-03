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
from netzob.Common.Plugins.Importers.AbstractImporterController import AbstractImporterController
from netzob.UI.NetzobWidgets import NetzobErrorMessage
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED

class PCAPImporterController(AbstractImporterController):
    """Controller of PCAP importer plugin"""

    COLUMN_ID = 0
    COLUMN_SELECTED = 1

    def __init__(self, netzob):
        super(PCAPImporterController, self).__init__(netzob)
        self.model = PCAPImporter(self.netzob.getCurrentWorkspace(),
                                  self.currentProject)
        self.view = PCAPImporterView(self)

    def doSetSourceFiles(self, filePathList):
        self.model.setSourceFiles(filePathList)

    def doReadMessages(self):
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

    def doGetMessageDetails(self, messageID):
        return self.model.getMessageDetails(messageID)

    def doImportMessages(self, selectedPackets):
        self.model.saveMessagesInProject(selectedPackets)

    def clearFilterButton_clicked_cb(self, widget):
        self.view.filterEntry.clear()
