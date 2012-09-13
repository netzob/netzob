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
import uuid
from datetime import datetime
import logging

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Field import Field
from netzob.Common.ProjectConfiguration import ProjectConfiguration
from netzob.Common.ImportedTrace import ImportedTrace
from netzob.Common.Symbol import Symbol
from netzob.Common.Session import Session
from netzob.Common.NetzobException import NetzobImportException
from netzob.UI.ModelReturnCodes import ERROR
from netzob.UI.Import.Controllers.ConfirmImportMessagesController import ConfirmImportMessagesController


class AbstractImporter(object):
    """Abstract class which provides common methods too any kind of importers"""

    def __init__(self, type, netzob):
        self.type = type
        self.messages = []
        self.netzob = netzob
        self.status_cb = None
        self.end_cb = None

    def saveMessagesInCurrentProject(self, messageIDList):
        """Retrieve messages from the provided list of IDs
        and add them to the current project"""
        addMessages = []
        # Compute the step
        step = float(100.0 / float(len(messageIDList)))
        status = 0.0
        old_status = 0.0
        for messageID in messageIDList:
            message = self.getMessageByID(str(messageID))
            if message is not None:
                addMessages.append(message)
            else:
                errorMessage = _("Message ID: {0} not found in importer message list").format(messageID)
                raise NetzobImportException("PCAP", errorMessage, ERROR)
            status += step

            if self.status_cb is not None:
                self.status_cb(status, None)
                old_status = status

        self.saveMessagesInProject(self.netzob.getCurrentWorkspace(), self.netzob.getCurrentProject(), addMessages)

    def saveMessagesInProject(self, workspace, project, messages):
        """Add a selection of messages to an existing project
           it also saves them in the workspace"""

        if self.end_cb is not None:
            self.end_cb(workspace, project, self.type, messages)
        else:
            confirmController = ConfirmImportMessagesController(workspace, project, self.type, messages)
            confirmController.run()

    def getMessageByID(self, strID):
        selectedMessage = None
        for message in self.messages:
            if str(message.getID()) == strID:
                selectedMessage = message
                break

        return selectedMessage

    def saveMessages(self):
        self.saveMessagesInProject(self.netzob.getCurrentWorkspace(), self.netzob.getCurrentProject(), self.messages)
