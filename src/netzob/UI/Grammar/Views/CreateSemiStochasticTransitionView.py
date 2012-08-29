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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class CreateSemiStochasticTransitionView(object):

    def __init__(self, controller, idTransition):
        '''
        Constructor
        '''
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui", "grammar",
                                                "createSemiStochasticTransitionDialogs.glade"))

        self._getObjects(self.builder, ["createSemiStochasticTransitionDialog",
                                        "createSemiStochasticTransitionButton",
                                        "cancelSemiStochasticTransitionButton",
                                        "idSemiStochasticTransitionEntry",
                                        "nameSemiStochasticTransitionEntry",
                                        "startStateSemiStochasticTransitionComboBox",
                                        "endStateSemiStochasticTransitionComboBox",
                                        "inputSymbolSemiStochasticTransitionComboBox",
                                        "errorSemiStochasticTransitionImage",
                                        "errorSemiStochasticTransitionLabel",
                                        "symbolListStore",
                                        "stateListStore",
                                        "outputSymbolListStore",
                                        "outputSymbolsListStore",
                                        "outputSymbolsSemiStochasticTransitionTreeview",
                                        "outputSymbolSemiStochasticTransitionComboBox",
                                        "outputSymbolsSemiStochasticTransitionComboBox",
                                        "outputSymbolProbabilitySemiStochasticTransitionEntry",
                                        "outputSymbolTimeSemiStochasticTransitionEntry",
                                        "removeOutputSymbolSemiStochasticTransitionButton",
                                        "addOutputSymbolSemiStochasticTransitionButton"
                                        ])
        self.controller = controller
        self.builder.connect_signals(self.controller)

        # Configure the current id of the new transition
        self.idSemiStochasticTransitionEntry.set_text(str(idTransition))
        self.idSemiStochasticTransitionEntry.set_sensitive(False)

        # Retrieves the list of states and of input symbols
        states = []
        inputSymbols = [EmptySymbol(), UnknownSymbol()]
        currentProject = self.controller.grammarController.getCurrentProject()
        if currentProject is not None:
            automata = currentProject.getGrammar().getAutomata()
            if automata is not None:
                states.extend(automata.getStates())
            vocabulary = currentProject.getVocabulary()
            if vocabulary is not None:
                inputSymbols.extend(vocabulary.getSymbols())

        self.stateListStore.clear()
        # Configure the list of states
        for state in states:
            i = self.stateListStore.append()
            self.stateListStore.set(i, 0, str(state.getID()))
            self.stateListStore.set(i, 1, state.getName())

        self.symbolListStore.clear()
        # Configure the list of input symbols
        for symbol in inputSymbols:
            i = self.symbolListStore.append()
            self.symbolListStore.set(i, 0, str(symbol.getID()))
            self.symbolListStore.set(i, 1, symbol.getName())

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.createSemiStochasticTransitionDialog.run()

    def destroy(self):
        self.createSemiStochasticTransitionDialog.destroy()
