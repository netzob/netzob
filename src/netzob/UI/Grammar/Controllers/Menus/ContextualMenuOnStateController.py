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
from gi.repository import Gtk, Gdk, GObject
import gi
from netzob.UI.Grammar.Views.Menus.ContextualMenuOnStateView import ContextualMenuOnStateView
from netzob.UI.Grammar.Controllers.DeleteStateController import DeleteStateController
from netzob.UI.Grammar.Controllers.DeleteTransitionController import DeleteTransitionController
from netzob.UI.Grammar.Controllers.EditStateController import EditStateController
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Pango

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class ContextualMenuOnStateController(object):
    """Contextual menu on state"""

    def __init__(self, grammarController, state):
        self.grammarController = grammarController
        self.state = state
        self._view = ContextualMenuOnStateView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def run(self, event):
        self._view.run(event)

    def getState(self):
        return self.state

    def editState_cb(self, widget):
        """callback executed when the user wants to edit a state"""
        controller = EditStateController(self.grammarController, self.state)
        controller.run()

    def deleteState_cb(self, widget):
        """callback executed when the user wants to delete a state"""
        controller = DeleteStateController(self.grammarController, self.state)
        controller.run()

    def editTransition_cb(self, widget, event, transition):
        """callback executed when the user wants to edit a transition"""
        print "edit transition"

    def deleteTransition_cb(self, widget, event, transition):
        """callback executed when the user wants to delete a transition"""
        controller = DeleteTransitionController(self.grammarController, transition)
        controller.run()
