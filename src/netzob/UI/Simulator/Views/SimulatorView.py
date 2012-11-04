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
from gi.repository import GObject, Gtk, Gdk
import gi
import logging
import os
import uuid
import datetime
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Simulator.XDotWidget import XDotWidget


class SimulatorView(object):

    def __init__(self, controller):
        self.controller = controller
        self.netzob = self.controller.netzob
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "simulator",
            "simulatorView.glade"))
        self._getObjects(self.builder, ["simulatorViewport",
                                        "editActorButton",
                                        "deleteActorButton",
                                        "stopActorButton",
                                        "startActorButton",
                                        "actorsListStore",
                                        "listOfActorsTreeView",
                                        "grammarCurrentActorViewport",
                                        "statusCurrentActorImage",
                                        "nameCurrentActorLabel",
                                        "stopCurrentActorButton",
                                        "startCurrentActorButton",
                                        "infoCurrentActorLabel",
                                        "statusCurrentActorLabel",
                                        "currentActorIOChannelListStore",
                                        "currentActorMemoryListStore",
                                        "currentActorPropertiesListStore"
                                        ])
        self._loadActionGroupUIDefinition()
        self.builder.connect_signals(self.controller)
        self.toggledActors = []

        self.xdotWidget = XDotWidget()
        self.xdotWidget.show_all()
        self.grammarCurrentActorViewport.add(self.xdotWidget)

        self.refreshListOfActors()
        self.updateCurrentActor()

    def _loadActionGroupUIDefinition(self):
        """Loads the action group and the UI definition of menu items
        . This method should only be called in the constructor"""
        # Load actions
        actionsBuilder = Gtk.Builder()
        actionsBuilder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "simulator",
            "simulatorActions.glade"))
        self._actionGroup = actionsBuilder.get_object("simulatorActionGroup")
        actionsBuilder.connect_signals(self.controller)
        uiDefinitionFilePath = os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "simulator",
            "simulatorMenuToolbar.ui")
        with open(uiDefinitionFilePath, "r") as uiDefinitionFile:
            self._uiDefinition = uiDefinitionFile.read()

    def _getObjects(self, builder, objectsList):
        for object in objectsList:
            setattr(self, object, builder.get_object(object))

    ## Mandatory view methods
    def getPanel(self):
        return self.simulatorViewport

    # Return the actions
    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return self._uiDefinition

    def restart(self):
        """restart the view"""
        self.refreshListOfActors()
        self.deleteActorButton.set_sensitive(False)

    def refreshListOfActors(self):
        """Clear the list of available actors and update it
        with declared actors in the project definition."""
        actors = []
        self.actorsListStore.clear()

        currentProject = self.controller.getCurrentProject()
        if currentProject is not None:
            simulator = currentProject.getSimulator()
            if simulator is not None:
                actors.extend(simulator.getActors())

        for actor in actors:
            i = self.actorsListStore.append()
            toggled = False
            if actor in self.toggledActors:
                toggled = True

            if actor.isActive():
                imageStatus = Gtk.STOCK_YES
            else:
                imageStatus = Gtk.STOCK_NO

            self.actorsListStore.set(i, 0, toggled)
            self.actorsListStore.set(i, 1, imageStatus)
            self.actorsListStore.set(i, 2, str(actor.getID()))
            self.actorsListStore.set(i, 3, actor.getName())

    def updateCurrentActor(self):
        currentActor = self.controller.getCurrentActor()

        self.currentActorIOChannelListStore.clear()
        self.currentActorMemoryListStore.clear()

        if currentActor is None:
            self.statusCurrentActorImage.hide()
            self.nameCurrentActorLabel.set_label("")
            self.nameCurrentActorLabel.hide()

            self.stopCurrentActorButton.set_sensitive(False)
            self.startCurrentActorButton.set_sensitive(False)

            self.updateGrammarOfCurrentActor()

            self.infoCurrentActorLabel.set_label("")
            self.infoCurrentActorLabel.hide()

            self.statusCurrentActorLabel.set_label("")
            self.statusCurrentActorLabel.hide()
        else:
            if currentActor.isActive():
                imageStatus = Gtk.STOCK_YES
                actorStatus = "active"
            else:
                imageStatus = Gtk.STOCK_NO
                actorStatus = "inactive"

            self.statusCurrentActorImage = Gtk.Image(stock=imageStatus)
            self.statusCurrentActorImage.show()
            self.nameCurrentActorLabel.set_label(currentActor.getName())
            self.nameCurrentActorLabel.show()

            self.stopCurrentActorButton.set_sensitive(True)
            self.startCurrentActorButton.set_sensitive(True)

            self.updateGrammarOfCurrentActor()

            self.infoCurrentActorLabel.set_label("hum hum")
            self.infoCurrentActorLabel.show()

            self.statusCurrentActorLabel.set_label(actorStatus)
            self.statusCurrentActorLabel.show()

            self.displayPropertiesOfActor(currentActor)

    def displayPropertiesOfActor(self, actor):
        """Display the properties of the actor"""
        self.currentActorPropertiesListStore.clear()

        for property in actor.getProperties():
            self.currentActorPropertiesListStore.append([str(property.getName()), str(property.getCurrentValue())])

    def updateGrammarOfCurrentActor(self):
        currentActor = self.controller.getCurrentActor()
        if currentActor is not None:
            grammar = self.controller.getCurrentProject().getGrammar()
            if grammar is not None:
                automata = grammar.getAutomata()
                if automata is not None:
                    self.xdotWidget.drawAutomata(automata)
                else:
                    self.xdotWidget.clear()
            self.xdotWidget.show()
        else:
            self.xdotWidget.clear()
            self.xdotWidget.hide()

    def registerInputSymbolOfCurrentActor(self, receptionTime, message, symbol):
        """Add a symbol, the message and the reception time in the list"""
        i = self.currentActorIOChannelListStore.append()
        self.currentActorIOChannelListStore.set(i, 0, Gtk.STOCK_GO_BACK)
        self.currentActorIOChannelListStore.set(i, 1, receptionTime)
        self.currentActorIOChannelListStore.set(i, 2, symbol.getName())
        self.currentActorIOChannelListStore.set(i, 3, message)

    def registerOutputSymbolOfCurrentActor(self, receptionTime, message, symbol):
        """Add a symbol, the message and the reception time in the list"""
        i = self.currentActorIOChannelListStore.append()
        self.currentActorIOChannelListStore.set(i, 0, Gtk.STOCK_GO_FORWARD)
        self.currentActorIOChannelListStore.set(i, 1, receptionTime)
        self.currentActorIOChannelListStore.set(i, 2, symbol.getName())
        self.currentActorIOChannelListStore.set(i, 3, message)

    def registerMemoryAccess(self, access, variable, value):
        """Describe in the GUI a memory access"""

        now = datetime.datetime.now()
        receptionTime = now.strftime("%H:%M:%S")

        if variable is not None:
            name = variable.getName()
        else:
            name = "?"

        data = str(value)

        i = self.currentActorMemoryListStore.append()
        self.currentActorMemoryListStore.set(i, 0, access)
        self.currentActorMemoryListStore.set(i, 1, receptionTime)
        self.currentActorMemoryListStore.set(i, 2, name)
        self.currentActorMemoryListStore.set(i, 3, data)

    def updateStatusOfCurrentActor(self):
        """Update the status (displayed) of the current actor"""

        currentActor = self.controller.getCurrentActor()
        if currentActor is not None:
            if currentActor.isActive():
                actorStatus = "active"
                self.stopCurrentActorButton.set_sensitive(True)
                self.startCurrentActorButton.set_sensitive(False)

            else:
                actorStatus = "inactive"
                self.stopCurrentActorButton.set_sensitive(False)
                self.startCurrentActorButton.set_sensitive(True)

            self.statusCurrentActorLabel.set_label(actorStatus)
            self.statusCurrentActorLabel.show()

        self.refreshListOfActors()
