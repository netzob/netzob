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
import gtk
import pygtk
import uuid
import errno
from netzob.UI.NetzobWidgets import NetzobErrorMessage
pygtk.require('2.0')
import logging
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Models.NetworkMessage import NetworkMessage
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory
from netzob.Import.AbstractImporter import AbstractImporter


#+----------------------------------------------
#| Pcap:
#|     GUI for capturing messages imported through a provided PCAP
#+----------------------------------------------
class PcapImport(AbstractImporter):

    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, zob):
        AbstractImporter.__init__(self, "PCAP IMPORT")
        self.zob = zob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.pcap.py')
        self.packets = []

        self.init()
        self.dialog = gtk.Dialog(title="Import PCAP file", flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(900, 700)

    def init(self):

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
#        label.show()  # TODO : implement the filter
        entry_filter = gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
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
        self.treestore = gtk.TreeStore(int, str, str, str, str, str, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
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
        self.panel.attach(scroll, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)
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
        self.panel.attach(scroll, 2, 4, 0, 5, xoptions=gtk.FILL | gtk.EXPAND, yoptions=gtk.FILL | gtk.EXPAND, xpadding=5, ypadding=5)

    #+----------------------------------------------
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets(self, button, treeview):

        currentProject = self.zob.getCurrentProject()
        # We compute the selected messages
        # Create the new XML structure
        messages = []
        selection = treeview.get_selection()
        (model, paths) = selection.get_selected_rows()
        for path in paths:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                proto = model.get_value(iter, 1)
                timestamp = str(model.get_value(iter, 6))
                packetPayload = self.packets[packetID]

                if self.datalink == pcapy.DLT_EN10MB:
                    layer2_decoder = Decoders.EthDecoder()
                elif self.datalink == pcapy.DLT_LINUX_SLL:
                    layer2_decoder = Decoders.LinuxSLLDecoder()

                ip_decoder = Decoders.IPDecoder()
                udp_decoder = Decoders.UDPDecoder()
                tcp_decoder = Decoders.TCPDecoder()

                IPsrc = None
                IPdst = None
                Sport = None
                Dport = None
                Data = None

                ethernet = layer2_decoder.decode(packetPayload)
                if ethernet.get_ether_type() == Packets.IP.ethertype:
                    ip = ip_decoder.decode(packetPayload[ethernet.get_header_size():])
                    IPsrc = ip.get_ip_src()
                    IPdst = ip.get_ip_dst()

                    if ip.get_ip_p() == Packets.UDP.protocol:
                        udp = udp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = udp.get_uh_sport()
                        Dport = udp.get_uh_dport()
                        Data = udp.get_data_as_string()
                    if ip.get_ip_p() == Packets.TCP.protocol:
                        tcp = tcp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = tcp.get_th_sport()
                        Dport = tcp.get_th_dport()
                        Data = tcp.get_data_as_string()

                # Compute the messages
                message = NetworkMessage(uuid.uuid4(), timestamp, Data.encode("hex"), IPsrc, IPdst, proto, Sport, Dport)
                messages.append(message)

        # We ask the confirmation
        md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL, "Are you sure to import the " + str(len(messages)) + " selected packets in project " + currentProject.getName() + ".")
#        md.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        resp = md.run()
        md.destroy()

        if resp == gtk.RESPONSE_OK:
            self.saveMessagesInProject(self.zob.getCurrentWorkspace(), currentProject, messages, False)
        self.dialog.destroy()

        # We update the gui
        self.zob.update()

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
                self.textview.get_buffer().set_text(str(decoder.decode(payload)))

    #+----------------------------------------------
    #| Called when user import a pcap file
    #+----------------------------------------------
    def import_pcap(self, button, label):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            label.set_text(chooser.get_filename())
        chooser.destroy()

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, aFilter, label_file):
        self.textview.get_buffer().set_text("")

        # retrieve the choosen pcap file
        pcapFile = label_file.get_text()

        # Before reading it we verify we have the necessary rights to open it
        # and to read it. If not we display an error message
        try:
            fp = open(pcapFile)
            fp.close()
        except IOError, e:
            errorMessage = "Error while trying to open the file " + pcapFile + "."
            if e.errno == errno.EACCES:
                errorMessage = "Error while trying to open the file " + pcapFile + ", more permissions are required for reading it."

            logging.warn(errorMessage)
            md = gtk.MessageDialog(None,
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_CLOSE, errorMessage)
            md.run()
            md.destroy()

            return

        button.set_sensitive(False)
        self.packets = []
        self.treestore.clear()

        # read it with pcapy
        reader = pcapy.open_offline(pcapFile)

        filter = aFilter.get_text()
#        reader.setfilter(r'ip proto \tcp or \udp')
        try:
            reader.setfilter(filter)
        except:
            self.logging.warn("The provided filter is not valid (it should respects the BPF format")
            button.set_sensitive(True)
            return

        self.log.info("Starting import from " + pcapFile + " (linktype:" + str(reader.datalink()) + ")")
        self.datalink = reader.datalink()

        if self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL:
            NetzobErrorMessage("This pcap cannot be imported since the layer 2 is not supported (" + str(self.datalink) + ")")
        else:
            reader.loop(0, self.packetHandler)
        button.set_sensitive(True)

    def packetHandler(self, header, payload):
        # Definition of the protocol decoders (impacket)
        if self.datalink == pcapy.DLT_EN10MB:
            layer2_decoder = Decoders.EthDecoder()
        elif self.datalink == pcapy.DLT_LINUX_SLL:
            layer2_decoder = Decoders.LinuxSLLDecoder()
        else:
            layer2_decoder = None
            self.log.warn("Cannot import one of the provided packets since its layer2 cannot be parsed (datalink = " + str(self.datalink) + " has no decoder)")
            return

        ip_decoder = Decoders.IPDecoder()
        udp_decoder = Decoders.UDPDecoder()
        tcp_decoder = Decoders.TCPDecoder()

        ethernet = layer2_decoder.decode(payload)
        if ethernet.get_ether_type() == Packets.IP.ethertype:
            ip = ip_decoder.decode(payload[ethernet.get_header_size():])
            if ip.get_ip_p() == Packets.UDP.protocol:
                udp = udp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                if len(udp.get_data_as_string()) > 0:
                    self.treestore.append(None, [len(self.packets), "UDP", ip.get_ip_src(), ip.get_ip_dst(), udp.get_uh_sport(), udp.get_uh_dport(), int(time.time())])
                    self.packets.append(payload)

            if ip.get_ip_p() == Packets.TCP.protocol:
                tcp = tcp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                if len(tcp.get_data_as_string()) > 0:
                    self.treestore.append(None, [len(self.packets), "TCP", ip.get_ip_src(), ip.get_ip_dst(), tcp.get_th_sport(), tcp.get_th_dport(), int(time.time())])
                    self.packets.append(payload)

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getPanel(self):
        return self.panel
