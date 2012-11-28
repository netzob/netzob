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
from IpcCapturerView import IpcCapturerView
from IpcCapturer import IpcCapturer
from netzob.Common.Models.IPCMessage import IPCMessage
from netzob.Common.NetzobException import NetzobImportException


class IpcCapturerController(AbstractCapturerController):
    """IpcCapturerController:
            A controller linking the IPC capturer and its view in the netzob GUI.
    """

    COLUMN_ID = 0
    COLUMN_SELECTED = 1

    def __init__(self, netzob, plugin):
        """Constructor of IpcCapturerController:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        super(IpcCapturerController, self).__init__(netzob, plugin)
        self.netzob = netzob
        self.model = IpcCapturer(netzob)
        self.view = IpcCapturerView(plugin, self)
        self.updateProcessList_cb(None)

    def updateProcessList_cb(self, button):
        """updateProcessList_cb:
                Called when user wants to update the process list
        """
        self.view.processCombo.get_model().clear()
        for process in self.model.getProcessList():
            self.view.processCombo.append_text(process)

    def updateFlowList_cb(self, button):
        """updateFlowList_cb:
                Called when user wants to update the flow list
        """
        self.view.fdStore.clear()
        processSelected = self.view.processCombo.get_active_text()
        if processSelected is None or processSelected == "":
            return
        self.model.pid = int(processSelected.split()[0])
        filter_fs = self.view.fsFilterButton.get_active()
        filter_net = self.view.networkFilterButton.get_active()
        filter_proc = self.view.ipcFilterButton.get_active()
        for fd in self.model.retrieveFDs(filter_fs, filter_net, filter_proc):
            self.view.fdStore.append(fd)

    def doReadMessages(self):
        # Launch packets capturing
        try:
            self.model.startSniff(self.callback_readMessage)
        except NetzobImportException, importEx:
            if importEx.statusCode == WARNING:
                self.view.showWarning(importEx.message)
            else:
                NetzobErrorMessage(importEx.message)

    def stopSniffing_cb(self, widget):
        self.model.stopSniff()

    def callback_readMessage(self, message):
        shortPayload = message.getStringData()
        if len(shortPayload) > 256:
            shortPayload = shortPayload[:255] + '...'
        self.view.listListStore.append([str(message.getID()),
                                        False,
                                        str(message.getKey()),
                                        str(message.getCategory()),
                                        str(message.getDirection()),
                                        str(shortPayload)])

    def doGetMessageDetails(self, messageID):
        return self.model.getMessageDetails(messageID)

    def doImportMessages(self, selectedPackets):
        self.model.saveMessagesInCurrentProject(selectedPackets)

    def sniffOptionRadioButton_toggled_cb(self, widget):
        if self.view.fsFlowsCheck.get_active():
            self.model.sniffOption = "fs"
        elif self.view.networkFlowsCheck.get_active():
            self.model.sniffOption = "network"
        elif self.view.ipcFlowsCheck.get_active():
            self.model.sniffOption = "ipc"
        elif self.view.selectedFlowsCheck.get_active():
            self.model.sniffOption = "selected"
        else:
            self.model.sniffOption = "all"
