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
        self.ProtocolEntry = gtk.Entry()
        self.ProtocolEntry.show()
        mainTable.attach(ProtocolLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(self.ProtocolEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
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
    
    def startInference(self, button):
        
        # We retrieve the specified value
        actorIP = self.IPEntry.get_text()
        actorNetworkProtocol = self.ProtocolEntry.get_text()
        actorPort = int(self.PortEntry.get_text())
        maxNumberOfState = int(self.MaxStatesEntry.get_text())
        
        self.dialog.destroy()
        
        # Lets create a simple network oracle
        oracleCommunicationChannel = NetworkClient(actorIP, actorNetworkProtocol, actorPort)
        # Lets create an equivalence oracle
        equivalenceOracle = WMethodNetworkEquivalenceOracle(oracleCommunicationChannel, maxNumberOfState)
        # Lets start the automatif inferer
        inferer = GrammarInferer(self.project.getVocabulary(), oracleCommunicationChannel, equivalenceOracle)
        resultedAutomaton = inferer.infer()
        
        print resultedAutomaton.getDotCode()
        
        
        
        
