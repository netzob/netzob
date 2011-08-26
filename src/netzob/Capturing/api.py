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

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import gtk
import pygtk
pygtk.require('2.0')
import logging
import os
import time
import random

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from ptrace.linux_proc import readProcesses, readProcessCmdline

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ..Common import ConfigurationParser
from ..Common import ExecutionContext

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Api :
#|     GUI for capturing messages from api hooking
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Api:
    
    #+-----------------------------------------------------------------------+ 
    #| Called when user select a new trace
    #+-----------------------------------------------------------------------+
    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass
    
    #+-----------------------------------------------------------------------+
    #| Constructor :
    #| @param groups: list of all groups 
    #+-----------------------------------------------------------------------+ 
    def __init__(self, zob):        
        self.zob = zob
        
        self.listOfProcess = []


        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.api.py')
        self.packets = []
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Main panel
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.panel = gtk.Table(rows=6, columns=5, homogeneous=False)
        self.panel.show()
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of processes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        but = gtk.Button("Update processes list")
        but.show()
        but.connect("clicked", self.updateProcessList_cb)
        self.processStore = gtk.combo_box_entry_new_text()
        self.processStore.show()
        self.processStore.set_size_request(500, -1)
        self.processStore.set_model(gtk.ListStore(str))
        self.panel.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(self.processStore, 1, 5, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.handlerID = self.processStore.connect("changed", self.processSelected_cb)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of DLL
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll = gtk.ScrolledWindow()
        self.dllTreeview = gtk.TreeView(gtk.TreeStore(str, str, str)) # file descriptor, type, name
        self.dllTreeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn('Name')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.dllTreeview.append_column(column)
        # Col type
        column = gtk.TreeViewColumn('Version')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.dllTreeview.append_column(column)
        # Col name
        column = gtk.TreeViewColumn('Size')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.dllTreeview.append_column(column)
        self.dllTreeview.show()
        scroll.add(self.dllTreeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 5, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of prototypes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.dllStore = gtk.combo_box_entry_new_text()
        self.dllStore.show()
        self.dllStore.set_size_request(300, -1)
        self.dllStore.set_model(gtk.ListStore(str))
        self.panel.attach(self.dllStore, 0, 3, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.butAddPrototype = gtk.Button("Create prototype")
        self.butAddPrototype.show()
        self.butAddPrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butAddPrototype, 3, 4, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.butRemovePrototype = gtk.Button("Delete prototype")
        self.butRemovePrototype.show()
        self.butRemovePrototype.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.butRemovePrototype, 4, 5, 4, 5, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of selected prototypes
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scroll2 = gtk.ScrolledWindow()
        self.selectedPrototypeTreeview = gtk.TreeView(gtk.TreeStore(str, str, str)) # file descriptor, type, name
        self.selectedPrototypeTreeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        cell = gtk.CellRendererText()
        # Col file descriptor
        column = gtk.TreeViewColumn('Name')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        self.selectedPrototypeTreeview.append_column(column)
        # Col type
        column = gtk.TreeViewColumn('Version')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        self.selectedPrototypeTreeview.append_column(column)
        # Col name
        column = gtk.TreeViewColumn('Size')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        self.selectedPrototypeTreeview.append_column(column)
        self.selectedPrototypeTreeview.show()
        scroll2.add(self.selectedPrototypeTreeview)
        scroll2.show()
        scroll2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll2, 0, 5, 5,6, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # List of buttons (start and stop capture)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.startCapture = gtk.Button("Start capture")
        self.startCapture.show()
        self.startCapture.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.startCapture, 3, 4, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        
        self.stopCapture = gtk.Button("Stop capture")
        self.stopCapture.show()
        self.stopCapture.connect("clicked", self.updateProcessList_cb)
        self.panel.attach(self.stopCapture, 4, 5, 6, 7, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

    
    #+---------------------------------------------- 
    #| Called when user wants to update the process list
    #+----------------------------------------------
    def updateProcessList_cb(self, button):
        self.processStore.handler_block(self.handlerID)
        # clear the list of process
        self.processStore.get_model().clear()
        
        # retrives the list of process
        self.listOfProcess = ExecutionContext.ExecutionContext.getCurrentProcesses()
        
        # add in the list all the process
        for process in self.listOfProcess :
            self.processStore.append_text(str(process.getPid()) + "\t" + process.getName())        
        self.processStore.handler_unblock(self.handlerID)

    #+---------------------------------------------- 
    #| Called when user select a process
    #+----------------------------------------------
    def processSelected_cb(self, widget):        
        # Updates the list of shared lib
        strProcessSelected = self.processStore.get_active_text()        
        pid = int(strProcessSelected.split()[0])
        selectedProcess = None
        
        for process in self.listOfProcess :
            if process.getPid() == pid :
                selectedProcess = process
                
        if selectedProcess != None :
            libs = selectedProcess.getSharedLibs()            
            
            self.dllTreeview.get_model().clear()
            for lib in libs :
                self.dllTreeview.get_model().append(None, [lib.getName(), "", ""])        
            
     
            
        else :
            print "not found"
        
        

    #+---------------------------------------------- 
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets(self, button, treeview):
        dialog = gtk.Dialog(title="Save selected packet as a new trace", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        # Add to an existing trace
        label = gtk.Label("Add to an existing trace")
        label.show()
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = gtk.Button("Save")
        but.connect("clicked", self.add_packets_to_existing_trace, entry, treeview.get_selection(), dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Create a new trace
        label = gtk.Label("Create a new trace")
        label.show()
        entry = gtk.Entry()
        entry.show()
        but = gtk.Button("Save")
        but.connect("clicked", self.create_new_trace, entry, treeview.get_selection(), dialog)
        but.show()
        table.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing trace
    #+----------------------------------------------
    def add_packets_to_existing_trace(self, button, entry, selection, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        existingTraceDir = tracesDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        res = "<datas>\n"
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                proto = model.get_value(iter, 1)
                timestamp = str(model.get_value(iter, 6))
                IPsrc = self.packets[packetID].sprintf("%IP.src%")
                IPdst = self.packets[packetID].sprintf("%IP.dst%")
                if scapyy.TCP in self.packets[packetID]:
                    sport = self.packets[packetID].sprintf("%TCP.sport%")
                    dport = self.packets[packetID].sprintf("%TCP.dport%")
                    rawPayload = self.packets[packetID].sprintf("%r,TCP.payload%")
                elif scapyy.UDP in self.packets[packetID]:
                    sport = self.packets[packetID].sprintf("%UDP.sport%")
                    dport = self.packets[packetID].sprintf("%UDP.dport%")
                    rawPayload = self.packets[packetID].sprintf("%r,UDP.payload%")
                if rawPayload == "":
                    continue
                res += "<data proto=\""+proto+"\" sourceIp=\""+IPsrc+"\" sourcePort=\""+sport+"\" targetIp=\""+IPdst+"\" targetPort=\""+dport+"\" timestamp=\""+timestamp+"\">\n"
                res += rawPayload.encode("hex") + "\n"
                res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(existingTraceDir +"/"+ str(random.randint(10000, 90000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()

    #+---------------------------------------------- 
    #| Creation of a new trace from a selection of packets
    #+----------------------------------------------
    def create_new_trace(self, button, entry, selection, dialog):
        tracesDirectoryPath = ConfigurationParser.ConfigurationParser().get("traces", "path")
        for tmpDir in os.listdir(tracesDirectoryPath):
            if tmpDir == '.svn':
                continue
            if entry.get_text() == tmpDir:
                dialogBis = gtk.Dialog(title="This trace already exists", flags=0, buttons=None)
                dialogBis.set_size_request(250, 50)
                dialogBis.show()
                return

        # Create the dest Dir
        newTraceDir = tracesDirectoryPath + "/" + entry.get_text()
        os.mkdir( newTraceDir )
        # Create the new XML structure
        res = "<datas>\n"
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                proto = model.get_value(iter, 1)
                timestamp = str(model.get_value(iter, 6))
                IPsrc = self.packets[packetID].sprintf("%IP.src%")
                IPdst = self.packets[packetID].sprintf("%IP.dst%")
                if scapyy.TCP in self.packets[packetID]:
                    sport = self.packets[packetID].sprintf("%TCP.sport%")
                    dport = self.packets[packetID].sprintf("%TCP.dport%")
                    rawPayload = self.packets[packetID].sprintf("%r,TCP.payload%")
                elif scapyy.UDP in self.packets[packetID]:
                    sport = self.packets[packetID].sprintf("%UDP.sport%")
                    dport = self.packets[packetID].sprintf("%UDP.dport%")
                    rawPayload = self.packets[packetID].sprintf("%r,UDP.payload%")
                if rawPayload == "":
                    continue
                res += "<data proto=\""+proto+"\" sourceIp=\""+IPsrc+"\" sourcePort=\""+sport+"\" targetIp=\""+IPdst+"\" targetPort=\""+dport+"\" timestamp=\""+timestamp+"\">\n"
                res += rawPayload.encode("hex") + "\n"
                res += "</data>\n"
        res += "</datas>\n"
        # Dump into a random XML file
        fd = open(newTraceDir +"/"+ str(random.randint(10000, 90000)) + ".xml"  , "w")
        fd.write(res)
        fd.close()
        dialog.destroy()
        self.zob.updateListOfAvailableTraces()

    #+---------------------------------------------- 
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_details(self, treeview):
        (model, paths) = treeview.get_selection().get_selected_rows()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                self.textview.get_buffer().set_text( self.packets[packetID].show() )

    #+---------------------------------------------- 
    #| Called when user import a pcap file
    #+----------------------------------------------
    def import_pcap(self, button, label):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            label.set_text(chooser.get_filename())
        chooser.destroy()

    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, aFilter, label_file):
        button.set_sensitive(False)
        self.packets = []
        self.treestore.clear()
        self.textview.get_buffer().set_text("")
        try: # Just see if scapy is correctly working
            scapyy.send(scapyy.UDP(), verbose=False)
        except:
            self.log.error("Scapy does not have the capability to sniff packets on your system")
            self.log.error("If you want capturing capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/bin/python2.6\"")
            self.log.error("And if you want filtering capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/sbin/tcpdump\"")
            return

        self.log.info("Launching sniff process with : filter=\""+aFilter.get_text()+"\"")
        scapyy.sniff(offline=label_file.get_text(), prn=self.callback_scapy, filter=aFilter.get_text(), store=0)
        button.set_sensitive(True)

    #+---------------------------------------------- 
    #| Called when scapy reiceve a message
    #+----------------------------------------------
    def callback_scapy(self, pkt):
        if scapyy.TCP in pkt and scapyy.Raw in pkt:
            self.treestore.append(None, [len(self.packets), "TCP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%TCP.sport%"), pkt.sprintf("%TCP.dport%"), int(time.time())])
            self.packets.append( pkt )
        elif scapyy.UDP in pkt and scapyy.Raw in pkt:
            self.treestore.append(None, [len(self.packets), "UDP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%UDP.sport%"), pkt.sprintf("%UDP.dport%"), int(time.time())])
            self.packets.append( pkt )

    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
