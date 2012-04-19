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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import gtk
import pygtk
import gobject

pygtk.require('2.0')

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Grammar.GrammarInferer import GrammarInferer
from netzob.Inference.Grammar.EquivalenceOracles.WMethodNetworkEquivalenceOracle import WMethodNetworkEquivalenceOracle
from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient
from netzob.Simulator.XDotWidget import XDotWidget
from netzob.Common.Threads.Tasks.ThreadedTask import ThreadedTask
from netzob.Common.Threads.Job import Job
from netzob.Common.MMSTD.Actors.Network.NetworkServer import NetworkServer
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol


#+----------------------------------------------
#| AutomaticGrammarInferenceView:
#|     Class dedicated to host the creation of the view for the inference
#+----------------------------------------------
class AutomaticGrammarInferenceView(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.AutomaticGrammarInferenceView.py')
        self.project = project
        self.inferer = None
        self.computedAutomaton = None
        self.finish = False

    def display(self):
        # Display the form for the creation of a word variable
        self.dialog = gtk.Dialog(title="Configuration of the automatic inference", flags=0, buttons=None)

        mainTable = gtk.Table(rows=9, columns=2, homogeneous=False)

        # Infer a client or a server
        targetOfInferenceLabel = gtk.Label("Target : ")
        targetOfInferenceLabel.show()
        self.targetOfInferenceCombo = gtk.ComboBox()
        self.targetOfInferenceCombo.set_model(gtk.ListStore(str))
        targetOfInferenceComboCell = gtk.CellRendererText()
        self.targetOfInferenceCombo.pack_start(targetOfInferenceComboCell, True)
        self.targetOfInferenceCombo.add_attribute(targetOfInferenceComboCell, 'text', 0)
        self.targetOfInferenceCombo.append_text("CLIENT")
        self.targetOfInferenceCombo.append_text("SERVER")
        self.targetOfInferenceCombo.show()
        mainTable.attach(targetOfInferenceLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.targetOfInferenceCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # IP of the server
        IPLabel = gtk.Label("IP :")
        IPLabel.show()
        self.IPEntry = gtk.Entry()
        self.IPEntry.show()
        mainTable.attach(IPLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.IPEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Protocol of the server
        ProtocolLabel = gtk.Label("Protocol :")
        ProtocolLabel.show()
        self.combo_protocolOfNetworkActor = gtk.combo_box_entry_new_text()
        self.combo_protocolOfNetworkActor.set_model(gtk.ListStore(str))
        self.combo_protocolOfNetworkActor.append_text("TCP")
        self.combo_protocolOfNetworkActor.append_text("UDP")
        self.combo_protocolOfNetworkActor.set_active(0)
        self.combo_protocolOfNetworkActor.show()

        mainTable.attach(ProtocolLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.combo_protocolOfNetworkActor, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Source port
        SourcePortLabel = gtk.Label("Our port :")
        SourcePortLabel.show()
        self.ourPortEntry = gtk.Entry()
        self.ourPortEntry.show()
        mainTable.attach(SourcePortLabel, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.ourPortEntry, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Port of the server
        PortLabel = gtk.Label("Target Port :")
        PortLabel.show()
        self.targetPortEntry = gtk.Entry()
        self.targetPortEntry.show()
        mainTable.attach(PortLabel, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.targetPortEntry, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Estimated number of states
        MaxStatesLabel = gtk.Label("Maximum number of states :")
        MaxStatesLabel.show()
        self.MaxStatesEntry = gtk.Entry()
        self.MaxStatesEntry.show()
        mainTable.attach(MaxStatesLabel, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.MaxStatesEntry, 1, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Script to execute to reset the implementation
        scriptLabel = gtk.Label("Reseting script :")
        scriptLabel.show()
        self.scriptEntry = gtk.Entry()
        self.scriptEntry.show()
        mainTable.attach(scriptLabel, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.scriptEntry, 1, 2, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Create button
        startButton = gtk.Button("Start inference")
        startButton.show()
        startButton.connect("clicked", self.startInference)
        mainTable.attach(startButton, 1, 2, 7, 8, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()

    def createInferringStatusView(self):
        self.dialog = gtk.Dialog(title="Execution of the inferring process", flags=0, buttons=None)

        mainTable = gtk.Table(rows=5, columns=4, homogeneous=False)

        # Insert the current Hypothesis of the automata
        self.xdotWidget = XDotWidget()
        self.xdotWidget.show_all()
        self.xdotWidget.set_size_request(500, 500)
        mainTable.attach(self.xdotWidget, 0, 2, 0, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Insert the updated list of requests and associated responses
        scroll_requests = gtk.ScrolledWindow()
        self.treestore_queries = gtk.TreeStore(str, str, str)  # queries, responses, color
        treeview_queries = gtk.TreeView(self.treestore_queries)
        treeview_queries.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview_queries.set_size_request(500, 500)
#        treeview_queries.connect('button-press-event', self.button_press_on_transitions)
        cell = gtk.CellRendererText()
        # col : membership queries
        col_queries_querie = gtk.TreeViewColumn('Membership queries')
        col_queries_querie.pack_start(cell, True)
        col_queries_querie.set_attributes(cell, text=0)
        treeview_queries.append_column(col_queries_querie)
        # col : responses to queries
        column_queries_responses = gtk.TreeViewColumn('Responses')
        column_queries_responses.pack_start(cell, True)
        column_queries_responses.set_attributes(cell, text=1)
        treeview_queries.append_column(column_queries_responses)
        scroll_requests.add(treeview_queries)
        scroll_requests.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_requests.show()
        mainTable.attach(scroll_requests, 2, 4, 0, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Progress bar
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.progressbar.show()
#        # Insert the status message
#        self.statusLabel = gtk.Label("A number of X states has been created - Current turn contains N MQ")
#        self.statusLabel.show()
        mainTable.attach(self.progressbar, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Insert the stop button
        self.stopButton = gtk.Button("Stop")
        self.stopButton.show()
        self.stopButton.connect("clicked", self.stopInference)
        mainTable.attach(self.stopButton, 2, 3, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Insert the Save button
        self.saveButton = gtk.Button("Save as Grammar")
        self.saveButton.show()
        self.saveButton.connect("clicked", self.saveGrammar)
        mainTable.attach(self.saveButton, 3, 4, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()

    def do_pulse(self, *args):
        if self.finish == False:
            self.progressbar.pulse()
            return True
        return False

    def callback_submitedQuery(self, query, resultQuery):
        if query == None:
            self.log.debug("Impossible to show a Null query")
            return

        # Create a str view of the Query
        strQuery = ""
        for symbol in query.getSymbols():
            strSymbol = ""
            if symbol.getType() == "DictionarySymbol":
                strSymbol = symbol.getName()
            else:
                strSymbol = "EmptySymbol"

            strQuery = strQuery + strSymbol + ", "

        # Create a str view of the Result Query
        strResultQuery = ""
        for symbol in resultQuery:
            strSymbol = ""
            if symbol.getType() == "DictionarySymbol":
                strSymbol = symbol.getName()
            else:
                strSymbol = str(symbol)

            strResultQuery = strResultQuery + strSymbol + ","

        self.treestore_queries.append(None, [strQuery, strResultQuery, "blue"])

    def callback_hypotheticalAutomaton(self, hypotheticalAutomaton):
        if hypotheticalAutomaton != None:
            self.computedAutomaton = hypotheticalAutomaton
            self.xdotWidget.set_dotcode(self.computedAutomaton.getDotCode())

    def stopInference(self, button):
        self.finish = True
        self.log.info("Stop the inferer")
        self.inferer.stop()

    def startInferer(self):
        (yield ThreadedTask(self.inferer.infer))
        self.computedAutomaton = self.inferer.getInferedAutomaton()
        self.finish = True

    def saveGrammar(self, button):
        if self.computedAutomaton != None:
            self.log.debug("Saving the computed automata as the grammar of current project")
            self.project.getGrammar().setAutomata(self.computedAutomaton)
            self.dialog.destroy()

    def startInference(self, button):
        # We retrieve the specified value
        actorType = self.targetOfInferenceCombo.get_active_text()
        actorIP = self.IPEntry.get_text()
        actorNetworkProtocol = self.combo_protocolOfNetworkActor.get_active_text()
        ourPort = int(self.ourPortEntry.get_text())
        targetPort = int(self.targetPortEntry.get_text())
        scriptFilename = self.scriptEntry.get_text()
        maxNumberOfState = int(self.MaxStatesEntry.get_text())

        inputDictionary = []
        for symbol in self.project.getVocabulary().getSymbols():
            if symbol.getName() == "LOGIN" or symbol.getName() == "EXECUTE" or symbol.getName() == "LOGOUT" or symbol.getName() == "DOWNLOAD":
                inputDictionary.append(symbol)
        inputDictionary.append(UnknownSymbol())
        # Close the current dialog
        self.dialog.destroy()

        if actorType == "CLIENT":
            # Lets create a simple network oracle
            oracleCommunicationChannel = NetworkServer(actorIP, actorNetworkProtocol, ourPort, targetPort)
        else:
            # Lets create a simple network oracle
            oracleCommunicationChannel = NetworkClient(actorIP, actorNetworkProtocol, targetPort, ourPort)

        # Lets create an equivalence oracle
        equivalenceOracle = WMethodNetworkEquivalenceOracle(oracleCommunicationChannel, maxNumberOfState, scriptFilename)

        # Lets create the automatic inferer
        self.inferer = GrammarInferer(self.project.getVocabulary(), inputDictionary, oracleCommunicationChannel, equivalenceOracle, scriptFilename, self.callback_submitedQuery, self.callback_hypotheticalAutomaton)

        # Open the new dialog which shows the status of the inferring process
        self.createInferringStatusView()

        # Start the progress bar
        gobject.timeout_add(200, self.do_pulse)

        # Start the inferer
        self.job = Job(self.startInferer())
