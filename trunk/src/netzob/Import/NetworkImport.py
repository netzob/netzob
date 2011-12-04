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
import threading
import os
import time
import random

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.Models.NetworkMessage import NetworkMessage
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory

#+---------------------------------------------------------------------------+ 
#| Network :
#|     This class offers the capability to capture traffic from live network 
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class NetworkImport:
    
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
    #| @param zob: a reference to the main netzob.py 
    #+-----------------------------------------------------------------------+  
    def __init__(self, zob):        
        self.zob = zob
        
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.Network.py')
        self.packets = []

        # Network Capturing Panel
        self.panel = gtk.Table(rows=7, columns=4, homogeneous=False)
        self.panel.show()

        # Network devices
        label = gtk.Label("Network devices")
        label.show()
        listNetworkDevice = gtk.combo_box_entry_new_text()
        listNetworkDevice.show()
        listNetworkDevice.set_size_request(300, -1)
        listNetworkDevice.set_model(gtk.ListStore(str))
        listNetworkDevice.get_model().clear()
        
        # list of interfaces
        try:
            interfaces = pcapy.findalldevs()
        except:
            self.log.warn("You don't have enough permissions to open any network interface on this system.")
            interfaces = []
        
        for interface in interfaces :
            listNetworkDevice.append_text(str(interface))        
        
        self.panel.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(listNetworkDevice, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # BPF filter
        label = gtk.Label("BPF filter")
        label.show()
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        self.panel.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_filter, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Count capturing limit
        label = gtk.Label("Count limit")
        label.show()
        entry_count = gtk.Entry()
        entry_count.show()
        entry_count.set_text("10")
        self.panel.attach(label, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_count, 1, 2, 2 , 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Time capturing limit
        label = gtk.Label("Timeout")
        label.show()
        entry_time = gtk.Entry()
        entry_time.show()
        entry_time.set_text("10")
        self.panel.attach(label, 0, 1, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_time, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        
        # Sniff launching button
        but = gtk.Button(label="Sniff traffic")
        but.show()
        but.connect("clicked", self.launch_sniff, listNetworkDevice, entry_filter, entry_count, entry_time)
        self.panel.attach(but, 1, 2, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

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
        self.panel.attach(scroll, 0, 2, 4, 5, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        but = gtk.Button(label="Save selected packets")
        but.show()
        but.connect("clicked", self.save_packets, treeview)
        self.panel.attach(but, 1, 2, 6, 7, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = gtk.ScrolledWindow()
        self.textview = gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 7, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

    #+---------------------------------------------- 
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets(self, button, treeview):
        dialog = gtk.Dialog(title="Save selected packet in a project", flags=0, buttons=None)
        dialog.show()
        table = gtk.Table(rows=2, columns=3, homogeneous=False)
        table.show()
        # Add to an existing project
        label = gtk.Label("Add to an existing project")
        label.show()
        entry = gtk.combo_box_entry_new_text()
        entry.show()
        entry.set_size_request(300, -1)
        entry.set_model(gtk.ListStore(str))
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        for tmpDir in os.listdir(projectsDirectoryPath):
            if tmpDir == '.svn':
                continue
            entry.append_text(tmpDir)
        but = gtk.Button("Save")
        but.connect("clicked", self.add_packets_to_existing_project, entry, treeview.get_selection(), dialog)
        but.show()
        table.attach(label, 0, 1, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(entry, 1, 2, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        table.attach(but, 2, 3, 0, 1, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        dialog.action_area.pack_start(table, True, True, 0)

    #+---------------------------------------------- 
    #| Add a selection of packets to an existing project
    #+----------------------------------------------
    def add_packets_to_existing_project(self, button, entry, selection, dialog):
        projectsDirectoryPath = ConfigurationParser().get("projects", "path")
        existingProjectDir = projectsDirectoryPath + "/" + entry.get_active_text()
        # Create the new XML structure
        messages = []
        
        
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                proto = model.get_value(iter, 1)
                timestamp = str(model.get_value(iter, 6))
                packetPayload = self.packets[packetID]
                
                eth_decoder = Decoders.EthDecoder()
                ip_decoder = Decoders.IPDecoder()
                udp_decoder = Decoders.UDPDecoder()
                tcp_decoder = Decoders.TCPDecoder()
        
                IPsrc = None
                IPdst = None
                Sport = None
                Dport = None
                Data = None
                
                
                ethernet = eth_decoder.decode(packetPayload)
                if ethernet.get_ether_type() == Packets.IP.ethertype:
                    ip = ip_decoder.decode(packetPayload[ethernet.get_header_size():])
                    IPsrc = ip.get_ip_src()
                    IPdst = ip.get_ip_dst()
                    
                    if ip.get_ip_p() == Packets.UDP.protocol: 
                        udp = udp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = udp.get_uh_sport()
                        Dport = udp.get_uh_dport()
                        Data = udp.get_data_as_string()

                                
                    if ip.get_ip_p() == Packets.TCP.protocol :
                        tcp = tcp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])  
                        Sport = tcp.get_th_sport()
                        Dport = tcp.get_th_dport()
                        Data = tcp.get_data_as_string()
                    
                    if Data != None and len(Data) > 0 :
                        # Compute the messages
                        message = NetworkMessage()
                        message.setProtocol(proto)
                        message.setIPSource(IPsrc)
                        message.setIPTarget(IPdst)
                        message.setL4SourcePort(Sport)
                        message.setL4TargetPort(Dport)
                        message.setTimestamp(timestamp)
                        message.setData(Data.encode("hex"))
                        messages.append(message)
        
        
        # Create the xml content of the file
        res = []
        res.append("<messages>")
        for message in messages :
            res.append(NetworkMessageFactory.saveInXML(message))
        res.append("</messages>")
        
        # Dump into a random XML file
        fd = open(existingProjectDir + "/" + str(random.randint(100000, 9000000)) + ".xml"  , "w")
        fd.write("\n".join(res))
        fd.close()
        dialog.destroy()        

    #+---------------------------------------------- 
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_details(self, treeview):
        (model, paths) = treeview.get_selection().get_selected_rows()
        decoder = Decoders.EthDecoder()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                payload = self.packets[packetID]
                self.textview.get_buffer().set_text("")
                self.textview.get_buffer().insert_with_tags_by_name(self.textview.get_buffer().get_start_iter(), str(decoder.decode(payload)), "normalTag")

    #+---------------------------------------------- 
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, dev, filter, count, time):
        button.set_sensitive(False)
        self.packets = []
        self.treestore.clear()
        self.textview.get_buffer().set_text("")
#        try: # Just see if scapy is correctly working
#            scapyy.send(scapyy.UDP(), verbose=False)
#        except:
#            self.log.error("Scapy does not have the capability to sniff packets on your system")
#            self.log.error("If you want capturing capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/bin/python2.6\"")
#            self.log.error("And if you want filtering capabilities, try the following command : \"sudo setcap cap_net_raw=ep /usr/sbin/tcpdump\"")
#            return

        aScapyThread = threading.Thread(None, self.sniffingThread, None, (button, dev, filter, count, time), {})
        aScapyThread.start()

    #+---------------------------------------------- 
    #| Thread for scapy work
    #+----------------------------------------------
    def sniffingThread(self, button, devstore, filter, count, time):
        modele = devstore.get_model()
        est_actif = devstore.get_active()
        dev = ""
        if est_actif < 0:
            dev = ""
        dev = modele[est_actif][0]
        
        self.log.info("Launching sniff process on dev " + dev + " with : count=" + count.get_text() + ", timeout=" + time.get_text() + ", filter=\"" + filter.get_text() + "\"")        
        sniffer = pcapy.open_live(dev, 1024, False, int(time.get_text()))

        try :
            sniffer.setfilter(filter.get_text())
        except :
            self.log.warn("The provided filter is not valid (it should respects the BPF format")
            button.set_sensitive(True)
            return
        
        
        sniffer.loop(int(count.get_text()), self.packetHandler)

        button.set_sensitive(True)

    def packetHandler(self, header, payload):
        # Definition of the protocol decoders (impacket)
        eth_decoder = Decoders.EthDecoder()
        ip_decoder = Decoders.IPDecoder()
        udp_decoder = Decoders.UDPDecoder()
        tcp_decoder = Decoders.TCPDecoder()

        
        ethernet = eth_decoder.decode(payload)
        if ethernet.get_ether_type() == Packets.IP.ethertype:
            ip = ip_decoder.decode(payload[ethernet.get_header_size():])
            if ip.get_ip_p() == Packets.UDP.protocol: 
                udp = udp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                self.treestore.append(None, [len(self.packets), "UDP", ip.get_ip_src(), ip.get_ip_dst(), udp.get_uh_sport(), udp.get_uh_dport(), int(time.time())])
                self.packets.append(payload)
                        
            if ip.get_ip_p() == Packets.TCP.protocol :
                tcp = tcp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])  
                self.treestore.append(None, [len(self.packets), "TCP", ip.get_ip_src(), ip.get_ip_dst(), tcp.get_th_sport(), tcp.get_th_dport(), int(time.time())])
                self.packets.append(payload)
                
                
    #+---------------------------------------------- 
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
