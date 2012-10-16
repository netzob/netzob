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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Plugins.Importers.AbstractFileImporterController import AbstractFileImporterController
from OSpyImporter import OSpyImporter
from OSpyImporterView import OSpyImporterView


class OSpyImporterController(AbstractFileImporterController):
    COLUMN_ID = 1
    COLUMN_SELECTED = 0

    def __init__(self, netzob, plugin):
        super(OSpyImporterController, self).__init__(netzob, plugin)
        self.model = OSpyImporter(netzob)
        self.view = OSpyImporterView(plugin, self)

    def run(self):
        self.view.run()

    def doSetSourceFiles(self, filePathList):
        self.model.setSourceFiles(filePathList)

    def doReadMessages(self):
        self.model.readMessages()
        for message in self.model.messages:
            self.view.listListStore.append([False, str(message.getID()), str(message.getL3SourceAddress()), str(message.getL3DestinationAddress()), str(message.getL4Protocol()), str(message.getL4SourcePort()), str(message.getL4DestinationPort()), message.getStringData()])

    def doGetMessageDetails(self, messageID):
        message = self.model.getMessageByID(str(messageID))
        return TypeConvertor.hexdump(TypeConvertor.netzobRawToPythonRaw(message.getData()))

    def doImportMessages(self, selectedMessages):
        self.model.saveMessagesInCurrentProject(selectedMessages)
