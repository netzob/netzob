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
import logging
import os
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, GObject
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.FilterMessagesView import FilterMessagesView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Type.Format import Format


class FilterMessagesController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = FilterMessagesView(self)
        self.log = logging.getLogger(__name__)
        self.nbResult = 0

    @property
    def view(self):
        return self._view

    def show(self):
        self._view.filterBar.show()

    def hide(self):
        self.view.filter_entry.set_text("")
        self._view.filterBar.hide()

    def filter_entry_changed_cb(self, widget):
        """Callback executed when the user types some
        data in the filter entry"""

        # Sanity checks
        if self.vocabularyController.getCurrentProject() is None:
            return
        symbol = self.vocabularyController.view.getDisplayedFieldInSelectedMessageTable()
        if symbol is None:
            return
        toSearch = widget.get_text()
        if toSearch == "":
            self.vocabularyController.view.selectedMessageTable.updateMessageTableListStore()
            return

        # Update the message list model
        self.vocabularyController.view.selectedMessageTable.updateMessageTableListStore()

        # Search non-matching messages
        messagesToRemove = []
        messagesStore = self.vocabularyController.view.selectedMessageTable.messageTableListStore
        for message in symbol.getMessages():
            messageData = "".join(message.applyAlignment(styled=False, encoded=True))
            if messageData.find(toSearch) == -1:
                i = messagesStore.get_iter_first()
                while True:
                    if i == None:
                        break
                    s = messagesStore.get_value(i, 0)
                    if str(s) == str(message.getID()):
                        messagesToRemove.append(i)
                        break
                    i = messagesStore.iter_next(i)

        # Remove non-matching messages
        for messageToRemove in messagesToRemove:
            messagesStore.remove(messageToRemove)

    def filter_close_clicked_cb(self, widget):
        """Callback executed when the user closes the results"""
        self.vocabularyController.view.updateSelectedMessageTable()
        checkMenuItem = self.vocabularyController.netzob.view.uiManager.get_widget("/mainMenuBar/mainMenuBarAdditions/searchMenu/filterMessages")
        checkMenuItem.set_active(False)
        self.hide()
