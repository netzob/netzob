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
#| FileImporter:
#|     GUI for capturing messages
#+----------------------------------------------
class DelimiterSeparatedImporter(AbstractImporter):
    """Model of file importer plugin"""

    def __init__(self, netzob):
        super(DelimiterSeparatedImporter, self).__init__("FILE IMPORT", netzob)
        self.log = logging.getLogger('netzob.Import.FileImporter.py')

        # create the environmental dependancy object
        self.envDeps = EnvironmentalDependencies()
        self.importedFiles = []
        self.messageSeparator = ""

    def setSourceFiles(self, filePathList):
        self.importedFiles = []
        for filePath in filePathList:
            size = os.path.getsize(filePath)
            creationDate = datetime.datetime.fromtimestamp(
                os.path.getctime(filePath))
            modificationDate = datetime.datetime.fromtimestamp(
                os.path.getmtime(filePath))
            owner = "none"
            # Retrieve the binary content of the file
            content = self._getNetzobRawContentOfFile(filePath)
            if not len(content) > 0:
                continue
            # Create a message
            message = FileMessage(uuid.uuid4(), 0,
                                  content, filePath, creationDate,
                                  modificationDate, owner, size, 0)
            self.importedFiles.append(message)

    def setSeparator(self, separator):
        self.messageSeparator = separator

    def readMessages(self):
        # Iterate over all imported files and split them
        # according to the set separator
        self.messages = []
        for fileMessage in self.importedFiles:
            lineNumber = 0
            if len(self.messageSeparator) > 0:
                splittedStrHexData = fileMessage.getData().split(self.messageSeparator)
            else:
                splittedStrHexData = [fileMessage.getData()]
            for s in splittedStrHexData:
                if len(s) > 0:
                    message = FileMessage(uuid.uuid4(), 0,
                                          s, fileMessage.getFilename(), fileMessage.getCreationDate(),
                                          fileMessage.getModificationDate(), fileMessage.getOwner(),
                                          fileMessage.getSize(), lineNumber)
                    self.messages.append(message)

    def _getNetzobRawContentOfFile(self, filename):
        with open(filename, "rb") as file:
            content = file.read()
            content = TypeConvertor.stringToNetzobRaw(content)
        return content
