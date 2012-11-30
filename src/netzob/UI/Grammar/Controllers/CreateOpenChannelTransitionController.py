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
from netzob.UI.Grammar.Views.CreateOpenChannelTransitionView import CreateOpenChannelTransitionView
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition

gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class CreateOpenChannelTransitionController(object):
    """Manages the creation of an open channel transition"""

    def __init__(self, grammarController, currentTransition):
        self.grammarController = grammarController
        self.currentTransition = currentTransition
        if self.currentTransition is None:
            self.idTransition = str(uuid.uuid4())
        else:
            self.idTransition = self.currentTransition.getID()
        self._view = CreateOpenChannelTransitionView(self, self.idTransition)
        self.log = logging.getLogger(__name__)

        if self.currentTransition is not None:
            self.view.idEntry.set_text(self.idTransition)
            self.view.nameEntry.set_text(self.currentTransition.getName())
            self.view.timeEntry.set_text(str(self.currentTransition.getConnectionTime()))
            self.view.maxNumberOfAttemptEntry.set_text(str(self.currentTransition.getMaxNumberOfAttempt()))

            # Retrieves the list of states
            states = []
            currentProject = self.grammarController.getCurrentProject()
            if currentProject is not None:
                automata = currentProject.getGrammar().getAutomata()
                if automata is not None:
                    states.extend(automata.getStates())

            # Set the start state
            i = 0
            for state in states:
                if str(state.getID()) == self.currentTransition.getInputState().getID():
                    self.view.startStateComboBox.set_active(i)
                    break
                i += 1

            # Set the end state
            i = 0
            for state in states:
                if str(state.getID()) == self.currentTransition.getOutputState().getID():
                    self.view.endStateComboBox.set_active(i)
                    break
                i += 1

    @property
    def view(self):
        return self._view

    def displayErrorMessage(self, errorMessage):
        if errorMessage is None:
            self._view.errorImage.hide()
            self._view.errorLabel.set_label("")
            self._view.errorLabel.hide()
        else:
            self._view.errorLabel.set_label(errorMessage)
            self._view.errorLabel.show()
            self._view.errorImage.show()

    def cancelButton_clicked_cb(self, event):
        """Callback executed when the user clicks on the cancel button"""
        self._view.destroy()

    def createButton_clicked_cb(self, event):
        """callback executed when the user clicks on the create button"""

        # Remove old transition
        currentProject = self.grammarController.getCurrentProject()
        if currentProject is not None:
            automata = currentProject.getGrammar().getAutomata()
            if self.currentTransition is not None:
                automata.removeTransition(self.currentTransition)

        # Transition's name
        transitionName = self._view.nameEntry.get_text()
        if transitionName == None or len(transitionName) == 0:
            errorMessage = _("Give a name to the transition")
            self.displayErrorMessage(errorMessage)
            return

        # Transition's time before executing
        timeTransition = None
        try:
            timeTransition = int(self._view.timeEntry.get_text())
        except:
            pass
        if timeTransition is None or timeTransition < 0:
            errorMessage = _("Give a valid time (> 0ms)")
            self.displayErrorMessage(errorMessage)
            return

        # Max number of attempt
        maxNumberOfAttempt = None
        try:
            maxNumberOfAttempt = int(self._view.maxNumberOfAttemptEntry.get_text())
        except:
            pass
        if maxNumberOfAttempt is None or maxNumberOfAttempt < 1:
            errorMessage = _("Give a valid maximum number of attempt (> 1)")
            self.displayErrorMessage(errorMessage)
            return

        # Transition's start & end state
        startState_iter = self._view.startStateComboBox.get_active_iter()
        endState_iter = self._view.endStateComboBox.get_active_iter()
        if startState_iter is None:
            errorMessage = _("Select a start state.")
            self.displayErrorMessage(errorMessage)
            return
        if endState_iter is None:
            errorMessage = _("Select an end state")
            self.displayErrorMessage(errorMessage)
            return

        automata = currentProject.getGrammar().getAutomata()
        states = []
        if automata is not None:
            states.extend(automata.getStates())

        idStartState = self._view.startStateComboBox.get_model()[startState_iter][0]
        idEndState = self._view.endStateComboBox.get_model()[endState_iter][0]
        startState = None
        endState = None
        for state in states:
            if str(state.getID()) == str(idStartState):
                startState = state
            if str(state.getID()) == str(idEndState):
                endState = state
            if startState is not None and endState is not None:
                break
        if startState is None:
            errorMessage = _("An error occurred and prevented to retrieve the provided start state.")
            self.displayErrorMessage(errorMessage)
            return
        if endState is None:
            errorMesssage = _("An error occurred and prevented to retrieve the provided end state.")
            self.displayErrorMessage(errorMessage)
            return

        # Verify no other open channel transition is registered on the start state
        found = False
        for transitionStartState in startState.getTransitions():
            if transitionStartState.getType() == OpenChannelTransition.TYPE:
                found = True
                break

        if found:
            errorMessage = _("Provided start state already has an open channel transition.")
            self.displayErrorMessage(errorMessage)
            return

        transition = OpenChannelTransition(self.idTransition, transitionName, startState, endState, timeTransition, maxNumberOfAttempt)
        startState.registerTransition(transition)

        # attach the transition to the grammar
        self.grammarController.getCurrentProject().getGrammar().getAutomata().addTransition(transition)

        self._view.destroy()
        self.grammarController.restart()

    def run(self):
        self._view.run()
