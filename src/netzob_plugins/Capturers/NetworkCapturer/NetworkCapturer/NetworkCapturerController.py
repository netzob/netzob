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
import os
import time

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobInfoMessage, NetzobErrorMessage
from netzob.Common.Plugins.Capturers.AbstractCapturerController import AbstractCapturerController
from NetworkCapturerView import NetworkCapturerView
from NetworkCapturer import NetworkCapturer
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage
from netzob.Common.NetzobException import NetzobImportException


class NetworkCapturerController(AbstractCapturerController):
    """NetworkCapturerController:
            A controller liking the network capturer and its view in the netzob GUI.
    """

    COLUMN_ID = 0
    COLUMN_SELECTED = 1

    def __init__(self, netzob, plugin):
        """Constructor of NetworkCapturerController:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        super(NetworkCapturerController, self).__init__(netzob, plugin)
        self.netzob = netzob
        self.model = NetworkCapturer(netzob)
        self.view = NetworkCapturerView(plugin, self)
        for device in self.model.getNetworkDevices():
            self.view.deviceCombo.append_text(str(device))

    def getImportLayer(self):
        return self.model.importLayer

    def setImportLayer(self, importLayer):
        self.model.setImportLayer(importLayer)

    importLayer = property(getImportLayer, setImportLayer)

    def clearFilterButton_clicked_cb(self, widget):
        self.view.filterEntry.set_text("")

    def layerRadioButton_toggled_cb(self, widget):
        if self.view.layerRadioButton1.get_active():
            self.importLayer = 1
            self.view.makeL1ImportTreeView()
        elif self.view.layerRadioButton2.get_active():
            self.importLayer = 2
            self.view.makeL2ImportTreeView()
        elif self.view.layerRadioButton3.get_active():
            self.importLayer = 3
            self.view.makeL3ImportTreeView()
        else:
            self.importLayer = 4
            self.view.makeL4ImportTreeView()

    def doReadMessages(self):
        # Sanity checks
        device = self.view.deviceCombo.get_active_text()
        if device is None:
            NetzobErrorMessage(_("Incorrect device"))
            return
        count = self.view.countEntry.get_text()
        try:
            count = int(count)
        except ValueError:
            NetzobErrorMessage(_("Incorrect count"))
            return
        if count < 1:
            NetzobErrorMessage(_("Incorrect count"))
        time = self.view.timeEntry.get_text()
        try:
            time = int(time)
        except ValueError:
            NetzobErrorMessage(_("Incorrect time"))
            return
        if time < 1:
            NetzobErrorMessage(_("Incorrect time"))

        # Launch packets capturing
        try:
            self.model.setBPFFilter(self.view.filterEntry.get_text().strip())
            self.model.readMessages(self.callback_readMessage, device, count, time)
        except NetzobImportException, importEx:
            if importEx.statusCode == WARNING:
                self.view.showWarning(importEx.message)
            else:
                NetzobErrorMessage(importEx.message)

    def callback_readMessage(self, message):
        # Display all read messages
        if self.importLayer == 1:
            self.view.listListStore.append([str(message.getID()), False,
                                            message.getStringData()])
        elif self.importLayer == 2:
            self.view.listListStore.append([str(message.getID()), False,
                                            str(message.getL2SourceAddress()),
                                            str(message.getL2DestinationAddress()),
                                            message.getStringData()])
        elif self.importLayer == 3:
            self.view.listListStore.append([str(message.getID()), False,
                                            str(message.getL3SourceAddress()),
                                            str(message.getL3DestinationAddress()),
                                            message.getStringData()])
        else:
            self.view.listListStore.append([str(message.getID()), False,
                                            str(message.getL3SourceAddress()), str(message.getL3DestinationAddress()),
                                            str(message.getL4Protocol()), str(message.getL4SourcePort()), str(message.getL4DestinationPort()),
                                            message.getStringData()])

    def doGetMessageDetails(self, messageID):
        return self.model.getMessageDetails(messageID)

    def doImportMessages(self, selectedPackets):
        self.model.saveMessagesInCurrentProject(selectedPackets)
