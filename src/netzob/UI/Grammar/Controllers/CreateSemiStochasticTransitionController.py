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
from netzob.Common.MMSTD.MMSTD import MMSTD
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Grammar.Views.CreateSemiStochasticTransitionView import CreateSemiStochasticTransitionView


class CreateSemiStochasticTransitionController(object):
    """Manages the creation of a new SemiStochasticTransition"""

    def __init__(self, grammarController, currentTransition):
        self.grammarController = grammarController
        self.currentTransition = currentTransition
        if self.currentTransition is None:
            self.idTransition = str(uuid.uuid4())
        else:
            self.idTransition = self.currentTransition.getID()
        self._view = CreateSemiStochasticTransitionView(self, self.idTransition)
        self.log = logging.getLogger(__name__)

        if self.currentTransition is not None:
            self.view.idSemiStochasticTransitionEntry.set_text(self.idTransition)
            self.view.nameSemiStochasticTransitionEntry.set_text(self.currentTransition.getName())

            # Retrieves the list of states and of input symbols
            states = []
            inputSymbols = [EmptySymbol(), UnknownSymbol()]
            currentProject = self.grammarController.getCurrentProject()
            if currentProject is not None:
                automata = currentProject.getGrammar().getAutomata()
                if automata is not None:
                    states.extend(automata.getStates())
                vocabulary = currentProject.getVocabulary()
                if vocabulary is not None:
                    inputSymbols.extend(vocabulary.getSymbols())

            # Set the start state
            i = 0
            for state in states:
                if str(state.getID()) == self.currentTransition.getInputState().getID():
                    self.view.startStateSemiStochasticTransitionComboBox.set_active(i)
                    break
                i += 1

            # Set the end state
            i = 0
            for state in states:
                if str(state.getID()) == self.currentTransition.getOutputState().getID():
                    self.view.endStateSemiStochasticTransitionComboBox.set_active(i)
                    break
                i += 1

            # Set the input symbol
            i = 0
            for symbol in inputSymbols:
                if str(symbol.getID()) == self.currentTransition.getInputSymbol().getID():
                    self.view.inputSymbolSemiStochasticTransitionComboBox.set_active(i)
                    break
                i += 1

            # Set the output symbols
            outputSymbols = self.currentTransition.getOutputSymbols()
            for outputSymbolTupple in outputSymbols:
                (outputSymbol, probabilityOutput, timeOutput) = outputSymbolTupple
                i = self.view.outputSymbolsListStore.append()
                self.view.outputSymbolsListStore.set(i, 0, str(outputSymbol.getID()))
                self.view.outputSymbolsListStore.set(i, 1, outputSymbol.getName())
                self.view.outputSymbolsListStore.set(i, 2, probabilityOutput)
                self.view.outputSymbolsListStore.set(i, 3, timeOutput)

    @property
    def view(self):
        return self._view

    def displayErrorMessage(self, errorMessage):
        if errorMessage is None:
            self._view.errorSemiStochasticTransitionImage.hide()
            self._view.errorSemiStochasticTransitionLabel.set_label("")
            self._view.errorSemiStochasticTransitionLabel.hide()
        else:
            self._view.errorSemiStochasticTransitionLabel.set_label(errorMessage)
            self._view.errorSemiStochasticTransitionLabel.show()
            self._view.errorSemiStochasticTransitionImage.show()

    def cancelSemiStochasticTransitionButton_clicked_cb(self, event):
        """Callback executed when the user clicks on the cancel button"""
        self._view.destroy()

    def createSemiStochasticTransitionButton_clicked_cb(self, event):
        """callback executed when the user requests
        the creation of the transition"""
        currentProject = self.grammarController.getCurrentProject()

        # Remove old transition
        if currentProject is not None:
            automata = currentProject.getGrammar().getAutomata()
            if self.currentTransition is not None:
                automata.removeTransition(self.currentTransition)

        # Retrieve the states and symbols of the current project
        states = []
        symbols = [EmptySymbol(), UnknownSymbol()]
        if currentProject is not None:
            automata = currentProject.getGrammar().getAutomata()
            if automata is not None:
                states.extend(automata.getStates())
            vocabulary = currentProject.getVocabulary()
            if vocabulary is not None:
                symbols.extend(vocabulary.getSymbols())

        # Name of the transition
        nameTransition = self._view.nameSemiStochasticTransitionEntry.get_text()
        if nameTransition is None or len(nameTransition) == 0:
            errorMessage = _("Give a name to the transition.")
            self.displayErrorMessage(errorMessage)
            return

        # Start and End state of the transition
        startState_iter = self._view.startStateSemiStochasticTransitionComboBox.get_active_iter()
        endState_iter = self._view.endStateSemiStochasticTransitionComboBox.get_active_iter()
        if startState_iter is None:
            errorMessage = _("Select a start state.")
            self.displayErrorMessage(errorMessage)
            return
        if endState_iter is None:
            errorMessage = _("Select an end state")
            self.displayErrorMessage(errorMessage)
            return

        idStartState = self._view.startStateSemiStochasticTransitionComboBox.get_model()[startState_iter][0]
        idEndState = self._view.endStateSemiStochasticTransitionComboBox.get_model()[endState_iter][0]
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

        # Input Symbol
        inputSymbolIter = self._view.inputSymbolSemiStochasticTransitionComboBox.get_active_iter()
        if inputSymbolIter is None:
            errorMessage = _("Select an input Symbol.")
            self.displayErrorMessage(errorMessage)
            return

        idInputSymbol = self._view.inputSymbolSemiStochasticTransitionComboBox.get_model()[inputSymbolIter][0]
        inputSymbol = None
        for symbol in symbols:
            if str(symbol.getID()) == str(idInputSymbol):
                inputSymbol = symbol
                break
        if inputSymbol is None:
            errorMessage = _("An error occurred and prevented to retrieve the provided input symbol")
            self.displayErrorMessage(errorMessage)
            return

        # Verify the start state doesn't have a transition which has the same input symbol
        found = False
        for startStateTransition in startState.getTransitions():
            if startStateTransition.getType() == SemiStochasticTransition.TYPE:
                if str(startStateTransition.getInputSymbol().getID()) == str(inputSymbol.getID()):
                    found = True
                    break
        if found:
            errorMessage = _("The specified start state already has a transition with the same input symbol.")
            self.displayErrorMessage(errorMessage)
            return

        if len(self._view.outputSymbolsListStore) == 0:
            errorMessage = _("Provide at least 1 output symbol (even an EmptySymbol).")
            self.displayErrorMessage(errorMessage)
            return

        # Create the transition
        transition = SemiStochasticTransition(self.idTransition, nameTransition, startState, endState, inputSymbol)

        # Now we add all the output symbols
        for row in self._view.outputSymbolsListStore:
            idOutputSymbol = row[0]
            probaOutputSymbol = row[2]
            timeOutputSymbol = row[3]

            outputSymbol = None
            for symbol in symbols:
                if str(symbol.getID()) == str(idOutputSymbol):
                    outputSymbol = symbol
                    break
            if outputSymbol == None:
                errorMessage = _("An error occurred and prevented to retrieve the output symbols")
                self.displayErrorMessage(errorMessage)
                return

            transition.addOutputSymbol(outputSymbol, probaOutputSymbol, timeOutputSymbol)

        # Add the transition
        startState.registerTransition(transition)

        # attach the transition to the grammar
        self.grammarController.getCurrentProject().getGrammar().getAutomata().addTransition(transition)
        self._view.destroy()
        self.grammarController.restart()

    def addOutputSymbolSemiStochasticTransitionButton_clicked_cb(self, event):
        symbols = [EmptySymbol(), UnknownSymbol()]
        currentProject = self.grammarController.getCurrentProject()
        if currentProject is not None:
            vocabulary = currentProject.getVocabulary()
            if vocabulary is not None:
                symbols.extend(vocabulary.getSymbols())

        # Retrieve the output symbol
        active_iter = self._view.outputSymbolSemiStochasticTransitionComboBox.get_active_iter()
        if active_iter is None:
            errorMessage = _("Select an output Symbol before adding it.")
            self.displayErrorMessage(errorMessage)
            return

        idSymbol = self._view.outputSymbolSemiStochasticTransitionComboBox.get_model()[active_iter][0]
        outputSymbol = None
        for symbol in symbols:
            if str(symbol.getID()) == str(idSymbol):
                outputSymbol = symbol
                break

        if outputSymbol == None:
            errorMessage = _("An error occured and prevented to retrieved the output symbol.")
            self.displayErrorMessage(errorMessage)
            return

        # Retrieve the probability of the symbol
        probabilityOutputSymbol = float(0.0)
        try:
            probabilityOutputSymbol = float(self._view.outputSymbolProbabilitySemiStochasticTransitionEntry.get_text())
        except:
            errorMessage = _("Specify a valid probability defined over 100 (float)")
            self.displayErrorMessage(errorMessage)
            return

        if probabilityOutputSymbol < 0 or probabilityOutputSymbol > 100:
            errorMessage = _("Specify a valid probability (0.0<=probability<=100.0)")
            self.displayErrorMessage(errorMessage)
            return

        # Retrieve the time of the output symbol
        timeOutputSymbol = 0
        try:
            timeOutputSymbol = int(self._view.outputSymbolTimeSemiStochasticTransitionEntry.get_text())
        except:
            errorMessage = _("Specify a valid time defined in millisecond (int)")
            self.displayErrorMessage(errorMessage)
            return

        if timeOutputSymbol < 0:
            errorMessage = _("Specify a valid time (0<=time)")
            self.displayErrorMessage(errorMessage)
            return

        # Now we verify its the first time this symbol is considered as an output symbol
        found = False
        sumProba = probabilityOutputSymbol
        for row in self._view.outputSymbolsListStore:
            if str(row[0]) == str(outputSymbol.getID()):
                found = True
                break
            sumProba += row[2]
        if found:
            errorMessage = _("You cannot add multiple time the same output symbol.")
            self.displayErrorMessage(errorMessage)
            return

        # We verify the sum of probabilities is under 100
        if sumProba > 100:
            errorMessage = _("The sum of probabilities is above 100, please adapt the provided value.")
            self.displayErrorMessage(errorMessage)
            return

        i = self._view.outputSymbolsListStore.append()
        self._view.outputSymbolsListStore.set(i, 0, str(outputSymbol.getID()))
        self._view.outputSymbolsListStore.set(i, 1, outputSymbol.getName())
        self._view.outputSymbolsListStore.set(i, 2, probabilityOutputSymbol)
        self._view.outputSymbolsListStore.set(i, 3, timeOutputSymbol)

        self.displayErrorMessage(None)

    def removeOutputSymbolSemiStochasticTransitionButton_clicked_cb(self, event):
        """Callback executed when the user requests to remove a selected output symbol including
        its probability and its time from the current list"""

        # Retrieve the selection
        selection = self._view.outputSymbolsSemiStochasticTransitionTreeview.get_selection()
        if selection is None:
            errorMessage = _("Select an output Symbol before removing it.")
            self.displayErrorMessage(errorMessage)
            return

        (model, path) = selection.get_selected()
        if model is None or path is None:
            errorMessage = _("Select an output Symbol before removing it.")
            self.displayErrorMessage(errorMessage)
            return

        model.remove(path)

    def run(self):
        self._view.run()
