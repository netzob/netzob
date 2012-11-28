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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.MoveMessageView import MoveMessageView
from netzob.UI.Vocabulary.Controllers.Partitioning.SequenceAlignmentController import SequenceAlignmentController
gi.require_version('Gtk', '3.0')
from gi.repository import GObject


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
class MoveMessageController(object):
    """Manage the case when its not trivial to move a message from a symbol to another one"""

    def __init__(self, vocabularyController, messages, targetSymbol):
        self.vocabularyController = vocabularyController
        self.log = logging.getLogger(__name__)
        self._view = MoveMessageView(self)
        self.messages = messages
        self.targetSymbol = targetSymbol

    @property
    def view(self):
        return self._view

    def run(self):
        self._view.run()

    def moveMessageCancelButton_clicked_cb(self, widget):
        """Callback executed when the user cancel
        the message moving"""
        self._view.moveMessageDialog.destroy()

    def moveMessageApplyButton_clicked_cb(self, widget):
        """Callback executed when the user request
        the execution of the ticked solution"""
        for message in self.messages:
            # retrieve which solution to execute
            if self._view.moveMessageMoveAndForgetRadioButton.get_active():
                self.forgetRegexAndMove(message)
            elif self._view.moveMessageMoveAndReComputeRadioButton.get_active():
                self.recomputeRegexAndMove(message)
            elif self._view.moveMessageMoveInTrashRadioButton.get_active():
                self.moveInTrash(message)

    def forgetRegexAndMove(self, message):
        """Move the requested message from its symbol
        to the defined other which's regex is reseted"""
        self.vocabularyController.moveMessage(message, self.targetSymbol)

        self.targetSymbol.getField().resetPartitioning()
        self._view.destroy()

    def recomputeRegexAndMove(self, message):
        """Move the requested message to the selected symbol
        which's regex is recomputed"""
        self.vocabularyController.moveMessage(message, self.targetSymbol)

        self._view.destroy()
        sequence_controller = SequenceAlignmentController(self.vocabularyController, [self.targetSymbol.getField()])
        sequence_controller.run()

    def moveInTrash(self, message):
        """Move the selected message in the trash symbol"""
        trashSymbol = self.vocabularyController.getCurrentProject().getVocabulary().getTrashSymbol()
        self.vocabularyController.moveMessage(message, trashSymbol)
        self._view.destroy()
