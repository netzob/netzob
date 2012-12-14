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
import logging
import uuid
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Simulator.XDotWidget import XDotWidget
from netzob.Common.SignalsManager import SignalsManager
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.MMSTD import MMSTD
from netzob.UI.Grammar.Views.GrammarXDotWidget import GrammarXDotWidget
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class GrammarView(object):

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "grammar",
            "GrammarView.glade"))
        self._getObjects(self.builder, ["paned1", "grammarViewport"])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)

        self.xdotWidget = GrammarXDotWidget(self.controller)
        self.xdotWidget.show_all()
        self.paned1.add(self.xdotWidget)
        self.registerSignalListeners()

    def registerSignalListeners(self):
        # Register signal processing on toolbar elements
        signalManager = self.netzob.getSignalsManager()
        if signalManager is None:
            self.log.warning("No signal manager has been found.")
            return

        signalManager.attach(self.projectStatusHasChanged_cb, [SignalsManager.SIG_PROJECT_OPEN, SignalsManager.SIG_PROJECT_CLOSE])

    def projectStatusHasChanged_cb(self, signal):
        """projectStatusHasChanged_cb: Callback executed when a signal
        is emitted."""

        actions = ["grammarInference",
                   "grammarEdition",
                   ]

        if signal == SignalsManager.SIG_PROJECT_OPEN:
            for action in actions:
                self._actionGroup.get_action(action).set_sensitive(True)

        elif signal == SignalsManager.SIG_PROJECT_CLOSE:
            for action in actions:
                self._actionGroup.get_action(action).set_sensitive(False)

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load actions
        actionsBuilder = Gtk.Builder()
        actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "grammar",
            "grammarActions.glade"))
        self._actionGroup = actionsBuilder.get_object("grammarActionGroup")
        actionsBuilder.connect_signals(self.controller)
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "grammar",
            "grammarMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    ## Mandatory view methods
    def getPanel(self):
        return self.grammarViewport

    # Return the actions
    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return self._uiDefinition

    def restart(self):
        """restart the view"""
        self.updateGrammar()

    def updateGrammar(self):
        """Update the displayed grammar"""
        # retrieve the current grammar
        if self.controller.getCurrentProject() is None:
            logging.info("No project is selected.")
            return

        grammar = self.controller.getCurrentProject().getGrammar()
        grammar.update(self.controller.getCurrentProject().getVocabulary())

        if grammar is not None:
            automata = grammar.getAutomata()
            if automata is not None:
                logging.debug("automata dot code: {0}".format(automata.getDotCode()))

                self.xdotWidget.drawAutomata(automata)
            else:
                self.xdotWidget.clear()
