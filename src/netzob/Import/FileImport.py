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
import uuid
import datetime
import logging
import os

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.FileMessage import FileMessage
from netzob.Common.EnvironmentalDependencies import EnvironmentalDependencies
from netzob.Import.AbstractImporter import AbstractImporter


#+----------------------------------------------
#| FileImport:
#|     GUI for capturing messages
#+----------------------------------------------
class FileImport(AbstractImporter):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        AbstractImporter.__init__(self, "FILE IMPORT")
        self.netzob = netzob
        self.log = logging.getLogger('netzob.Import.FileImport.py')

        # create the environmental dependancy object
        self.envDeps = EnvironmentalDependencies()

        self.messages = []
        self.filesToBeImported = []

    def getMessageByID(self, strID):
        selectedMessage = None
        for message in self.messages:
            if str(message.getID()) == strID:
                selectedMessage = message

        return selectedMessage

    #+----------------------------------------------
    #| Retrieve messages from files
    #+----------------------------------------------
    def retrieveMessagesFromFiles(self):
        # We capture the current environment
        self.envDeps.captureEnvData()

        # We read each file and create one message for each file
        fileNumber = 0
        self.messages = []

        for file in self.filesToBeImported:
            # Extraction of the metadata
            fileName = file.strip()
            size = os.path.getsize(file)
            creationDate = datetime.datetime.fromtimestamp(os.path.getctime(file))
            modificationDate = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            owner = "none"

            # Retrieve the binary content of the file
            content = self.getNetzobRawContentOfFile(file)
            if not len(content) > 0:
                continue

            # Create a message
            message = FileMessage(uuid.uuid4(), 0, content, fileName, creationDate, modificationDate, owner, size, 0)
            self.messages.append(message)
            fileNumber += 1

    def getNetzobRawContentOfFile(self, filename):
        file = open(filename, "rb")
        content = file.read()
        file.close()
        return TypeConvertor.stringToNetzobRaw(content)

    def applySeparatorOnFiles(self, lineSeparator):
        # We read each file and create one message for each file
        fileNumber = 0

        # We split the content of each message and retrieve new messages
        self.retrieveMessagesFromFiles()
        new_messages = []
        for message in self.messages:
            lineNumber = 0
            if len(lineSeparator) > 0:
                splittedStrHexData = message.getData().split(lineSeparator)
            else:
                splittedStrHexData = [message.getData()]
            for s in splittedStrHexData:
                if len(s) > 0:
                    message = FileMessage(uuid.uuid4(), 0, s, message.getFilename(), message.getCreationDate(), message.getModificationDate(), message.getOwner(), message.getSize(), lineNumber)
                    new_messages.append(message)
                    lineNumber += 1

        # We save the new messages
        self.messages = []
        self.messages.extend(new_messages)

    def saveMessages(self):
        self.saveMessagesInProject(self.netzob.getCurrentWorkspace(),
                                   self.netzob.getCurrentProject(),
                                   self.messages)
