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
import gobject
import logging
import threading
import os
import time
import random
import nfqueue
import socket
from dpkt import ip, tcp, udp

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ..Common import ConfigurationParser
from TreeViews import TreeGroupGenerator
from TreeViews import TreeTypeStructureGenerator

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+ 
#| Network :
#|     This class offers the capability to fuzz network flows in live 
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Network:
    def new(self):
        pass

    def update(self):
        self.treeGroupGenerator.update()
        self.treeTypeStructureGenerator.update()

    def clear(self):
        pass

    def kill(self):
#        os.popen("sudo iptables -D OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -D OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        if self.aFuzzThread != None and self.aFuzzThread.isAlive():
            self.aFuzzThread._Thread__stop()
    
    def save(self):
        pass
   
    #+---------------------------------------------- 
    #| Constructor :
    #| @param netzob: the netzob main object
    #+----------------------------------------------   
    def __init__(self, netzob):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Fuzzing.Network.py')
        self.netzob = netzob
        self.selectedGroup = None
        self.aFuzzThread = None
        self.packets = [] 
        self.panel = gtk.VPaned()
        self.panel.show()

        #+---------------------------------------------- 
        #| LEFT PART OF THE GUI : TREEVIEW
        #+----------------------------------------------           
        topPanel = gtk.HPaned()
        topPanel.show()
        self.panel.add(topPanel)
        vb_left_panel = gtk.VBox(False, spacing=0)
        topPanel.add(vb_left_panel)
        vb_left_panel.set_size_request(-1, -1)
        vb_left_panel.show()

        # Initialize the treeview generator for the groups
        self.treeGroupGenerator = TreeGroupGenerator.TreeGroupGenerator(self.netzob)
        self.treeGroupGenerator.initialization()
        vb_left_panel.pack_start(self.treeGroupGenerator.getScrollLib(), True, True, 0)
        self.treeGroupGenerator.getTreeview().connect("cursor-changed", self.groupSelected) 

        #+---------------------------------------------- 
        #| RIGHT PART OF THE GUI : TYPE STRUCTURE OUTPUT
        #+----------------------------------------------
        vb_right_panel = gtk.VBox(False, spacing=0)
        vb_right_panel.show()
        # Initialize the treeview for the type structure
        self.treeTypeStructureGenerator = TreeTypeStructureGenerator.TreeTypeStructureGenerator()
        self.treeTypeStructureGenerator.initialization()
        self.treeTypeStructureGenerator.getTreeview().connect('button-press-event', self.button_press_on_field)
        vb_right_panel.add(self.treeTypeStructureGenerator.getScrollLib())
        topPanel.add(vb_right_panel)

        #+---------------------------------------------- 
        #| BOTTOM PART OF THE GUI : PACKET CAPTURING
        #+----------------------------------------------
        # Network Capturing Panel
        sniffPanel = gtk.Table(rows=6, columns=4, homogeneous=False)
        self.panel.add(sniffPanel)
        sniffPanel.show()

        # Filter
        label = gtk.Label("Filter")
        label.show()
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        sniffPanel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        sniffPanel.attach(entry_filter, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        but = gtk.Button(label="Fuzz traffic")
        but.show()
        but.connect("clicked", self.launchFuzz_cb, entry_filter)
        sniffPanel.attach(but, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = gtk.ScrolledWindow()
        self.treestore = gtk.TreeStore(int, str, str, str, str, str, int) # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
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
        sniffPanel.attach(scroll, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sniffPanel.attach(scroll, 2, 4, 0, 6, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

    #+---------------------------------------------- 
    #| update:
    #|   Update the Treestore
    #+---------------------------------------------- 
    def groupSelected(self, treeview):
        (model, iter) = treeview.get_selection().get_selected()
        if(iter):
            if(model.iter_is_valid(iter)):
                # Retrieve the selected group
                idGroup = model.get_value(iter, 0)
                self.selectedGroup = idGroup
                group = None
                for tmp_group in self.netzob.groups.getGroups() :
                    if str(tmp_group.getID()) == idGroup :
                        group = tmp_group

                # Retrieve a random message in order to show a type structure
                message = group.getMessages()[-1]
                self.treeTypeStructureGenerator.setGroup(group)
                self.treeTypeStructureGenerator.setMessage(message)
                self.treeTypeStructureGenerator.update()

    #+---------------------------------------------- 
    #| button_press_on_field :
    #|   Create a menu to display available operations
    #|   on the treeview groups
    #+----------------------------------------------
    def button_press_on_field(self, button, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:        
            # Retrieves the group on which the user has clicked on
            x = int(event.x)
            y = int(event.y)
            (path, treeviewColumn, x, y) = self.treeTypeStructureGenerator.getTreeview().get_path_at_pos(x, y)
            aIter = self.treeTypeStructureGenerator.getTreeview().get_model().get_iter(path)
            field = self.treeTypeStructureGenerator.getTreeview().get_model().get_value(aIter, 0)
            menu = gtk.Menu()
            item = gtk.MenuItem("Fuzz field")
            item.connect("activate", self.fuzz_field_cb, field)
            item.show()
            menu.append(item)
            menu.popup(None, None, None, event.button, event.time)

    def fuzz_field_cb(self, widget, field):
        print "Fuzz field : " + str(field)

    #+---------------------------------------------- 
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_details(self, treeview):
        (model, paths) = treeview.get_selection().get_selected_rows()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                self.textview.get_buffer().set_text(self.packets[packetID].show())

    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launchFuzz_cb(self, button, aFilter):
        button.set_sensitive(False)
        self.packets = []
        self.treestore.clear()
        self.textview.get_buffer().set_text("")

        self.aFuzzThread = threading.Thread(None, self.fuzzThread, None, (button, aFilter), {})
        self.aFuzzThread.start()

    #+---------------------------------------------- 
    #| Thread for fuzzing
    #+----------------------------------------------
    def fuzzThread(self, button, aFilter):
        self.log.info("Launching fuzzing process with : filter=\"" + aFilter.get_text() + "\"")

        ## Set Netfilter NFQUEUE
#        os.popen("sudo iptables -I OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -I OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        q = nfqueue.queue()
        q.open()
        try:
            q.unbind(socket.AF_INET)
        except:
            pass
        q.bind(socket.AF_INET)
        q.set_callback(self.nfqueue_cb)
        q.create_queue(0)
        q.set_queue_maxlen(5000)   
        try:
            

            ## TODO : do it in a dedicated process

            q.try_run()
        except:
            pass
        q.unbind(socket.AF_INET)
        q.close()

#        os.popen("sudo iptables -D OUTPUT -p tcp --dport 80  -j NFQUEUE 2>&1 > /dev/null")
#        os.popen("sudo iptables -D OUTPUT -p tcp --sport 80  -j NFQUEUE 2>&1 > /dev/null")
        gobject.idle_add( button.set_sensitive, True )

    #+---------------------------------------------- 
    #| Called when we reiceve a corresponding packet to fuzz
    #+----------------------------------------------
    def nfqueue_cb(self, dummy, payload):
        return payload.set_verdict(nfqueue.NF_ACCEPT)
    """
        data = payload.get_data()
        ip_pkt = ip.IP(data)
        if ip_pkt.p == ip.IP_PROTO_TCP:
            proto_pkt = tcp.TCP(str(ip_pkt.data))
            gobject.idle_add(self.treestore.append,
                             None,
                             [len(self.packets),
                              "TCP",
                              str(ip_pkt.src),
                              str(ip_pkt.dst),
                              str(proto_pkt.sport),
                              str(proto_pkt.dport),
                              int(time.time())]
                             )
        elif ip_pkt.p == ip.IP_PROTO_UDP:
            proto_pkt = udp.UDP(str(ip_pkt.data))
            gobject.idle_add(self.treestore.append,
                             None,
                             [len(self.packets),
                              "UDP",
                              str(ip_pkt.src),
                              str(ip_pkt.dst),
                              str(proto_pkt.sport),
                              str(proto_pkt.dport),
                              int(time.time())]
                             )
        self.packets.append(repr( ip_pkt ))
        new_ip_pkt = ip_pkt
        new_ip_pkt.data = self.fuzzPacket( ip_pkt.data )
        return payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(new_ip_pkt), len(new_ip_pkt))
    """
    #+---------------------------------------------- 
    #| Main function to fuzz packets
    #+----------------------------------------------
    def fuzzPacket(self, packet):
        print repr(packet)
        return packet

    """
        res = ""
        for i in range(len(strIN)):
            if i == offset:
                res += value
            else:
                res += strIN[i]
        return res
    """
    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
