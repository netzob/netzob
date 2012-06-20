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
import random
from netzob.Common.Plugins.ImporterPlugin import ImporterPlugin
from netzob_plugins.Importers.FileImporter.EntryPoints.GlobalMenuEntryPoint import GlobalMenuEntryPoint
from netzob_plugins.Importers.FileImporter.FileImportController import FileImportController

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| FileImporter: Import messages from files
#+---------------------------------------------------------------------------+
class FileImporterPlugin(ImporterPlugin):

    __plugin_name__ = "FileImporter"
    __plugin_version__ = "1.0"
    __plugin_description__ = "This is a File Importer"
    __plugin_author__ = "Georges Bossert <georges.bossert@supelec.fr>"

    def __init__(self, netzob):
        ImporterPlugin.__init__(self, netzob)
        self.entryPoints = []
        # create the menu entry point
        self.entryPoints.append(GlobalMenuEntryPoint(self.getNetzob()))

    def getName(self):
        return self.__plugin_name__

    def getEntryPoints(self):
        return self.entryPoints

    def setVal(self, val):
        self.val = val
