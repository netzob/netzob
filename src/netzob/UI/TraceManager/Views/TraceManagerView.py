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
from gi.repository import Gtk
import logging
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractPerspectiveView import NetzobAbstractPerspectiveView


class TraceManagerView(NetzobAbstractPerspectiveView):

    def __init__(self, controller):
        gladeFile = os.path.join("traceManager", "traceManagerView.glade")
        menubar = os.path.join("traceManager", "traceManagerMenuToolbar.ui")
        popupFile = os.path.join("traceManager", "popupMenu.ui")

        super(TraceManagerView, self).__init__(controller,
                                               gladeFile,
                                               root="TraceManagerView",
                                               uiMenuBar=menubar,
                                               actionGroup="actionGroup")

        self._getObjects(["traceTreeview",
                          "traceTreestore",
                          "messageListTreeview",
                          "traceTreeviewSelection",
                          "traceNameEntry",
                          "traceDescriptionEntry",
                          "traceImportDate",
                          "traceDataType",
                          "currentTraceMessageListstore",
                          ])

        self.uiManager = Gtk.UIManager()
        self.uiManager.insert_action_group(self.actionGroup)
        self.uiManager.add_ui_from_file(self._findUiResource(popupFile))

        # Getting popup for the Trace List
        self.traceListPopup = self.uiManager.get_widget("/TraceListPopupMenu")
