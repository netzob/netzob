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
import logging
import time
import gtk
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Simulator.XDotWidget import XDotWidget
from netzob.Common.MMSTD.States.impl.NormalState import NormalState
from netzob.Common.MMSTD.MMSTD import MMSTD
from netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition import OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition import CloseChannelTransition
from netzob.Common.MMSTD.Symbols.impl.DictionarySymbol import DictionarySymbol
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition

#+---------------------------------------------------------------------------+
#| UIGrammarInference :
#|    Graphical display of the inferring process of a grammar
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class UIGrammarInference:
    
    #+---------------------------------------------- 
    #| Called when user select a new trace
    #+----------------------------------------------
    def new(self):
        pass

    def update(self):
        self.updateInterface()
    
    def clear(self):
        pass

    def kill(self):
        pass
    
    def save(self, file):
        pass
    
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main class
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Inference.Grammar.UIGrammarInference.py')
        self.netzob = netzob
        
        if netzob.getCurrentProject() != None :
            self.grammar = netzob.getCurrentProject().getGrammar()
        
        self.grammar = None 
        self.states = []
        self.initialState = None
        self.transitions = []
        
        self.panel = gtk.HBox(False, spacing=0)
        self.panel.show()
        
        
        
        # ----------------------------------------
        # Left Panel 
        # ----------------------------------------
        self.mainPanel = gtk.VBox(False, spacing=0)
        self.mainPanel.show()
        
        # First we add a table
        leftFormTable = gtk.Table(rows=7, columns=2, homogeneous=False)
        # Type of the model
        modelLabel = gtk.Label("Type of model : ")
        modelLabel.show()
        self.grammarModelCombo = gtk.combo_box_entry_new_text()
        self.grammarModelCombo.set_model(gtk.ListStore(str))
        possible_choices = ["MMSTD"]
        for i in range(len(possible_choices)):
            self.grammarModelCombo.append_text(str(possible_choices[i]))
        self.grammarModelCombo.show()
        leftFormTable.attach(modelLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        leftFormTable.attach(self.grammarModelCombo, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # We add the button for the automatic inference process
        self.grammarAutomaticInferenceButton = gtk.Button("Open wizard for automatic inference")
#        self.grammarAutomaticInferenceButton.connect("clicked", None)
        self.grammarAutomaticInferenceButton.show()
        self.grammarAutomaticInferenceButton.set_sensitive(False)
        leftFormTable.attach(self.grammarAutomaticInferenceButton, 0, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # CREATE A STATE
        self.createStateButton = gtk.Button("Create a state")
        self.createStateButton.show()
        self.createStateButton.connect("clicked", self.createState)
        self.createStateButton.set_sensitive(False)
        leftFormTable.attach(self.createStateButton, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # The list of current states
        scroll_listStates = gtk.ScrolledWindow()
        self.treestore_listStates = gtk.TreeStore(str, str, str) # id, name, type        
        treeview_listStates = gtk.TreeView(self.treestore_listStates)
        treeview_listStates.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview_listStates.set_size_request(-1, 250)
#        treeview_listStates.connect("cursor-changed", self.actorDetails)
        cell = gtk.CellRendererText()
        # main col
        column_listStates_name = gtk.TreeViewColumn('State name')
        column_listStates_name.pack_start(cell, True)
        column_listStates_name.set_attributes(cell, text=1)
        treeview_listStates.append_column(column_listStates_name)
        # main col
        column_listStates_type = gtk.TreeViewColumn('State Type')
        column_listStates_type.pack_start(cell, True)
        column_listStates_type.set_attributes(cell, text=2)
        treeview_listStates.append_column(column_listStates_type)
        treeview_listStates.show()
        scroll_listStates.add(treeview_listStates)
        scroll_listStates.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_listStates.show()
        leftFormTable.attach(scroll_listStates, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # CREATE A TRANSITION
        self.createTransitionButton = gtk.Button("Create a transition")
        self.createTransitionButton.show()
        self.createTransitionButton.connect("clicked", self.createTransition)
        self.createTransitionButton.set_sensitive(False)
        leftFormTable.attach(self.createTransitionButton, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # The list of current transitions
        scroll_listTransitions = gtk.ScrolledWindow()
        self.treestore_listTransitions = gtk.TreeStore(str, str, str, str, str) # id, name, start state, end state, type   
        treeview_listTransitions = gtk.TreeView(self.treestore_listTransitions)
        treeview_listTransitions.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview_listTransitions.set_size_request(-1, 250)
#        treeview_listStates.connect("cursor-changed", self.actorDetails)
        cell = gtk.CellRendererText()
        # col : name of the transition
        column_listTransitions_name = gtk.TreeViewColumn('Transition name')
        column_listTransitions_name.pack_start(cell, True)
        column_listTransitions_name.set_attributes(cell, text=1)
        treeview_listTransitions.append_column(column_listTransitions_name)
        # col : start state
        column_listTransitions_startState = gtk.TreeViewColumn('Start state')
        column_listTransitions_startState.pack_start(cell, True)
        column_listTransitions_startState.set_attributes(cell, text=2)
        treeview_listTransitions.append_column(column_listTransitions_startState)
        # col : end state
        column_listTransitions_endState = gtk.TreeViewColumn('End state')
        column_listTransitions_endState.pack_start(cell, True)
        column_listTransitions_endState.set_attributes(cell, text=3)
        treeview_listTransitions.append_column(column_listTransitions_endState)
        # col : type
        column_listTransitions_type = gtk.TreeViewColumn('Type')
        column_listTransitions_type.pack_start(cell, True)
        column_listTransitions_type.set_attributes(cell, text=4)
        treeview_listTransitions.append_column(column_listTransitions_type)
        treeview_listTransitions.show()
        scroll_listTransitions.add(treeview_listTransitions)
        scroll_listTransitions.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_listTransitions.show()
        leftFormTable.attach(scroll_listTransitions, 0, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        leftFormTable.show()
        self.mainPanel.pack_start(leftFormTable, False, False, 0)
        
        self.panel.pack_start(self.mainPanel, False, False, 0)
        
        # ----------------------------------------
        # Right panel
        # ----------------------------------------
        self.rightPanel = gtk.HPaned()
        self.rightPanel.show()
        self.panel.pack_start(self.rightPanel, True, True, 0)
        
        
        self.xdotWidget = XDotWidget()
        self.xdotWidget.show_all()
#        self.xdotWidget.set_size_request(500, -1)  
        
        self.rightPanel.add(self.xdotWidget)
          
          
    def createTransition(self, widget):
        self.log.debug("Opening the dialog for the creation of a new transition")
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the new transition')
        
        # Create the ID of the new transition
        transitionID = str(uuid.uuid4())
        
        mainTable = gtk.Table(rows=5, columns=2, homogeneous=False)
        
        transitionIDLabel = gtk.Label("ID :")
        transitionIDLabel.show()
        transitionIDValueLabel = gtk.Label(transitionID)
        transitionIDValueLabel.show()
        mainTable.attach(transitionIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        transitionNameLabel = gtk.Label("Name : ")
        transitionNameLabel.show()
        transitionNameEntry = gtk.Entry()
        transitionNameEntry.show()
        mainTable.attach(transitionNameLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionNameEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        transitionTypeLabel = gtk.Label("Type : ")
        transitionTypeLabel.show()
        transitionTypeCombo = gtk.ComboBox()
        transitionTypeCombo.set_model(gtk.ListStore(str))
        transitionTypeComboCell = gtk.CellRendererText()
        transitionTypeCombo.pack_start(transitionTypeComboCell, True)
        transitionTypeCombo.add_attribute(transitionTypeComboCell, 'text', 0)
        possible_choices = ["SemiStochastic", "OpenChannel", "CloseChannel"]
        for i in range(len(possible_choices)):
            transitionTypeCombo.append_text(str(possible_choices[i]))
        transitionTypeCombo.show()
        mainTable.attach(transitionTypeLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionTypeCombo, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        transitionStartStateLabel = gtk.Label("Start State : ")
        transitionStartStateLabel.show()
        transitionStartStateCombo = gtk.ComboBox()
        transitionStartStateCombo.set_model(gtk.ListStore(str, str))
        transitionStartStateCell = gtk.CellRendererText()
        transitionStartStateCombo.pack_start(transitionStartStateCell, True)
        transitionStartStateCombo.add_attribute(transitionStartStateCell, 'text', 0)
        
        for state in self.states :
            transitionStartStateCombo.get_model().append([state.getName(), str(state.getID())])
        transitionStartStateCombo.show()
        mainTable.attach(transitionStartStateLabel, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionStartStateCombo, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        transitionStopStateLabel = gtk.Label("Stop State : ")
        transitionStopStateLabel.show()
        transitionStopStateCombo = gtk.ComboBox()
        transitionStopStateCombo.set_model(gtk.ListStore(str, str))
        transitionStopStateComboCell = gtk.CellRendererText()
        transitionStopStateCombo.pack_start(transitionStopStateComboCell, True)
        transitionStopStateCombo.add_attribute(transitionStopStateComboCell, 'text', 0)
        
        for state in self.states :
            transitionStopStateCombo.get_model().append([state.getName(), str(state.getID())])
        transitionStopStateCombo.show()
        mainTable.attach(transitionStopStateLabel, 0, 1, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionStopStateCombo, 1, 2, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result != gtk.RESPONSE_OK :
            return 
        
        # We retrieve the selected values
        transitionName = transitionNameEntry.get_text()
        transitionType = transitionTypeCombo.get_model()[transitionTypeCombo.get_active()][0]
        idStartState = transitionStartStateCombo.get_model()[transitionStartStateCombo.get_active()][1]
        idStopState = transitionStopStateCombo.get_model()[transitionStopStateCombo.get_active()][1]
        startState = None
        stopState = None
        for state in self.states :
            if str(state.getID()) == idStartState :
                startState = state
            if str(state.getID()) == idStopState :
                stopState = state
        
        if startState == None or stopState == None :
            self.log.warn("The states of the transition are not valid.")
            return
        
        dialog.destroy()
        createdTransition = None
        if transitionType == "SemiStochastic" :
            createdTransition = self.createSemiStochasticTransition(transitionID, transitionName, startState, stopState)
        elif transitionType == "OpenChannel" :
            createdTransition = self.createOpenChannelTransition(transitionID, transitionName, startState, stopState)
        elif transitionType == "CloseChannel" :
            createdTransition = self.createCloseChannelTransition(transitionID, transitionName, startState, stopState)
        else :
            self.log.warn("Impossible to create the requested transition since the type is unknown")
        
        
        if createdTransition != None :
            self.transitions.append(createdTransition)
            self.updateListTransitions()
            self.updateXDot()
            
        
    def createOpenChannelTransition(self, transitionID, transitionName, startState, stopState):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of an OpenChannel Transition')
        
        mainTable = gtk.Table(rows=2, columns=2, homogeneous=False)
        transitionConnectionTimeLabel = gtk.Label("Connection time (ms): ")
        transitionConnectionTimeLabel.show()
        transitionConnectionTimeEntry = gtk.Entry()
        transitionConnectionTimeEntry.show()
        mainTable.attach(transitionConnectionTimeLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionConnectionTimeEntry, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        transitionMaxAttemptsLabel = gtk.Label("Maximum number of connection attempts: ")
        transitionMaxAttemptsLabel.show()
        transitionMaxAttemptsEntry = gtk.Entry()
        transitionMaxAttemptsEntry.show()
        mainTable.attach(transitionMaxAttemptsLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionMaxAttemptsEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result != gtk.RESPONSE_OK :
            dialog.destroy()
            return None
        
        connectionTime = int(transitionConnectionTimeEntry.get_text())
        maxNumberOfAttempt = int(transitionMaxAttemptsEntry.get_text())
        transition = OpenChannelTransition(transitionID, transitionName, startState, stopState, connectionTime, maxNumberOfAttempt)
        startState.registerTransition(transition)
        dialog.destroy()
        return transition
    
    def createCloseChannelTransition(self, transitionID, transitionName, startState, stopState):    
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of an CloseChannel Transition')
        
        mainTable = gtk.Table(rows=1, columns=2, homogeneous=False)
        transitionDisconnectionTimeLabel = gtk.Label("Disconnection time (ms): ")
        transitionDisconnectionTimeLabel.show()
        transitionDisconnectionTimeEntry = gtk.Entry()
        transitionDisconnectionTimeEntry.show()
        mainTable.attach(transitionDisconnectionTimeLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(transitionDisconnectionTimeEntry, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result != gtk.RESPONSE_OK :
            dialog.destroy()
            return None
        
        disconnectionTime = int(transitionDisconnectionTimeEntry.get_text())
        transition = CloseChannelTransition(transitionID, transitionName, startState, stopState, disconnectionTime)
        startState.registerTransition(transition)
        dialog.destroy()
        return transition
    def createSemiStochasticTransition(self, transitionID, transitionName, startState, stopState):
        
        entries = self.netzob.getDictionary().getEntries()
        
        
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of a SemiStochastic Transition')
        
        mainTable = gtk.Table(rows=9, columns=2, homogeneous=False)
        
        inputSymbolTitle = gtk.Label("Define input symbol")
        inputSymbolTitle.show()
        mainTable.attach(inputSymbolTitle, 0, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        inputSymbolLabel = gtk.Label("Dictionary entry : ")
        inputSymbolLabel.show()
        
        inputSymbolCombo = gtk.ComboBox()
        inputSymbolCombo.set_model(gtk.ListStore(str, str)) #entry name, entry id
        inputSymbolComboCell = gtk.CellRendererText()
        inputSymbolCombo.pack_start(inputSymbolComboCell, True)
        inputSymbolCombo.add_attribute(inputSymbolComboCell, 'text', 0)
        
        for dicoEntry in entries :
            inputSymbolCombo.get_model().append([dicoEntry.getName(), str(dicoEntry.getID())])
        inputSymbolCombo.show()
        
        mainTable.attach(inputSymbolLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(inputSymbolCombo, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        
        outputSymbolTitle = gtk.Label("Define output symbols")
        outputSymbolTitle.show()
        mainTable.attach(outputSymbolTitle, 0, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        outputSymbolLabel = gtk.Label("Dictionary entry : ")
        outputSymbolLabel.show()
        
        outputSymbolCombo = gtk.ComboBox()
        outputSymbolCombo.set_model(gtk.ListStore(str, str)) #entry name, entry id
        outputSymbolComboCell = gtk.CellRendererText()
        outputSymbolCombo.pack_start(outputSymbolComboCell, True)
        outputSymbolCombo.add_attribute(outputSymbolComboCell, 'text', 0)
        
        for dicoEntry in entries :
            outputSymbolCombo.get_model().append([dicoEntry.getName(), str(dicoEntry.getID())])
        outputSymbolCombo.show()
        
        mainTable.attach(outputSymbolLabel, 0, 1, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(outputSymbolCombo, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        outputTimeLabel = gtk.Label("Time : ")
        outputTimeLabel.show()
        outputTimeEntry = gtk.Entry()
        outputTimeEntry.show()
        mainTable.attach(outputTimeLabel, 0, 1, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(outputTimeEntry, 1, 2, 5, 6, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        outputProbabilityLabel = gtk.Label("Probability ([0;100]) : ")
        outputProbabilityLabel.show()
        outputProbabilityEntry = gtk.Entry()
        outputProbabilityEntry.show()
        mainTable.attach(outputProbabilityLabel, 0, 1, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(outputProbabilityEntry, 1, 2, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        removeOutputSymbolButton = gtk.Button("Remove")
#       removeOutputSymbolButton.connect("clicked", None)
        removeOutputSymbolButton.show()
        removeOutputSymbolButton.set_sensitive(False)
        
        
        outputSymbolsTreeStore = gtk.TreeStore(str, str, str, str) # id, name, time, proba
        
        addOutputSymbolButton = gtk.Button("Add")
        addOutputSymbolButton.connect("clicked", self.addSymbolToTheList, entries, outputSymbolsTreeStore, outputSymbolCombo, outputTimeEntry, outputProbabilityEntry)
        addOutputSymbolButton.show()
        addOutputSymbolButton.set_sensitive(True)
        
        mainTable.attach(removeOutputSymbolButton, 0, 1, 7, 8, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(addOutputSymbolButton, 1, 2, 7, 8, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        outputSymbolsScroll = gtk.ScrolledWindow()
        
        outputSymbolsTreeView = gtk.TreeView(outputSymbolsTreeStore)
        outputSymbolsTreeView.get_selection().set_mode(gtk.SELECTION_SINGLE)
        outputSymbolsTreeView.set_size_request(-1, 250)
#        outputSymbolsTreeView.connect("cursor-changed", self.actorDetails)
        outputSymbolsTreeViewCell = gtk.CellRendererText()
        # col : name of the symbol
        outputSymbolsTreeViewCol_name = gtk.TreeViewColumn('Symbol name')
        outputSymbolsTreeViewCol_name.pack_start(outputSymbolsTreeViewCell, True)
        outputSymbolsTreeViewCol_name.set_attributes(outputSymbolsTreeViewCell, text=1)
        outputSymbolsTreeView.append_column(outputSymbolsTreeViewCol_name)
        # col : time of the symbol
        outputSymbolsTreeViewCol_time = gtk.TreeViewColumn('time')
        outputSymbolsTreeViewCol_time.pack_start(outputSymbolsTreeViewCell, True)
        outputSymbolsTreeViewCol_time.set_attributes(outputSymbolsTreeViewCell, text=2)
        outputSymbolsTreeView.append_column(outputSymbolsTreeViewCol_time)
        # col : proba of the symbo2
        outputSymbolsTreeViewCol_proba = gtk.TreeViewColumn('proba')
        outputSymbolsTreeViewCol_proba.pack_start(outputSymbolsTreeViewCell, True)
        outputSymbolsTreeViewCol_proba.set_attributes(outputSymbolsTreeViewCell, text=3)
        outputSymbolsTreeView.append_column(outputSymbolsTreeViewCol_proba)
        outputSymbolsTreeView.show()
        outputSymbolsScroll.add(outputSymbolsTreeView)
        outputSymbolsScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        outputSymbolsScroll.show()
        
        mainTable.attach(outputSymbolsScroll, 0, 2, 8, 9, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result != gtk.RESPONSE_OK :
            dialog.destroy()
            return None


        # retrieve the input symbols
        inputEntryID = inputSymbolCombo.get_model()[inputSymbolCombo.get_active()][1]
        inputEntry = None
        for entry in entries :
            if str(entry.getID()) == inputEntryID :
                inputEntry = entry
        
        if inputEntry == None :
            self.log.warn("Impossible to retrieve the selected input dictionary entry")
            dialog.destroy()
            return
        inputSymbol = DictionarySymbol(inputEntry)
        
        # retrieve the output symbols 
        outputSymbols = [] # [ [symbol, proba, time], ...]
        for outputData in outputSymbolsTreeStore :
            outputSymbolID = outputData[0]
            outputSymbolName = outputData[1]
            outputSymbolTime = outputData[2]
            outputSymbolProba = outputData[3]
            
            outputEntry = None
            for entry in entries :
                if str(entry.getID()) == outputSymbolID :
                    outputEntry = entry
                    
            if outputEntry == None :
                self.log.warn("Impossible to retrieve the selected output dictionary entry")
                dialog.destroy()
                return
            outputSymbols.append([DictionarySymbol(outputEntry), int(outputSymbolProba), int(outputSymbolTime)])
            
        # Now we create the transition
        transition = SemiStochasticTransition(transitionID, transitionName, startState, stopState, inputSymbol)
        for data in outputSymbols :
            transition.addOutputSymbol(data[0], data[1], data[2])
        startState.registerTransition(transition)
        dialog.destroy()
        return transition
        




    def addSymbolToTheList(self, widget, entries, outputSymbolsTreeStore, outputSymbolCombo, outputTimeEntry, outputProbabilityEntry):
        entryID = outputSymbolCombo.get_model()[outputSymbolCombo.get_active()][1]
        entryTime = outputTimeEntry.get_text()
        entryProba = outputProbabilityEntry.get_text()
        selectedEntry = None
        for entry in entries :
            if str(entry.getID()) == entryID :
                selectedEntry = entry
        if selectedEntry == None :
            self.log.warn("Impossible to retrieve the selected dictionary entry")
            return
        
        outputSymbolsTreeStore.append(None, [selectedEntry.getID(), selectedEntry.getName(), entryTime, entryProba])
        
        
        
        
        


    def createState(self, widget):
        self.log.debug("Opening the dialog for the creation of a new state")
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, None)
        dialog.set_markup('Definition of the new state')
        
        # Create the ID of the new state
        stateID = str(uuid.uuid4())
        
        mainTable = gtk.Table(rows=3, columns=2, homogeneous=False)
        stateIDLabel = gtk.Label("ID :")
        stateIDLabel.show()
        stateIDValueLabel = gtk.Label(stateID)
        stateIDValueLabel.show()
        mainTable.attach(stateIDLabel, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(stateIDValueLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        stateNameLabel = gtk.Label("Name : ")
        stateNameLabel.show()
        stateNameEntry = gtk.Entry()
        stateNameEntry.show()
        mainTable.attach(stateNameLabel, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(stateNameEntry, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        isItInitialStateLabel = gtk.Label("Is it the initial state : ")
        isItInitialStateLabel.show()
        isItInitialStateButton = gtk.CheckButton("")
        if self.initialState == None:
            isItInitialStateButton.set_active(True)
        else:
            isItInitialStateButton.set_active(False)
        isItInitialStateButton.show()

        mainTable.attach(isItInitialStateLabel, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        mainTable.attach(isItInitialStateButton, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        dialog.vbox.pack_end(mainTable, True, True, 0)
        dialog.show_all()
        result = dialog.run()
        
        if result == gtk.RESPONSE_OK :
            stateName = stateNameEntry.get_text()
            
            if stateName != None and len(stateName) > 0:
                # Create of the new state
                self.log.info("Create a state " + stateName + " (" + stateID + ")")
                state = NormalState(stateID, stateName)
                self.states.append(state)        
                
                if isItInitialStateButton.get_active() :
                    self.initialState = state
            
            dialog.destroy()
            
            # update the list of states
            self.updateListStates()
            
            # update the xdot
            self.updateXDot()
            
        
    def updateListStates(self):
        self.treestore_listStates.clear()
        for state in self.states :
            self.treestore_listStates.append(None, [str(state.getID()), state.getName(), state.getType()])
            
    def updateListTransitions(self):
        self.treestore_listTransitions.clear()
        for transition in self.transitions :   
            startState = transition.getInputState().getName()
            endState = transition.getOutputState().getName()
            self.treestore_listTransitions.append(None, [str(transition.getID()), transition.getName(), startState, endState, transition.getType()])
        
        
    def updateXDot(self):
        if self.initialState != None :
            # Build the current grammar 
            self.grammar = MMSTD(self.initialState, self.netzob.getDictionary())
            self.xdotWidget.set_dotcode(self.grammar.getDotCode())
            
    def updateInterface(self):
        if self.netzob.getCurrentProject() == None :
            self.createStateButton.set_sensitive(False)
            self.createTransitionButton.set_sensitive(False)
        
        else :
            self.createStateButton.set_sensitive(True)
            self.createTransitionButton.set_sensitive(True)
