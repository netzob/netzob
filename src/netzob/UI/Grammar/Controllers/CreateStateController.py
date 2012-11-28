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
from netzob.UI.Grammar.Views.CreateStateView import CreateStateView
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.MMSTD import MMSTD
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class CreateStateController(object):
    """Manages the creation of a new state"""

    def __init__(self, grammarController):
        self.grammarController = grammarController
        self.idState = str(uuid.uuid4())
        self._view = CreateStateView(self, self.idState)
        self.log = logging.getLogger(__name__)

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
        currentProject = self.grammarController.getCurrentProject()

        """callback executed when the user clicks on the create button"""
        initialState = self._view.initialStateCheckButton.get_active()
        stateName = self._view.nameEntry.get_text()

        automata = currentProject.getGrammar().getAutomata()

        errorMessage = None
        # verify initialState is valid
        if not initialState and automata is None:
            errorMessage = _("The first created state must be an initial state")
            self.displayErrorMessage(errorMessage)
            return

        # verify the name of the state is unique
        found = False
        if automata is not None:
            for state in automata.getStates():
                if state.getName() == stateName:
                    found = True
                    break

        if found:
            errorMessage = _("A state already has this name, please specify another one")
            self.displayErrorMessage(errorMessage)
            return

        newState = NormalState(self.idState, stateName)
        if automata == None:
            automata = MMSTD(newState, currentProject.getVocabulary())
            currentProject.getGrammar().setAutomata(automata)

        automata.addState(newState)
        self._view.destroy()
        self.grammarController.restart()

    def run(self):
        self._view.run()
