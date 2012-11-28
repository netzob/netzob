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
from datetime import datetime

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask, TaskError
from netzob.UI.Import.Views.ConfirmImportMessagesView import ConfirmImportMessagesView
from netzob.Common.Threads.Job import Job
from netzob.Common.Session import Session
from netzob.Common.ImportedTrace import ImportedTrace
from netzob.Common.Symbol import Symbol


class ConfirmImportMessagesController(object):
    '''Controller to request the user to confirm the import process of
    provided messages'''

    def __init__(self, currentWorkspace, currentProject, importType, messages):
        self.currentWorkspace = currentWorkspace
        self.currentProject = currentProject
        self._view = ConfirmImportMessagesView(self)
        self.log = logging.getLogger(__name__)
        self.messages = messages
        self.importedMessages = messages
        self.excludedMessages = []
        self.importType = importType
        self.finish_cb = None

    @property
    def view(self):
        return self._view

    def cancelButton_clicked_cb(self, widget):
        """Callback executed when the user wants to cancel the import"""
        self.stopFlag = True
        self._view.destroy()

    def importButton_clicked_cb(self, widget):
        """Callback executed when the user wants to import messages"""
        if self.currentProject is None:
            self.log.error("No project is open")
            return

        # retrieve symbol name
        symbolName = self._view.nameOfCreatedSymbolEntry.get_text()
        if symbolName is None or len(symbolName) < 1:
            self.displayErrorMessage(_("Specify the name of new symbol"))
            return

        found = False
        for symbol in self.currentProject.getVocabulary().getSymbols():
            if symbol.getName() == symbolName:
                found = True
                break

        if found:
            self.displayErrorMessage(_("The provided symbol name already exists."))
            return

        # Should we consider meta datas of excluded messages
        if self._view.removeDuplicatedMessagesCheckButton.get_active() and self._view.keepPropertiesOfDuplicatedMessagesCheckButton.get_active():
            # Retrieve the 'excluded' messages and retrieve their properties
            for message in self.excludedMessages:
                # search for an included message to register properties
                eq_message = None
                for importedMessage in self.importedMessages:
                    if importedMessage.getStringData() == message.getStringData():
                        eq_message = importedMessage
                        break
                if eq_message is not None:
                    for property in message.getProperties():
                        eq_message.addExtraProperty(property)

        # We register each message in the vocabulary of the project
        for message in self.importedMessages:
            self.currentProject.getVocabulary().addMessage(message)

        # We create a session with each message
        session = Session(str(uuid.uuid4()), "Session 1", "")
        for message in self.importedMessages:
            session.addMessage(message)
        # We register the session in the vocabulary of the project
        self.currentProject.getVocabulary().addSession(session)

        # We create a default symbol dedicated for this
        symbol = Symbol(str(uuid.uuid4()), symbolName, self.currentProject)
        for message in self.importedMessages:
            symbol.addMessage(message)
        # We register the symbol in the vocabulary of the project
        self.currentProject.getVocabulary().addSymbol(symbol)

        # Add the environmental dependencies to the project
#        if fetchEnv:
#            project.getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES,
#                                                                       self.envDeps.getEnvData())
        # Computes current date
        date = datetime.now()
        description = "No description (yet not implemented)"

        # We also save the session and the messages in the workspace
        trace = ImportedTrace(str(uuid.uuid4()), date, self.importType, description, self.currentProject.getName())
        trace.addSession(session)
        for message in self.importedMessages:
            trace.addMessage(message)

        self.currentWorkspace.addImportedTrace(trace)

        # Now we save the workspace
        self.currentWorkspace.saveConfigFile()

        self._view.destroy()

        if self.finish_cb is not None:
            GObject.idle_add(self.finish_cb)

    def displayErrorMessage(self, errorMessage):
        """Display to the user the provided errorMessage"""
        if errorMessage is not None:
            self._view.errorImage.show()
            self._view.errorLabel.set_label(errorMessage)
            self._view.errorLabel.show()
        else:
            self._view.errorImage.hide()
            self.showNumberOfImportedMessages()

    def showNumberOfImportedMessages(self):
        """Set the text which shows to the user the number
        of messages that will be imported."""
        self._view.errorLabel.set_label(_("{0} messages will be imported").format(len(self.importedMessages)))
        self._view.errorLabel.show()

    def removeDuplicatedMessagesCheckButton_toggled_cb(self, widget):
        """Callback executed when the user toggle (or untoggle) the
        checkbox to deactivate the duplication of payloads in import"""
        if self._view.removeDuplicatedMessagesCheckButton.get_active():
            self._view.keepPropertiesOfDuplicatedMessagesCheckButton.set_sensitive(True)
            self.removeDuplicatedMessagesFromImport()
        else:
            self._view.keepPropertiesOfDuplicatedMessagesCheckButton.set_sensitive(False)
            self.importedMessages = self.messages

        self.showNumberOfImportedMessages()

    def removeDuplicatedMessagesFromImport(self):
        """Remove duplicated messages"""
        self.importedMessages = []
        self.excludedMessages = []

        existingMessages = []
        for symbol in self.currentProject.getVocabulary().getSymbols():
            existingMessages.extend(symbol.getMessages())

        # Remove duplicated messages
        for message in self.messages:
            found = False

            # we verify its a not an empty message
            if len(message.getStringData()) > 0:
                for m in self.importedMessages:
                    if m.getStringData() == message.getStringData():
                        found = True
                        break
                if not found:
                    for m in existingMessages:
                        if m.getStringData() == message.getStringData():
                            found = True
                            break
                    if not found:
                        self.importedMessages.append(message)
                    else:
                        self.excludedMessages.append(message)
                else:
                    self.excludedMessages.append(message)

    def run(self):
        """Run method"""
        self._view.errorImage.hide()
        self._view.errorLabel.show()
        self._view.errorLabel.set_label(_("{0} messages will be imported").format(len(self.importedMessages)))
        self._view.nameOfCreatedSymbolEntry.set_text("IMPORTS")
        self._view.removeDuplicatedMessagesCheckButton.set_active(True)
        self._view.keepPropertiesOfDuplicatedMessagesCheckButton.show()
        self._view.keepPropertiesOfDuplicatedMessagesCheckButton.set_active(True)

        self._view.run()

    def setFinish_cb(self, function):
        """Set the callback to execute when import is finished"""
        self.finish_cb = function
