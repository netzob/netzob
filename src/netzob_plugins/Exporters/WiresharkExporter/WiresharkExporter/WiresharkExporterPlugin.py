# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.ExporterPlugin import ExporterPlugin
from netzob.Common.Plugins.Extensions.ExportMenuExtension import ExportMenuExtension
from WiresharkExporterController import WiresharkExporterController


class WiresharkExporterPlugin(ExporterPlugin):
    """
    Wireshark dissector generator
    """
    __plugin_name__ = "WiresharkExporter"
    __plugin_version__ = "0.1"
    __plugin_description__ = _("Generate a LUA script used by Wireshark to dissect specific symbols.")
    __plugin_author__ = "Alexandre PIGNÉ <alex@freesenses.net>"
    __plugin_copyright__ = "AMOSSYS"
    __plugin_license__ = "GPLv3+"

    def __init__(self, netzobb):
        super(WiresharkExporterPlugin, self).__init__(netzobb)
        self.controller = WiresharkExporterController(netzobb, self)
        self.entry_points = [ExportMenuExtension(netzobb, self.controller,
                                                 "wiresharkExporter", "Wireshark LUA script")]

    def getEntryPoints(self):
        """getEntryPoints:

                @rtype: netzob_plugins.Exporters.WiresharkExporter.EntryPoints.GlobalMenuEntryPoint.GlobalMenuEntryPoint
                @return: the plugin entry point, so it can be linked to the netzob project.
        """
        return self.entry_points
