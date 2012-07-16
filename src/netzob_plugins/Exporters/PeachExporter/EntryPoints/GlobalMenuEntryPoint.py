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
#| Global Imports                                                            |
#+---------------------------------------------------------------------------+
import logging
import gtk
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Local Imports                                                             |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.Extensions.GlobalMenuExtension import GlobalMenuExtension
from netzob.Common.Menu import Menu
from netzob_plugins.Exporters.PeachExporter.PeachExportController import PeachExportController


class GlobalMenuEntryPoint(GlobalMenuExtension):
    """GlobalMenuEntryPoint:
            Entry points in the menu for the peach exporter plugin.
    """

    def __init__(self, netzob):
        """Constructor of GlobalMenuEntryPoint:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob

    def getMenuEntries(self):
        """getMenuEntries:

                @rtype: string tuple list
                @return: the menu entry points.
        """
        menuEntries = [
                       (Menu.PATH_PROJECT_EXPORTPROJECT + "/" + _("Peach pit file"), None, self.executeAction, 0, None)
                       ]
        return menuEntries

    def executeAction(self, widget, data):
        """executeAction:
                Launch the Peach exporter GUI.

                @type widget: Gtk.widget
                @param widget: Not used.
                @type data:
                @param data: Not used.
        """
        PeachExportController(self.netzob)
