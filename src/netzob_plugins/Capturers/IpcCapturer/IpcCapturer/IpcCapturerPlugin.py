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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import uuid
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.CapturerPlugin import CapturerPlugin
from netzob.Common.Plugins.Extensions.CapturerMenuExtension import CapturerMenuExtension
from IpcCapturerController import IpcCapturerController
from netzob.UI.NetzobWidgets import NetzobErrorMessage


class IpcCapturerPlugin(CapturerPlugin):
    """IpcCapturerPlugin:
            Plugin that captures IPC traffic.
    """
    __plugin_name__ = "IpcCapturer"
    __plugin_version__ = "1.0"
    __plugin_description__ = _("Provide the possibility to capture IPC traffic.")
    __plugin_author__ = "Frédéric Guihéry <frederic.guihery@amossys.fr>"
    __plugin_copyright__ = "Georges Bossert and Frédéric Guihéry"
    __plugin_license__ = "GPLv3+"

    def __init__(self, netzob):
        """Constructor of IpcCapturerPlugin:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        super(IpcCapturerPlugin, self).__init__(netzob)
        self.netzob = netzob
        self.entryPoints = [CapturerMenuExtension(netzob, self.actionCallback, _("Capture IPC traffic"), _("Capture IPC traffic"))]

    def getName(self):
        """getName:

                @rtype: string
                @return: the plugin name.
        """
        return self.__plugin_name__

    def getVersion(self):
        """getVersion:

                @rtype: string
                @return: the plugin version.
        """
        return self.__plugin_version__

    def getDescription(self):
        """getDescription:

                @rtype: string
                @return: a plugin description.
        """
        return self.__plugin_description__

    def getAuthor(self):
        """getAuthor:

                @rtype: string
                @return: the plugin author.
        """
        return self.__plugin_author__

    def getEntryPoints(self):
        """getEntryPoints:

                @rtype: netzob_plugins.Capturers.IpcCapturer.EntryPoints.GlobalMenuEntryPoint.GlobalMenuEntryPoint
                @return: the plugin entry point, so it can be linked to the netzob project.
        """
        return self.entryPoints

    def setVal(self, val):
        """setVal:
                Useless function.

                @type val:
                @param val:
        """
        self.val = val

    def actionCallback(self, vocabularyView):
        """setVal:
                Callback when plugin is launched.

                @type val:
                @param val:
        """
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.finish = vocabularyView.updateSymbolList
        controller = IpcCapturerController(self.netzob, self)
        controller.run()
