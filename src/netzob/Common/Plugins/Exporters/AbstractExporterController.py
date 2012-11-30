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
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.AbstractPluginController import AbstractPluginController


class AbstractExporterController(AbstractPluginController):
    """AbstractExporterController:
        Abstract controller for exporters plugins
    """

    def __init__(self, netzob, plugin):
        """Constructor of AbstractExporterController:

            @type netzob: netzob.NetzobGUI.NetzobGUI
            @param netzob: the current neztob project.
            @type plugin: netzob.Common.Plugins.ExporterPlugin.ExporterPlugin
            @param plugin: the plugin that encapsulates this controller.
        """
        super(AbstractExporterController, self).__init__(netzob, plugin)
        self.log = logging.getLogger(__name__)
        self.selectedPacketCount = 0

    def run(self):
        """run:
            Show the plugin view.
        """
        self.view.dialog.show_all()
        self.view.hideWarning()
