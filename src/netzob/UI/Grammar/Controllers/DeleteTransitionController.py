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
from netzob.UI.Grammar.Views.DeleteTransitionView import DeleteTransitionView
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class DeleteTransitionController(object):
    """Manages the deletion of a transition"""

    def __init__(self, grammarController, transition):
        self.grammarController = grammarController
        self.transition = transition
        self._view = DeleteTransitionView(self, self.transition)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def deleteButton_clicked_cb(self, widget):
        currentProject = self.grammarController.getCurrentProject()
        if currentProject is None or self.transition is None:
            return
        grammar = currentProject.getGrammar()
        automata = grammar.getAutomata()
        if automata is None:
            return

        automata.removeTransition(self.transition)
        self._view.destroy()

        self.grammarController.restart()

    def cancelButton_clicked_cb(self, widget):
        self._view.destroy()

    def run(self):
        self._view.run()
