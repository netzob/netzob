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
import scapy.all

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
class UIcapturing:
    
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
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.UIseqMessage.py')
        self.zob = zob
        self.packets = []
        self.panel = gtk.HPaned()
        self.panel.show()

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing types
        #+----------------------------------------------
        notebook = gtk.Notebook()
        notebook.show()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.connect("switch-page", self.notebookFocus)
        self.panel.add(notebook)

        #+----------------------------------------------
        #| LEFT PART OF THE GUI : Capturing panels
        #+----------------------------------------------
        # Network Capturing Panel
        netPanel = gtk.Table(rows=5, columns=4, homogeneous=False)
        netPanel.show()
        notebook.append_page(netPanel, gtk.Label("Network Capturing"))

        # IPC Capturing Panel
        ipcPanel = gtk.HPaned()
        ipcPanel.show()
        notebook.append_page(ipcPanel, gtk.Label("IPC Capturing"))

        #+----------------------------------------------
        #| Network Capturing sub-panel
        #+----------------------------------------------
        # Scapy filter
        label = gtk.Label("Scapy filter")
        label.show()
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        netPanel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        netPanel.attach(entry_filter, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Count capturing limit
        label = gtk.Label("Count limit")
        label.show()
        entry_count = gtk.Entry()
        entry_count.show()
        entry_count.set_text("10")
        netPanel.attach(label, 0, 1, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        netPanel.attach(entry_count, 1, 2, 1, 2, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Time capturing limit
        label = gtk.Label("Timeout (s)")
        label.show()
        entry_time = gtk.Entry()
        entry_time.show()
        entry_time.set_text("10")
        netPanel.attach(label, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        netPanel.attach(entry_time, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        
        # Sniff launching button
        but = gtk.Button(label="Sniff traffic")
        but.show()
        but.connect("clicked", self.launch_sniff, entry_filter, entry_count, entry_time)
        netPanel.attach(but, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.treestore = gtk.TreeStore(int, str, str, str, str, str)
        treeview = gtk.TreeView(self.treestore)
        treeview.connect("cursor-changed", self.packet_selected)
        cell = gtk.CellRendererText()
        # Col proto
        column = gtk.TreeViewColumn('Proto')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        treeview.append_column(column)
        # Col IP.src
        column = gtk.TreeViewColumn('IP source')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=1)
        treeview.append_column(column)
        # Col IP.dst
        column = gtk.TreeViewColumn('IP dest')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=2)
        treeview.append_column(column)
        # Col {TCP,UDP}.sport
        column = gtk.TreeViewColumn('sport')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=3)
        treeview.append_column(column)
        # Col {TCP,UDP}.dport
        column = gtk.TreeViewColumn('dport')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=4)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        netPanel.attach(scroll, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        netPanel.attach(scroll, 2, 4, 0, 5, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND, xpadding=5, ypadding=5)

    #+---------------------------------------------- 
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_selected(self, treeview):
        (modele, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(modele.iter_is_valid(iter)):
                packetID = modele.get_value(iter, 0)
                self.textview.get_buffer().set_text( self.packets[packetID].show() )


                #TODO : use label_lvl="": to take a subpart of a packet


    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, filter, count, time):
        button.set_sensitive(False)
        self.packets = []
        scapy.all.send(scapy.all.UDP(), verbose=False)
        try: # Just see if scapy is correctly working
            scapy.all.send(scapy.all.UDP(), verbose=False)
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
        scapy.all.sniff(prn=self.callback_scapy, filter=filter.get_text(), store=0, count=int(count.get_text()), timeout=int(time.get_text()))
        button.set_sensitive(True)

    #+---------------------------------------------- 
    #| Called when scapy reiceve a message
    #+----------------------------------------------
    def callback_scapy(self, pkt):
        if scapy.all.TCP in pkt:
            self.packets.append( pkt )
            self.treestore.append(None, [len(self.packets) + 1, "TCP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%TCP.sport%"), pkt.sprintf("%TCP.dport%")])
        elif scapy.all.UDP in pkt:
            self.packets.append( pkt )
            self.treestore.append(None, [len(self.packets) + 1, "UDP", pkt.sprintf("%IP.src%"), pkt.sprintf("%IP.dst%"), pkt.sprintf("%UDP.sport%"), pkt.sprintf("%UDP.dport%")])
#        print pkt.sprintf("%TCP.payload%")

    #+---------------------------------------------- 
    #| Called when user select a notebook
    #+----------------------------------------------
    def notebookFocus(self, notebook, page, pagenum):
        nameTab = notebook.get_tab_label_text(notebook.get_nth_page(pagenum))
        
