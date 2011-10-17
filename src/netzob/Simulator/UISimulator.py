#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import pygtk
pygtk.require('2.0')
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
from . import XDotWidget
from ..Common.MMSTD.Tools.Parsers.MMSTDParser import MMSTDXmlParser

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UISimulator :
#|     GUI for the simulation of actors
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
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
        pass
    
    def save(self, file):
        self.log = logging.getLogger('netzob.Simuator.UISimulator.py')
        self.log.warn("The simulation process cannot be saved for the moment")
        
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main class
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Simulator.UISimulator.py')
        self.netzob = netzob
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = gtk.Table(rows=5, columns=2, homogeneous=False)
        self.panel.show()
        
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Table hosting the form for a new actor
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.tableFormNewActor = gtk.Table(rows=3, columns=4, homogeneous=True)
        
        # Actor's name
        label_actorName = gtk.Label("Actor's name : ")
        label_actorName.show()
        self.entry_actorName = gtk.Entry()
#        self.entry_actorName.set_width_chars(50)
        self.entry_actorName.set_text("")
        self.entry_actorName.show()
        self.tableFormNewActor.attach(label_actorName, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_actorName, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Available grammars
        label_grammar = gtk.Label("Grammar : ")
        label_grammar.show()
        self.combo_grammar = gtk.combo_box_entry_new_text()
        self.combo_grammar.set_model(gtk.ListStore(str))
        possible_grammars = ["demo1.xml", "demo2.xml"]
        for i in range(len(possible_grammars)):
            self.combo_grammar.append_text(possible_grammars[i])
        self.combo_grammar.show()
        self.tableFormNewActor.attach(label_grammar, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.combo_grammar, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Type of actor
        label_typeOfActor = gtk.Label("Type : ")
        label_typeOfActor.show()
        self.combo_typeOfActor = gtk.combo_box_entry_new_text()
        self.combo_typeOfActor.set_model(gtk.ListStore(str))
        self.combo_typeOfActor.append_text("CLIENT")
        self.combo_typeOfActor.append_text("SERVER")
        self.combo_typeOfActor.show()
        self.tableFormNewActor.attach(label_typeOfActor, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.combo_typeOfActor, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # IP
        label_IP = gtk.Label("IP : ")
        label_IP.show()
        self.entry_IP = gtk.Entry()
#        self.entry_IP.set_width_chars(50)
        self.entry_IP.set_text("")
        self.entry_IP.show()
        self.tableFormNewActor.attach(label_IP, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_IP, 3, 4, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # PORT
        label_Port = gtk.Label("Port : ")
        label_Port.show()
        self.entry_Port = gtk.Entry()
#        self.entry_Port.set_width_chars(50)
        self.entry_Port.set_text("")
        self.entry_Port.show()
        self.tableFormNewActor.attach(label_Port, 2, 3, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.tableFormNewActor.attach(self.entry_Port, 3, 4, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # Add actor button
        self.button_addActor = gtk.Button(gtk.STOCK_OK)
        self.button_addActor.set_label("Add actor")
#        self.button_addActor.connect("clicked", self.startAnalysis_cb)
        self.button_addActor.show()
        self.tableFormNewActor.attach(self.button_addActor, 3, 4, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
                
        self.tableFormNewActor.show()
        self.panel.attach(self.tableFormNewActor, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Panel hosting the list of curent actors
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_listActiveActors = gtk.ScrolledWindow()
        self.treestore_listActiveActors = gtk.TreeStore(str, str) # actor's name, typ
        
        self.treestore_listActiveActors.append(None, ["actor1", "Server"])
        self.treestore_listActiveActors.append(None, ["actor2", "Client"])
        self.treestore_listActiveActors.append(None, ["actor3", "Client"])
        self.treestore_listActiveActors.append(None, ["actor4", "Client"])
        self.treestore_listActiveActors.append(None, ["actor5", "Client"])
        
        treeview_listActiveActors = gtk.TreeView(self.treestore_listActiveActors)
        treeview_listActiveActors.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview_listActiveActors.set_size_request(500, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = gtk.CellRendererText()
        # main col
        column_listActiveActors_name = gtk.TreeViewColumn('Active actors')
        column_listActiveActors_name.pack_start(cell, True)
        column_listActiveActors_name.set_attributes(cell, text=0)
        treeview_listActiveActors.append_column(column_listActiveActors_name)
        treeview_listActiveActors.show()
        scroll_listActiveActors.add(treeview_listActiveActors)
        scroll_listActiveActors.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_listActiveActors.show()
        self.panel.attach(scroll_listActiveActors, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Inputs
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_inputs = gtk.ScrolledWindow()
        self.treestore_inputs = gtk.TreeStore(str, str) # date, input message
        
        self.treestore_inputs.append(None, ["12:45:01", "message 1"])
        self.treestore_inputs.append(None, ["12:45:11", "message 2"])
        self.treestore_inputs.append(None, ["12:45:21", "message 3"])
        self.treestore_inputs.append(None, ["12:45:23", "message 4"])
        self.treestore_inputs.append(None, ["12:45:23", "message 5"])
        
        treeview_inputs = gtk.TreeView(self.treestore_inputs)
        treeview_inputs.get_selection().set_mode(gtk.SELECTION_NONE)
        treeview_inputs.set_size_request(500, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = gtk.CellRendererText()
        # col date
        column_inputs_date = gtk.TreeViewColumn('Date')
        column_inputs_date.pack_start(cell, True)
        column_inputs_date.set_attributes(cell, text=0)
        # col message
        column_inputs_message = gtk.TreeViewColumn('Received message')
        column_inputs_message.pack_start(cell, True)
        column_inputs_message.set_attributes(cell, text=1)
        treeview_inputs.append_column(column_inputs_date)
        treeview_inputs.append_column(column_inputs_message)
        treeview_inputs.show()
        scroll_inputs.add(treeview_inputs)
        scroll_inputs.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_inputs.show()
        self.panel.attach(scroll_inputs, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
               
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Outputs
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_outputs = gtk.ScrolledWindow()
        self.treestore_outputs = gtk.TreeStore(str, str) # date, output message
        
        self.treestore_outputs.append(None, ["12:45:01", "message 1"])
        self.treestore_outputs.append(None, ["12:45:11", "message 2"])
        self.treestore_outputs.append(None, ["12:45:21", "message 3"])
        self.treestore_outputs.append(None, ["12:45:23", "message 4"])
        self.treestore_outputs.append(None, ["12:45:23", "message 5"])
        
        treeview_outputs = gtk.TreeView(self.treestore_outputs)
        treeview_outputs.get_selection().set_mode(gtk.SELECTION_NONE)
        treeview_outputs.set_size_request(500, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = gtk.CellRendererText()
        # col date
        column_outputs_date = gtk.TreeViewColumn('Date')
        column_outputs_date.pack_start(cell, True)
        column_outputs_date.set_attributes(cell, text=0)
        # col message
        column_outputs_message = gtk.TreeViewColumn('Emitted message')
        column_outputs_message.pack_start(cell, True)
        column_outputs_message.set_attributes(cell, text=1)
        treeview_outputs.append_column(column_outputs_date)
        treeview_outputs.append_column(column_outputs_message)
        treeview_outputs.show()
        scroll_outputs.add(treeview_outputs)
        scroll_outputs.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_outputs.show()
        self.panel.attach(scroll_outputs, 0, 1, 2, 3, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Memory
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll_memory = gtk.ScrolledWindow()
        self.treestore_memory = gtk.TreeStore(str, str, str) # name, type, value
        
        self.treestore_memory.append(None, ["var1", "IP", "192.168.0.10"])
        self.treestore_memory.append(None, ["var2", "WORD", "PSEUDO"])
        self.treestore_memory.append(None, ["var3", "IP", "192.178.12.12"])
        
        treeview_memory = gtk.TreeView(self.treestore_memory)
        treeview_memory.get_selection().set_mode(gtk.SELECTION_NONE)
        treeview_memory.set_size_request(500, -1)
#        treeview_listActiveActors.connect("cursor-changed", self.packet_details)
        cell = gtk.CellRendererText()
        # col name
        column_memory_name = gtk.TreeViewColumn('Variable')
        column_memory_name.pack_start(cell, True)
        column_memory_name.set_attributes(cell, text=0)
        # col type
        column_memory_type = gtk.TreeViewColumn('Type')
        column_memory_type.pack_start(cell, True)
        column_memory_type.set_attributes(cell, text=1)
        # col Value
        column_memory_value = gtk.TreeViewColumn('Value')
        column_memory_value.pack_start(cell, True)
        column_memory_value.set_attributes(cell, text=2)
        
        treeview_memory.append_column(column_memory_name)
        treeview_memory.append_column(column_memory_type)
        treeview_memory.append_column(column_memory_value)
        treeview_memory.show()
        scroll_memory.add(treeview_memory)
        scroll_memory.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_memory.show()
        self.panel.attach(scroll_memory, 0, 1, 3, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
                
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Panel for the Model
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        xdotWidget = XDotWidget.XDotWidget()
        
        xmlFile = "resources/automaton/example1.xml"     
        tree = ElementTree.ElementTree()
        tree.parse(xmlFile)
           
        automata = MMSTDXmlParser.MMSTDXmlParser.loadFromXML(tree.getroot())
        
        xdotWidget.drawAutomata(automata)
        xdotWidget.show_all()
        xdotWidget.set_size_request(500, 500)
        
        self.panel.attach(xdotWidget, 1, 2, 1, 4, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
