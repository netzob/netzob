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
from gettext import gettext as _
import fnmatch
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.FileImporterPlugin import FileImporterPlugin
from PCAPImporterController import PCAPImporterController


class PCAPImporterPlugin(FileImporterPlugin):
    """PCAPImporter: Provide the possibility to import messages
       from PCAP network capture files"""

    __plugin_name__ = "PCAPImporter"
    __plugin_version__ = "1.0"
    __plugin_description__ = _("Provide the possibility to import messages from PCAP network capture files")
    __plugin_author__ = "Georges Bossert <georges.bossert@supelec.fr>"
    __plugin_copyright__ = "Georges Bossert and Frédéric Guihéry"
    __plugin_license__ = "GPLv3+"

    FILE_TYPE_DESCRIPTION = "PCAP File"

    def __init__(self, netzob):
        super(PCAPImporterPlugin, self).__init__(netzob)
        self.entryPoints = []

    def getEntryPoints(self):
        return self.entryPoints

    def canHandleFile(self, filePath):
        return fnmatch.fnmatch(filePath, "*.pcap")

    def getFileTypeDescription(self):
        return self.FILE_TYPE_DESCRIPTION

    def importFile(self, filePathList):
        self.controller = PCAPImporterController(self.getNetzob(), self)
        self.controller.setSourceFiles(filePathList)
        self.controller.run()
