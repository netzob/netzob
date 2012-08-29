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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
from gettext import gettext as _
from gi.repository import Gtk
import gi
from netzob.Common.MMSTD.Dictionary.Memory import Memory
gi.require_version('Gtk', '3.0')
import logging
import threading

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.Tools.Parsers.MMSTDParser import MMSTDXmlParser
from netzob.Common.MMSTD.Actors.Network import NetworkServer
from netzob.Common.MMSTD.Actors.Network import NetworkClient
from netzob.Common.MMSTD.Dictionary import AbstractionLayer
from netzob.Common.MMSTD.Actors import MMSTDVisitor
from netzob.Simulator.XDotWidget import XDotWidget


#+----------------------------------------------
#| UISimulator:
#|     GUI for the simulation of actors
#+----------------------------------------------
class UISimulator:

    #+----------------------------------------------
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        self.finish = True

    def save(self, file):
        self.log = logging.getLogger('netzob.Simuator.UISimulator.py')
        self.log.warn(_("The simulation process cannot be saved for the moment"))

    def restart(self):
        """Restart the view"""
        logging.debug("Restart the UISimulator")

    #+----------------------------------------------
    #| Constructor:
    #| @param netzob: the netzob main class
    #+----------------------------------------------
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Simulator.UISimulator.py')
        self.netzob = netzob

        self.actors = []
        self.selectedActor = None
        self.finish = False

        # Init each field with its saved value if it exist
        config = ConfigurationParser()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = Gtk.Table(rows=5, columns=2, homogeneous=False)
        self.panel.show()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Table hosting the form for a new actor
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.tableFormNewActor = Gtk.Table(rows=4, columns=4, homogeneous=True)

        # Actor's name
        label_actorName = Gtk.Label(label=_("Actor's name:"))
        label_actorName.show()
        self.entry_actorName = Gtk.Entry()

        if config.get("simulating", "actorName") is not None:
            self.entry_actorName.set_text(config.get("simulating", "actorName"))
        else:
            self.entry_actorName.set_text("")

        self.entry_actorName.show()
        self.tableFormNewActor.attach(label_actorName, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_actorName, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # Type of actor
        label_typeOfActor = Gtk.Label(label=_("Type of actor:"))
        label_typeOfActor.show()
        self.combo_typeOfActor = Gtk.ComboBoxText.new_with_entry()
        self.combo_typeOfActor.set_model(Gtk.ListStore(str))
        self.combo_typeOfActor.append_text("CLIENT")
        self.combo_typeOfActor.append_text("MASTER")

        if (config.get("simulating", "typeOfActor") == "CLIENT"):
            self.combo_typeOfActor.set_active(0)
        if (config.get("simulating", "typeOfActor") == "MASTER"):
            self.combo_typeOfActor.set_active(1)

        self.combo_typeOfActor.show()
        self.tableFormNewActor.attach(label_typeOfActor, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.combo_typeOfActor, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Network layer actor
        label_typeOfNetworkActor = Gtk.Label(label=_("Network layer:"))
        label_typeOfNetworkActor.show()
        self.combo_typeOfNetworkActor = Gtk.ComboBoxText.new_with_entry()
        self.combo_typeOfNetworkActor.set_model(Gtk.ListStore(str))
        self.combo_typeOfNetworkActor.append_text("CLIENT")
        self.combo_typeOfNetworkActor.append_text("SERVER")

        if (config.get("simulating", "networkLayer") == "CLIENT"):
            self.combo_typeOfNetworkActor.set_active(0)
        if (config.get("simulating", "networkLayer") == "SERVER"):
            self.combo_typeOfNetworkActor.set_active(1)

        self.combo_typeOfNetworkActor.show()
        self.tableFormNewActor.attach(label_typeOfNetworkActor, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.combo_typeOfNetworkActor, 1, 2, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Network protocol
        label_protocolOfNetworkActor = Gtk.Label(label=_("Network Protocol:"))
        label_protocolOfNetworkActor.show()
        self.combo_protocolOfNetworkActor = Gtk.ComboBoxText.new_with_entry()
        self.combo_protocolOfNetworkActor.set_model(Gtk.ListStore(str))
        self.combo_protocolOfNetworkActor.append_text(_("TCP"))
        self.combo_protocolOfNetworkActor.append_text(_("UDP"))

        if (config.get("simulating", "networkProtocol") == "TCP"):
            self.combo_protocolOfNetworkActor.set_active(0)
        if (config.get("simulating", "networkProtocol") == "UDP"):
            self.combo_protocolOfNetworkActor.set_active(1)

        self.combo_protocolOfNetworkActor.show()
        self.tableFormNewActor.attach(label_protocolOfNetworkActor, 0, 1, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.combo_protocolOfNetworkActor, 1, 2, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # IP
        label_IP = Gtk.Label(label=_("IP:"))
        label_IP.show()
        self.entry_IP = Gtk.Entry()
        if (config.get("simulating", "ip") is not None):
            self.entry_IP.set_text(config.get("simulating", "ip"))
        else:
            self.entry_IP.set_text("")

        self.entry_IP.show()
        self.tableFormNewActor.attach(label_IP, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_IP, 3, 4, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # S-PORT
        label_SPort = Gtk.Label(label=_("Source Port:"))
        label_SPort.show()
        self.entry_SPort = Gtk.Entry()
        self.entry_SPort.show()
        self.tableFormNewActor.attach(label_SPort, 2, 3, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_SPort, 3, 4, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # D-PORT
        label_Port = Gtk.Label(label=_("Destination Port:"))
        label_Port.show()
        self.entry_Port = Gtk.Entry()

        if (config.getInt("simulating", "port") is not None):
            self.entry_Port.set_text(str(config.getInt("simulating", "port")))
        else:
            self.entry_Port.set_text("")

        self.entry_Port.show()
        self.tableFormNewActor.attach(label_Port, 2, 3, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_Port, 3, 4, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Add actor button
        self.button_addActor = Gtk.Button(Gtk.STOCK_OK)
        self.button_addActor.set_label(_("Add actor"))
        self.button_addActor.connect("clicked", self.addActor)
        self.button_addActor.show()
        self.tableFormNewActor.attach(self.button_addActor, 3, 4, 3, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.tableFormNewActor.show()
        self.panel.attach(self.tableFormNewActor, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Panel hosting the list of curent actors
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_listActiveActors = Gtk.ScrolledWindow()
        self.treestore_listActiveActors = Gtk.TreeStore(str, str)  # actor's name, typ

#        self.treestore_listActiveActors.append(None, ["actor1", "Server"])
#        self.treestore_listActiveActors.append(None, ["actor2", "Client"])
#        self.treestore_listActiveActors.append(None, ["actor3", "Client"])
#        self.treestore_listActiveActors.append(None, ["actor4", "Client"])
#        self.treestore_listActiveActors.append(None, ["actor5", "Client"])

        treeview_listActiveActors = Gtk.TreeView(self.treestore_listActiveActors)
        treeview_listActiveActors.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        treeview_listActiveActors.set_size_request(300, -1)
        treeview_listActiveActors_selection = treeview_listActiveActors.get_selection()
        treeview_listActiveActors_selection.connect("changed", self.actorDetails)
        cell = Gtk.CellRendererText()
        # main col
        column_listActiveActors_name = Gtk.TreeViewColumn(_("Active actors"))
        column_listActiveActors_name.pack_start(cell, True)
        column_listActiveActors_name.add_attribute(cell, "text", 0)
        treeview_listActiveActors.append_column(column_listActiveActors_name)
        treeview_listActiveActors.show()
        scroll_listActiveActors.add(treeview_listActiveActors)
        scroll_listActiveActors.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_listActiveActors.show()
        self.panel.attach(scroll_listActiveActors, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Inputs
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_inputs = Gtk.ScrolledWindow()
        self.treestore_inputs = Gtk.TreeStore(str, str, str)  # date, input message symbol

#        self.treestore_inputs.append(None, ["12:45:01", "message 1"])
#        self.treestore_inputs.append(None, ["12:45:11", "message 2"])
#        self.treestore_inputs.append(None, ["12:45:21", "message 3"])
#        self.treestore_inputs.append(None, ["12:45:23", "message 4"])
#        self.treestore_inputs.append(None, ["12:45:23", "message 5"])

        treeview_inputs = Gtk.TreeView(self.treestore_inputs)
        treeview_inputs.get_selection().set_mode(Gtk.SelectionMode.NONE)
        treeview_inputs.set_size_request(300, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = Gtk.CellRendererText()
        # col date
        column_inputs_date = Gtk.TreeViewColumn(_("Date"))
        column_inputs_date.pack_start(cell, True)
        column_inputs_date.add_attribute(cell, "text", 0)
        # col message
        column_inputs_message = Gtk.TreeViewColumn(_("Received message"))
        column_inputs_message.pack_start(cell, True)
        column_inputs_message.add_attribute(cell, "text", 1)
        # col symbol
        column_inputs_symbol = Gtk.TreeViewColumn(_("Symbol"))
        column_inputs_symbol.pack_start(cell, True)
        column_inputs_symbol.add_attribute(cell, "text", 2)
        treeview_inputs.append_column(column_inputs_date)
        treeview_inputs.append_column(column_inputs_message)
        treeview_inputs.append_column(column_inputs_symbol)
        treeview_inputs.show()
        scroll_inputs.add(treeview_inputs)
        scroll_inputs.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_inputs.show()
        self.panel.attach(scroll_inputs, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Outputs
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_outputs = Gtk.ScrolledWindow()
        self.treestore_outputs = Gtk.TreeStore(str, str, str)  # date, output message, symbol

#        self.treestore_outputs.append(None, ["12:45:01", "message 1"])
#        self.treestore_outputs.append(None, ["12:45:11", "message 2"])
#        self.treestore_outputs.append(None, ["12:45:21", "message 3"])
#        self.treestore_outputs.append(None, ["12:45:23", "message 4"])
#        self.treestore_outputs.append(None, ["12:45:23", "message 5"])

        treeview_outputs = Gtk.TreeView(self.treestore_outputs)
        treeview_outputs.get_selection().set_mode(Gtk.SelectionMode.NONE)
        treeview_outputs.set_size_request(300, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = Gtk.CellRendererText()
        # col date
        column_outputs_date = Gtk.TreeViewColumn(_("Date"))
        column_outputs_date.pack_start(cell, True)
        column_outputs_date.add_attribute(cell, "text", 0)
        # col message
        column_outputs_message = Gtk.TreeViewColumn(_("Emitted message"))
        column_outputs_message.pack_start(cell, True)
        column_outputs_message.add_attribute(cell, "text", 1)
        # col symbol
        column_outputs_symbol = Gtk.TreeViewColumn(_("Emitted message"))
        column_outputs_symbol.pack_start(cell, True)
        column_outputs_symbol.add_attribute(cell, "text", 2)
        treeview_outputs.append_column(column_outputs_date)
        treeview_outputs.append_column(column_outputs_message)
        treeview_outputs.append_column(column_outputs_symbol)
        treeview_outputs.show()
        scroll_outputs.add(treeview_outputs)
        scroll_outputs.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_outputs.show()
        self.panel.attach(scroll_outputs, 0, 1, 2, 3, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Memory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_memory = Gtk.ScrolledWindow()
        self.treestore_memory = Gtk.TreeStore(str, str, str)  # name, type, value

#        self.treestore_memory.append(None, ["var1", "IP", "192.168.0.10"])
#        self.treestore_memory.append(None, ["var2", "WORD", "PSEUDO"])
#        self.treestore_memory.append(None, ["var3", "IP", "192.178.12.12"])

        treeview_memory = Gtk.TreeView(self.treestore_memory)
        treeview_memory.get_selection().set_mode(Gtk.SelectionMode.NONE)
        treeview_memory.set_size_request(300, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = Gtk.CellRendererText()
        # col name
        column_memory_name = Gtk.TreeViewColumn(_("Variable"))
        column_memory_name.pack_start(cell, True)
        column_memory_name.add_attribute(cell, "text", 0)
        # col type
        column_memory_type = Gtk.TreeViewColumn(_("Type"))
        column_memory_type.pack_start(cell, True)
        column_memory_type.add_attribute(cell, "text", 1)
        # col Value
        column_memory_value = Gtk.TreeViewColumn(_("Value"))
        column_memory_value.pack_start(cell, True)
        column_memory_value.add_attribute(cell, "text", 2)

        treeview_memory.append_column(column_memory_name)
        treeview_memory.append_column(column_memory_type)
        treeview_memory.append_column(column_memory_value)
        treeview_memory.show()
        scroll_memory.add(treeview_memory)
        scroll_memory.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_memory.show()
        self.panel.attach(scroll_memory, 0, 1, 3, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Panel for the Model
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.xdotWidget = XDotWidget()

        self.xdotWidget.show_all()
        self.xdotWidget.set_size_request(300, 300)
        self.panel.attach(self.xdotWidget, 1, 2, 1, 4, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Break and stop
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.tableForBreakAndStop = Gtk.Table(rows=1, columns=3, homogeneous=True)
        # Add start button
        self.button_startActor = Gtk.Button(Gtk.STOCK_OK)
        self.button_startActor.set_label(_("START"))
        self.button_startActor.connect("clicked", self.startSelectedActor)
        self.button_startActor.show()
        self.tableForBreakAndStop.attach(self.button_startActor, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Add stop button
        self.button_stopActor = Gtk.Button(Gtk.STOCK_OK)
        self.button_stopActor.set_label(_("STOP"))
        self.button_stopActor.connect("clicked", self.stopSelectedActor)
        self.button_stopActor.show()
        self.tableForBreakAndStop.attach(self.button_stopActor, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        #Add delete actor button
        self.button_delActor = Gtk.Button(Gtk.STOCK_OK)
        self.button_delActor.set_label(_("DELETE"))
        self.button_delActor.connect("clicked", self.deleteSelectedActor)
        self.button_delActor.show()
        self.tableForBreakAndStop.attach(self.button_delActor, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.tableForBreakAndStop.show()
        self.panel.attach(self.tableForBreakAndStop, 1, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

        # Update the GUI
        self.refreshGUI(1)

        self._actionGroup = Gtk.ActionGroup("simulatorActionGroup")

    @property
    def view(self):
        return self

    def getPanel(self):
        return self.panel

    def getActionGroup(self):
        return self._actionGroup

    # Return toolbar and menu
    def getMenuToolbarUIDefinition(self):
        return ""

    #+----------------------------------------------
    #| startSelectedActor:
    #| Starts the selected actor
    #+----------------------------------------------
    def startSelectedActor(self, widget):
        if self.selectedActor is None:
            return

        self.log.info(_("Start the actor {0}").format(self.selectedActor.getName()))
        self.selectedActor.start()

    #+----------------------------------------------
    #| stopSelectedActor:
    #| Stops the selected actor
    #+----------------------------------------------
    def stopSelectedActor(self, widget):
        if self.selectedActor is None:
            return

        self.log.info(_("Stop the actor {0}").format(self.selectedActor.getName()))
        self.selectedActor.stop()

    #+----------------------------------------------
    #| deleteSelectedActor:
    #| Delete the selected actor (if stopped)
    #+----------------------------------------------
    def deleteSelectedActor(self, widget):
        if self.selectedActor is None:
            return

        if self.selectedActor.isActive():
            self.log.info(_("Impossible to delete an active actor. It must be stopped before"))
            return

        self.log.info(_("Delete the actor {0}").format(self.selectedActor.getName()))
        self.actors.remove(self.selectedActor)
        self.treestore_listActiveActors.clear()
        self.selectedActor = None

    #+----------------------------------------------
    #| addActor:
    #| Creates and registers an actor based on the form
    #+----------------------------------------------
    def addActor(self, widget):
        # Retrieves the value of the form to create the actor
        actorName = self.entry_actorName.get_text()
        actorGrammarType = self.combo_typeOfActor.get_active_text()
        actorNetworkProtocol = self.combo_protocolOfNetworkActor.get_active_text()
        actorNetworkType = self.combo_typeOfNetworkActor.get_active_text()
        actorIP = self.entry_IP.get_text()
        actorSPort = self.entry_SPort.get_text()
        actorPort = self.entry_Port.get_text()

        # We verify we have everything and the actor's name is unique
        for actor in self.actors:
            if actor.getName() == actorName:
                self.log.warn(_("Impossible to create the requested actor since another one has the same name"))
                return

        self.log.info(_("Will add an actor named {0}").format(actorName))

        grammar = self.netzob.getCurrentProject().getGrammar()
        # We create an actor based on given informations
        if actorGrammarType == "MASTER":
            isMaster = True
        else:
            isMaster = False

        # Create the network layer
        if actorNetworkType == "SERVER":
            communicationChannel = NetworkServer.NetworkServer(actorIP, actorNetworkProtocol, int(actorPort), int(actorSPort))
        else:
            communicationChannel = NetworkClient.NetworkClient(actorIP, actorNetworkProtocol, int(actorPort), int(actorSPort))

        # Create the abstraction layer for this connection
        abstractionLayer = AbstractionLayer.AbstractionLayer(communicationChannel, self.netzob.getCurrentProject().getVocabulary(), Memory(self.netzob.getCurrentProject().getVocabulary().getVariables()))

        # And we create an MMSTD visitor for this
        visitor = MMSTDVisitor.MMSTDVisitor(actorName, grammar.getAutomata(), isMaster, abstractionLayer)

        # add the actor to the list
        self.actors.append(visitor)

        # update the list of actors
        self.updateListOfActors()

#        # we save the form in the configuration considering its a valid one
#        config = ConfigurationParser()
#        config.set("simulating", "actorName", actorName)
#        config.set("simulating", "typeOfActor", actorGrammarType)
#        config.set("simulating", "networkLayer", actorNetworkType)
#        config.set("simulating", "networkProtocol", actorNetworkProtocol)
#        config.set("simulating", "ip", actorIP)
#        config.set("simulating", "port", int(actorPort))

    def updateListOfActors(self):
#        self.treestore_listActiveActors.clear()
        for actor in self.actors:

            # Do we add this actor ?
            treestoreActor = None
            for line in self.treestore_listActiveActors:
                if line[0] == actor.getName():
                    treestoreActor = self.treestore_listActiveActors.get_iter(line.path)
                    found = True

            if treestoreActor is None:
                treestoreActor = self.treestore_listActiveActors.append(None, [actor.getName(), "type"])

            # Retrieve generates instances by the communication channel
            communicationChannel = actor.getAbstractionLayer().getCommunicationChannel()
            instances = communicationChannel.getGeneratedInstances()
            for instance in instances:

                # do we add this instance
                found = False
                for line in self.treestore_listActiveActors:
                    if line[0] == instance.getName():
                        found = True
                if not found:
                    self.treestore_listActiveActors.append(treestoreActor, [instance.getName(), "type"])

    def actorDetails(self, selection):
        self.selectedActor = None
        actorName = ""
        (model, iter) = selection.get_selected()

        if(iter):
            if(model.iter_is_valid(iter)):
                actorName = model.get_value(iter, 0)
                #actorType = model.get_value(iter, 1)

        for actor in self.actors:
            if actor.getName() == actorName:
                self.selectedActor = actor
            # Retrieve generates instances by the communication channel
            communicationChannel = actor.getAbstractionLayer().getCommunicationChannel()
            instances = communicationChannel.getGeneratedInstances()
            for instance in instances:
                if instance.getName() == actorName:
                    self.selectedActor = instance

        if self.selectedActor is None:
            self.log.warn(_("Impossible to retrieve the requested actor"))
            return

        # Now we update the GUI based on the actor
        self.updateGUIForActor()

    def updateGUIForActor(self):
        if self.selectedActor is None:
            return

        # First we display its model
        automata = self.selectedActor.getModel()
        self.xdotWidget.drawAutomata(automata)
        self.xdotWidget.show_all()

        # Now we display its received message
        self.treestore_inputs.clear()
        for inputMessage in self.selectedActor.getInputMessages():
            self.treestore_inputs.append(None, inputMessage)

        # Now we display its emitted message
        self.treestore_outputs.clear()
        for outputMessage in self.selectedActor.getOutputMessages():
            self.treestore_outputs.append(None, outputMessage)

        # Now we update its memory
        self.treestore_memory.clear()
        for memory_id in self.selectedActor.getMemory().recallAll().keys():
            self.treestore_memory.append(None, [memory_id, "type", self.selectedActor.getMemory().recallAll()[memory_id]])

    def refreshGUI(self, tempo=0.5):
#TODO
#        if not self.finish:
#            threading.Timer(tempo, self.refreshGUI, [tempo]).start()
#            self.updateListOfActors()
#            self.updateGUIForActor()
        pass
