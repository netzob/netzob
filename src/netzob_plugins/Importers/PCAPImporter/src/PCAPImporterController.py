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
from PCAPImporter import PCAPImporter
from PCAPImporterView import PCAPImporterView
from netzob.Common.NetzobException import NetzobImportException
from netzob.Common.Plugins.Importers.AbstractFileImporterController import AbstractFileImporterController
from netzob.UI.NetzobWidgets import NetzobErrorMessage
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED


class PCAPImporterController(AbstractFileImporterController):
    """Controller of PCAP importer plugin"""

    COLUMN_ID = 0
    COLUMN_SELECTED = 1

    def __init__(self, netzob, plugin):
        super(PCAPImporterController, self).__init__(netzob, plugin)
        self.model = PCAPImporter(netzob)
        self.view = PCAPImporterView(plugin, self)

    def getImportLayer(self):
        return self.model.importLayer

    def setImportLayer(self, importLayer):
        self.model.setImportLayer(importLayer)

    importLayer = property(getImportLayer, setImportLayer)

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
        if self.importLayer == 1:
            for message in self.model.messages:
                self.view.listListStore.append([str(message.getID()), False,
                                                message.getStringData()])
        elif self.importLayer == 2:
            for message in self.model.messages:
                self.view.listListStore.append([str(message.getID()), False,
                                                str(message.getL2SourceAddress()),
                                                str(message.getL2DestinationAddress()),
                                                message.getStringData()])
        elif self.importLayer == 3:
            for message in self.model.messages:
                self.view.listListStore.append([str(message.getID()), False,
                                                str(message.getL3SourceAddress()),
                                                str(message.getL3DestinationAddress()),
                                                message.getStringData()])
        else:
            for message in self.model.messages:
                self.view.listListStore.append([str(message.getID()), False,
                                                str(message.getL3SourceAddress()), str(message.getL3DestinationAddress()),
                                                str(message.getL4Protocol()), str(message.getL4SourcePort()), str(message.getL4DestinationPort()),
                                                message.getStringData()])

    def doGetMessageDetails(self, messageID):
        return self.model.getMessageDetails(messageID)

    def doImportMessages(self, selectedPackets):
        self.model.saveMessagesInCurrentProject(selectedPackets)

    def clearFilterButton_clicked_cb(self, widget):
        self.view.filterEntry.clear()

    def layerRadioButton_toggled_cb(self, widget):
        if self.view.layerRadioButton1.get_active():
            self.importLayer = 1
            self.view.makeL1ImportTreeView()
        elif self.view.layerRadioButton2.get_active():
            self.importLayer = 2
            self.view.makeL2ImportTreeView()
        elif self.view.layerRadioButton3.get_active():
            self.importLayer = 3
            self.view.makeL3ImportTreeView()
        else:
            self.importLayer = 4
            self.view.makeL4ImportTreeView()
