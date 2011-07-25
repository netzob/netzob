#!/usr/bin/python
# coding: utf8

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
import threading

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
class IPC:
    
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
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.UIseqMessage.py')
        self.packets = []

        # IPC Capturing Panel
        self.panel = gtk.Table(rows=6, columns=4, homogeneous=False)
        self.panel.show()

        # Scapy filter
        label = gtk.Label("Scapy filter")
        label.show()
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        self.panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_filter, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Count capturing limit
        label = gtk.Label("Count limit")
        label.show()
        entry_count = gtk.Entry()
        entry_count.show()
        entry_count.set_text("10")
        self.panel.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_count, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Time capturing limit
        label = gtk.Label("Timeout (s)")
        label.show()
        entry_time = gtk.Entry()
        entry_time.show()
        entry_time.set_text("10")
        self.panel.attach(label, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_time, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        
        # Sniff launching button
        but = gtk.Button(label="Sniff traffic")
        but.show()
        but.connect("clicked", self.launch_sniff, entry_filter, entry_count, entry_time)
        self.panel.attach(but, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.treestore = gtk.TreeStore(int, str, str, str, str, str)
        treeview = gtk.TreeView(self.treestore)
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
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
        self.panel.attach(scroll, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        but = gtk.Button(label="Select packets for analysis")
        but.show()
        but.connect("clicked", self.select_packets, treeview)
        self.panel.attach(but, 1, 2, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 6, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)

    #+---------------------------------------------- 
    #| Called when user select a list of packet
    #+----------------------------------------------
    def select_packets(self, button, treeview):
        print treeview.get_selection().count_selected_rows()

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
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, filter, count, time):
        button.set_sensitive(False)
        self.packets = []
        try: # Just see if scapy is correctly working
            scapyy.send(scapyy.UDP(), verbose=False)
        except:
            self.log.error("Scapy does not have the capability to sniff packets on your system")
            self.log.error("If you want capturing capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/bin/python2.6\"")
            self.log.error("And if you want filtering capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/sbin/tcpdump\"")
            return

        aScapyThread = threading.Thread(None, self.scapyThread, None, (button, filter, count, time), {})
        aScapyThread.start()

    #+---------------------------------------------- 
    #| Thread for scapy work
    #+----------------------------------------------
    def scapyThread(self, button, filter, count, time):
        self.log.info("Launching sniff process with : count="+count.get_text()+", timeout="+time.get_text()+", filter=\""+filter.get_text()+"\"")
        scapyy.sniff(prn=self.callback_scapy, filter=filter.get_text(), store=0, count=int(count.get_text()), timeout=int(time.get_text()))
        button.set_sensitive(True)

    #+---------------------------------------------- 
    #| Called when scapy reiceve a message
    #+----------------------------------------------
    def callback_scapy(self, pkt):
        if scapyy.TCP in pkt:
            self.treestore.append(None, [len(self.packets), "TCP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%TCP.sport%"), pkt.sprintf("%TCP.dport%")])
            self.packets.append( pkt )
        elif scapyy.UDP in pkt:
            self.treestore.append(None, [len(self.packets), "UDP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%UDP.sport%"), pkt.sprintf("%UDP.dport%")])
            self.packets.append( pkt )

    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
