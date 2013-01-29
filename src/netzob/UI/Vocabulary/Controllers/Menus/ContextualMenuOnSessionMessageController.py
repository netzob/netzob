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
import time
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.Menus.ContextualMenuOnSessionMessageView import ContextualMenuOnSessionMessageView
from netzob.UI.NetzobWidgets import NetzobLabel
from netzob.UI.NetzobWidgets import NetzobErrorMessage
from netzob.Common.Session import Session


class ContextualMenuOnSessionMessageController(object):
    """Contextual menu on field (copy to clipboard, message
    visualization, etc.)"""

    def __init__(self, vocabularyController, session, messages):
        self.vocabularyController = vocabularyController
        self.session = session
        self.messages = messages
        self._view = ContextualMenuOnSessionMessageView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    def getSymbol(self):
        return self.field.getSymbol()

    def colorizeConversation_cb(self, event):
        # Clean message list
        self.vocabularyController.updateSelectedMessageTable()

        # Retrieve the couple (src, dst) of the current message
        if len(self.messages) > 0:
            selectedMessage = self.messages[0]
        src = selectedMessage.getSource()
        dst = selectedMessage.getDestination()

        # Retrieve all messages in session with the same (src, dst) or (dst, src) couple
        messagesSent = []
        messagesReceived = []
        for message in self.session.getMessages():
            if (message.getSource() == src) and (message.getDestination() == dst):
                messagesSent.append(message.getID())
            elif (message.getSource() == dst) and (message.getDestination() == src):
                messagesReceived.append(message.getID())

        # Colorize listore according to the direction
        sessionTableView = self.vocabularyController.getSelectedMessageTable()
        model = sessionTableView.sessionTableListStore
        aIter = model.get_iter_first()
        while aIter:
            anID = model[aIter][0]
            if anID in messagesSent:
                model[aIter][1] = "#F3E2A9"
            elif anID in messagesReceived:
                model[aIter][1] = "#A9F5A9"
            aIter = model.iter_next(aIter)

    def extractConversation_cb(self, event):
        # Clean message list
        self.vocabularyController.updateSelectedMessageTable()

        # Retrieve the couple (src, dst) of the first selected message
        if len(self.messages) > 0:
            selectedMessage = self.messages[0]
        src = selectedMessage.getSource()
        dst = selectedMessage.getDestination()

        # Retrieve all messages in session with the same (src, dst) or (dst, src) couple
        messagesConversation = []
        for message in self.session.getMessages():
            if (message.getSource() == src) and (message.getDestination() == dst):
                messagesConversation.append(message)
            elif (message.getSource() == dst) and (message.getDestination() == src):
                messagesConversation.append(message)

        # Create and register a new session
        newSession = Session(str(uuid.uuid4()), "New session", self.vocabularyController.getCurrentProject(), "")
        for message in messagesConversation:
            newSession.addMessage(message)
        # We register the session in the vocabulary of the project
        self.vocabularyController.getCurrentProject().getVocabulary().addSession(newSession)

        # Update UI
        self.vocabularyController.updateLeftPanel()
