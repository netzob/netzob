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
import pango
import gobject
import re
import pygtk
pygtk.require('2.0')
import logging
import os
import time
import random

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser
#from scapy.all import send, UDP, conf, packet
import scapyy.all as scapyy

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| UIcapturing :
#|     GUI for capturing messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Pcap:
    
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
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param groups: list of all groups 
    #+----------------------------------------------   
    def __init__(self, zob):        
        self.zob = zob

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.pcap.py')
        self.packets = []

        # Network Capturing Panel
        self.panel = gtk.Table(rows=5, columns=4, homogeneous=False)
        self.panel.show()

        # Scapy filter
        but = gtk.Button("Import PCAP")
        but.show()
        label_file = gtk.Label("...")
        label_file.show()
        but.connect("clicked", self.import_pcap, label_file)
        self.panel.attach(but, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(label_file, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Scapy filter
        label = gtk.Label("Scapy filter")
#        label.show() # TODO : implement the filter
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
#        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        self.panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_filter, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        but = gtk.Button(label="Import traffic")
        but.show()
        but.connect("clicked", self.launch_sniff, entry_filter, label_file)
        self.panel.attach(but, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.treestore = gtk.TreeStore(int, str, str, str, str, str, int) # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        treeview = gtk.TreeView(self.treestore)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        treeview.set_size_request(500, -1)
        treeview.connect("cursor-changed", self.packet_details)
        cell = gtk.CellRendererText()
        # Col proto
        column = gtk.TreeViewColumn('Proto')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col IP.src
        column = gtk.TreeViewColumn('IP source')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col IP.dst
        column = gtk.TreeViewColumn('IP dest')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        # Col {TCP,UDP}.sport
        column = gtk.TreeViewColumn('sport')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        treeview.append_column(column)
        # Col {TCP,UDP}.dport
        column = gtk.TreeViewColumn('dport')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=5)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        but = gtk.Button(label="Save selected packets")
        but.show()
        but.connect("clicked", self.save_packets, treeview)
        self.panel.attach(but, 1, 2, 4, 5, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 5, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)

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
        fd = open(existingTraceDir +"/"+ str(random.randint(100000, 9000000)) + ".xml"  , "w")
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
        fd = open(newTraceDir +"/"+ str(random.randint(100000, 9000000)) + ".xml"  , "w")
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
