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
from abc import abstractmethod
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin


class FileImporterPlugin(NetzobPlugin):
    """Abstract base class for all file importer plugins"""

    PLUGIN_PRIORITY = 1

    def __init__(self, netzob):
        NetzobPlugin.__init__(self, netzob)
        self.finish = None

    @abstractmethod
    def canHandleFile(self, filePath):
        """Checks if the file at filePath can be handled by this
        importer plugin"""
        pass

    @abstractmethod
    def getFileTypeDescription(self):
        """Returns a string representation
        (eg "PCAP file" or "XML file")"""
        pass

    @abstractmethod
    def importFile(self, filePathList):
        """Imports message located in file at filePath"""
        pass

    def setFinish_cb(self, finish):
        """Define the callback function which should be executed by the
        plugin when he has finished to import messages."""
        self.finish = finish
