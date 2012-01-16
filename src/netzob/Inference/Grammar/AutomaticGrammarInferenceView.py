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
import logging
import gtk
import pygtk
import uuid
from netzob.Inference.Grammar.GrammarInferer import GrammarInferer
from netzob.Inference.Grammar.EquivalenceOracles.WMethodNetworkEquivalenceOracle import WMethodNetworkEquivalenceOracle
from netzob.Common.MMSTD.Actors.Network.NetworkClient import NetworkClient
from netzob.Simulator.XDotWidget import XDotWidget

pygtk.require('2.0')

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------


#+---------------------------------------------- 
#| AutomaticGrammarInferenceView :
#|     Class dedicated to host the creation of the view for the inference
#+---------------------------------------------- 
class AutomaticGrammarInferenceView(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self, project):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.AutomaticGrammarInferenceView.py')
        self.project = project
        
    def display(self):
        # Display the form for the creation of a word variable
        self.dialog = gtk.Dialog(title="Configuration of the automatic inference", flags=0, buttons=None)
        
        mainTable = gtk.Table(rows=6, columns=2, homogeneous=False)

        # IP of the server
        IPLabel = gtk.Label("IP of the server :")
        IPLabel.show()
        self.IPEntry = gtk.Entry()
        self.IPEntry.show()
        mainTable.attach(IPLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.IPEntry, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Protocol of the server
        ProtocolLabel = gtk.Label("Protocol :")
        ProtocolLabel.show()
        self.combo_protocolOfNetworkActor = gtk.combo_box_entry_new_text()
        self.combo_protocolOfNetworkActor.set_model(gtk.ListStore(str))
        self.combo_protocolOfNetworkActor.append_text("TCP")
        self.combo_protocolOfNetworkActor.append_text("UDP")
        self.combo_protocolOfNetworkActor.set_active(0)
        self.combo_protocolOfNetworkActor.show()

        mainTable.attach(ProtocolLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.combo_protocolOfNetworkActor, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Port of the server
        PortLabel = gtk.Label("Port :")
        PortLabel.show()
        self.PortEntry = gtk.Entry()
        self.PortEntry.show()
        mainTable.attach(PortLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.PortEntry, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Estimated number of states
        MaxStatesLabel = gtk.Label("Maximum number of states :")
        MaxStatesLabel.show()
        self.MaxStatesEntry = gtk.Entry()
        self.MaxStatesEntry.show()
        mainTable.attach(MaxStatesLabel, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.MaxStatesEntry, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Create button
        startButton = gtk.Button("Start inference")
        startButton.show()
        startButton.connect("clicked", self.startInference)
        mainTable.attach(startButton, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()
        
    def createInferringStatusView(self):
        self.dialog = gtk.Dialog(title="Execution of the inferring process", flags=0, buttons=None)
        
        mainTable = gtk.Table(rows=5, columns=4, homogeneous=False)
        
        # Insert the current Hypothesis of the automata
        self.xdotWidget = XDotWidget()
        self.xdotWidget.show_all()       
        mainTable.attach(self.xdotWidget, 0, 2, 0, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Insert the updated list of requests and associated responses
        scroll_requests = gtk.ScrolledWindow()
        self.treestore_queries = gtk.TreeStore(str, str, str) # queries, responses, color
        treeview_queries = gtk.TreeView(self.treestore_queries)
        treeview_queries.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview_queries.set_size_request(-1, 250)
#        treeview_queries.connect('button-press-event', self.button_press_on_transitions)
        cell = gtk.CellRendererText()
        # col : membership queries
        col_queries_querie = gtk.TreeViewColumn('Membership query')
        col_queries_querie.pack_start(cell, True)
        col_queries_querie.set_attributes(cell, text=1)
        treeview_queries.append_column(col_queries_querie)
        # col : responses to queries
        column_queries_responses = gtk.TreeViewColumn('Responses')
        column_queries_responses.pack_start(cell, True)
        column_queries_responses.set_attributes(cell, text=2)
        treeview_queries.append_column(column_queries_responses)
        scroll_requests.add(treeview_queries)
        scroll_requests.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_requests.show()
        mainTable.attach(scroll_requests, 2, 4, 0, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Insert the status message
        self.statusLabel = gtk.Label("A number of X states has been created - Current turn contains N MQ")
        self.statusLabel.show()
        mainTable.attach(self.statusLabel, 0, 3, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Insert the stop button
        self.stopButton = gtk.Button("Stop")
        self.stopButton.show()
#        self.stopButton.connect("clicked", self.startInference)
        mainTable.attach(self.stopButton, 3, 4, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.dialog.vbox.pack_end(mainTable, True, True, 0)
        self.dialog.show_all()
        
    
    def startInference(self, button):
        
        # We retrieve the specified value
        actorIP = self.IPEntry.get_text()
        actorNetworkProtocol = self.combo_protocolOfNetworkActor.get_active_text()
        actorPort = int(self.PortEntry.get_text())
        maxNumberOfState = int(self.MaxStatesEntry.get_text())
        
        # Close the current dialog
        self.dialog.destroy()
        
        # Open the new dialog which shows the status of the infering process
        self.createInferringStatusView()
#        
#        # Lets create a simple network oracle
#        oracleCommunicationChannel = NetworkClient(actorIP, actorNetworkProtocol, actorPort)
#        # Lets create an equivalence oracle
#        equivalenceOracle = WMethodNetworkEquivalenceOracle(oracleCommunicationChannel, maxNumberOfState)
#        # Lets start the automatif inferer
#        inferer = GrammarInferer(self.project.getVocabulary(), oracleCommunicationChannel, equivalenceOracle)
#        resultedAutomaton = inferer.infer()
#        
#        
#        inferedGrammar = resultedAutomaton.toGrammar()
#        if inferedGrammar != None :
#            self.log.info("A grammar has been successfully infered.")
#            self.project.setGrammar(inferedGrammar)
#        else :
#            self.log.warn("The automatic inference process has failed, no grammar was computed")
#            
#        
        
        
