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
        session = Session(uuid.uuid4(), "Session 1", "")
        for message in self.importedMessages:
            session.addMessage(message)
        # We register the session in the vocabulary of the project
        self.currentProject.getVocabulary().addSession(session)

        # We create a default symbol dedicated for this
        symbol = Symbol(uuid.uuid4(), symbolName, self.currentProject)
        for message in self.importedMessages:
            symbol.addMessage(message)
        # We register the symbol in the vocabulary of the project
        self.currentProject.getVocabulary().addSymbol(symbol)
        # We create a default field for the symbol
        symbol.reinitFields()

        # Add the environmental dependencies to the project
#        if fetchEnv:
#            project.getConfiguration().setVocabularyInferenceParameter(ProjectConfiguration.VOCABULARY_ENVIRONMENTAL_DEPENDENCIES,
#                                                                       self.envDeps.getEnvData())
        # Computes current date
        date = datetime.now()
        description = "No description (yet not implemented)"

        # We also save the session and the messages in the workspace
        trace = ImportedTrace(uuid.uuid4(), date, self.importType, description, self.currentProject.getName())
        trace.addSession(session)
        for message in self.importedMessages:
            trace.addMessage(message)

        self.currentWorkspace.addImportedTrace(trace)

        # Now we save the workspace
        self.currentWorkspace.saveConfigFile()

        self._view.destroy()

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


#        self.flagStop = False
#        # update widget
#        self._view.simple_cancel.set_sensitive(False)
#        self._view.simple_execute.set_sensitive(False)
#        self._view.radiobutton8bits.set_sensitive(False)
#        self._view.radiobutton16bits.set_sensitive(False)
#        self._view.radiobutton32bits.set_sensitive(False)
#        self._view.radiobutton64bits.set_sensitive(False)
#
#        self._view.simple_stop.set_sensitive(True)
#
#        #extract chosen value
#        formatBits = UnitSize.BITS8
#        if self._view.radiobutton16bits.get_active():
#            formatBits = UnitSize.BITS16
#        elif self._view.radiobutton32bits.get_active():
#            formatBits = UnitSize.BITS32
#        elif self._view.radiobutton64bits.get_active():
#            formatBits = UnitSize.BITS64
#
#        # create a job to execute the partitioning
#        Job(self.startSimplePartitioning(formatBits))
#
#    def startSimplePartitioning(self, unitSize):
#        if len(self.symbols) > 0:
#            self.log.debug("Start to simple partitioning the selected symbols")
#            try:
#                (yield ThreadedTask(self.simplePartitioning, unitSize))
#            except TaskError, e:
#                self.log.error(_("Error while proceeding to the simple partitioning of symbols: {0}").format(str(e)))
#        else:
#            self.log.debug("No symbol selected")
#
#        # Update button
#        self._view.simple_stop.set_sensitive(False)
#
#        # Close dialog box
#        self._view.simpleDialog.destroy()
#
#        # Update the message table view
#        self.vocabularyController._view.updateMessageTableDisplayingSymbols(self.symbols)
#        # Update the symbol properties view
#        self.vocabularyController._view.updateLeftPanel()
#
#    def simplePartitioning(self, unitSize):
#        """Simple partitioning the provided symbols"""
#        self.id_current_symbol = 0
#        for symbol in self.symbols:
#            GObject.idle_add(self._view.simple_progressbar.set_text, _("Simple partitioning symbol {0}".format(symbol.getName())))
#            if self.isFlagStopRaised():
#                return
#            symbol.simplePartitioning(unitSize, self.updateProgessBar, self.isFlagStopRaised)
#            self.id_current_symbol += 1
#
#    def updateProgessBar(self, percent, message):
#        """Update the progress bar given the provided informations"""
#        nbStage = len(self.symbols)
#        if percent is not None:
#            totalPercent = (100 / nbStage) * self.id_current_symbol + percent / nbStage
#            valTotalPercent = float(totalPercent) / float(100)
#            time.sleep(0.01)
#            GObject.idle_add(self._view.simple_progressbar.set_fraction, valTotalPercent)
#
#        if message is None:
#            GObject.idle_add(self._view.simple_progressbar.set_text, "")
#        else:
#            GObject.idle_add(self._view.simple_progressbar.set_text, message)
#
#    def isFlagStopRaised(self):
#        return self.flagStop
#
#    def simple_stop_clicked_cb(self, widget):
#        # update button
#        self._view.simple_stop.set_sensitive(False)
#        self.flagStop = True
#
#        # update widget
#        self._view.simple_execute.set_sensitive(True)
#        self._view.simple_cancel.set_sensitive(True)
#        self._view.radiobutton8bits.set_sensitive(True)
#        self._view.radiobutton16bits.set_sensitive(True)
#        self._view.radiobutton32bits.set_sensitive(True)
#        self._view.radiobutton64bits.set_sensitive(True)
