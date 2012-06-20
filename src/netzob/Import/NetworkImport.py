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
from gettext import gettext as _
from gi.repository import Gtk
import gi
import uuid
from netzob.Import.AbstractImporter import AbstractImporter
gi.require_version('Gtk', '3.0')
import logging
import threading
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.NetworkMessage import NetworkMessage
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory
from netzob.Common.EnvironmentalDependencies import EnvironmentalDependencies


#+---------------------------------------------------------------------------+
#| Network:
#|     This class offers the capability to capture traffic from live network
#+---------------------------------------------------------------------------+
class NetworkImport(AbstractImporter):

    def new(self):
        pass

    def update(self):
        pass

    def clear(self):
        pass

    def kill(self):
        pass

    #+-----------------------------------------------------------------------+
    #| Constructor:
    #| @param zob: a reference to the main netzob.py
    #+-----------------------------------------------------------------------+
    def __init__(self, zob):
        AbstractImporter.__init__(self, "NETWORK IMPORT")
        self.zob = zob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.Network.py')
        self.packets = []

        self.init()

        self.dialog = Gtk.Dialog(title=_("Capture network trafic"), flags=0, buttons=None)
        self.dialog.show()
        self.dialog.vbox.pack_start(self.getPanel(), True, True, 0)
        self.dialog.set_size_request(900, 700)

    def init(self):

        # create the environmental dependancy object
        self.envDeps = EnvironmentalDependencies()

        # Network Capturing Panel
        self.panel = Gtk.Table(rows=7, columns=4, homogeneous=False)
        self.panel.show()

        # Network devices
        label = Gtk.Label(label=_("Network devices"))
        label.show()
        listNetworkDevice = Gtk.combo_box_entry_new_text()
        listNetworkDevice.show()
        listNetworkDevice.set_size_request(300, -1)
        listNetworkDevice.set_model(Gtk.ListStore(str))
        listNetworkDevice.get_model().clear()

        # list of interfaces
        try:
            interfaces = pcapy.findalldevs()
        except:
            self.log.warn(_("You don't have enough permissions to open any network interface on this system."))
            interfaces = []

        for interface in interfaces:
            listNetworkDevice.append_text(str(interface))

        self.panel.attach(label, 0, 1, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(listNetworkDevice, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # BPF filter
        label = Gtk.Label(label=_("BPF filter"))
        label.show()
        entry_filter = Gtk.Entry()
        entry_filter.set_width_chars(50)
        entry_filter.show()
        entry_filter.set_text("tcp port 80")
        self.panel.attach(label, 0, 1, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_filter, 1, 2, 1, 2, xoptions=Gtk.AttachOptions.FILL, yoptions=0, xpadding=5, ypadding=5)

        # Count capturing limit
        label = Gtk.Label(label=_("Count limit"))
        label.show()
        entry_count = Gtk.Entry()
        entry_count.show()
        entry_count.set_text("10")
        self.panel.attach(label, 0, 1, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_count, 1, 2, 2, 3, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Time capturing limit
        label = Gtk.Label(label=_("Timeout"))
        label.show()
        entry_time = Gtk.Entry()
        entry_time.show()
        entry_time.set_text("10")
        self.panel.attach(label, 0, 1, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)
        self.panel.attach(entry_time, 1, 2, 3, 4, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Sniff launching button
        but = Gtk.Button(label=_("Sniff traffic"))
        but.show()
        but.connect("clicked", self.launch_sniff, listNetworkDevice, entry_filter, entry_count, entry_time)
        self.panel.attach(but, 1, 2, 5, 6, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet list
        scroll = Gtk.ScrolledWindow()
        self.treestore = Gtk.TreeStore(int, str, str, str, str, str, int)  # pktID, proto (udp/tcp), IP.src, IP.dst, sport, dport, timestamp
        treeview = Gtk.TreeView(self.treestore)
        treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        treeview.connect("cursor-changed", self.packet_details)
        cell = Gtk.CellRendererText()
        # Col proto
        column = Gtk.TreeViewColumn(_("Proto"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 1)
        treeview.append_column(column)
        # Col IP.src
        column = Gtk.TreeViewColumn(_("IP source"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 2)
        treeview.append_column(column)
        # Col IP.dst
        column = Gtk.TreeViewColumn(_("IP dest"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 3)
        treeview.append_column(column)
        # Col {TCP,UDP}.sport
        column = Gtk.TreeViewColumn(_("sport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 4)
        treeview.append_column(column)
        # Col {TCP,UDP}.dport
        column = Gtk.TreeViewColumn(_("dport"))
        column.pack_start(cell, True)
        column.add_attribute(cell, "text", 5)
        treeview.append_column(column)
        treeview.show()
        scroll.add(treeview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.panel.attach(scroll, 0, 2, 4, 5, xoptions=Gtk.AttachOptions.FILL, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)
        # Button select packets for further analysis
        but = Gtk.Button(label=_("Save selected packets"))
        but.show()
        but.connect("clicked", self.save_packets, treeview)
        self.panel.attach(but, 1, 2, 6, 7, xoptions=0, yoptions=0, xpadding=5, ypadding=5)

        # Packet detail
        scroll = Gtk.ScrolledWindow()
        self.textview = Gtk.TextView()
        self.textview.show()
        self.textview.get_buffer().create_tag("normalTag", family="Courier")
        scroll.add(self.textview)
        scroll.show()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.panel.attach(scroll, 2, 4, 0, 7, xoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, yoptions=Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND, xpadding=5, ypadding=5)

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
                    if ip.get_ip_p() == Packets.TCP.protocol:
                        tcp = tcp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = tcp.get_th_sport()
                        Dport = tcp.get_th_dport()
                        Data = tcp.get_data_as_string()

                # Compute the messages
                message = NetworkMessage(uuid.uuid4(), timestamp, Data.encode("hex"), IPsrc, IPdst, proto, Sport, Dport)
                messages.append(message)

        # We ask the confirmation
        md = Gtk.MessageDialog(None,
            Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK_CANCEL, (_("Are you sure to import the %s selected packets in project %s?") % (str(len(messages)), currentProject.getName())))
#        md.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        resp = md.run()
        md.destroy()

        if resp == Gtk.ResponseType.OK:
            self.saveMessagesInProject(self.zob.getCurrentWorkspace(), currentProject, messages)
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
                self.textview.get_buffer().set_text("")
                self.textview.get_buffer().insert_with_tags_by_name(self.textview.get_buffer().get_start_iter(), str(decoder.decode(payload)), "normalTag")

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff(self, button, dev, filter, count, time):
        button.set_sensitive(False)
        self.envDeps.captureEnvData()  # Retrieve the environmental data (os specific, system specific, etc.)
        self.packets = []
        self.treestore.clear()
        self.textview.get_buffer().set_text("")
        aSniffThread = threading.Thread(None, self.sniffingThread, None, (button, dev, filter, count, time), {})
        aSniffThread.start()

    #+----------------------------------------------
    #| Thread for sniffing work
    #+----------------------------------------------
    def sniffingThread(self, button, devstore, filter, count, time):
        modele = devstore.get_model()
        est_actif = devstore.get_active()
        dev = ""
        if est_actif < 0:
            dev = ""
        dev = modele[est_actif][0]

        self.log.info(_("Launching sniff process on dev {0} with : count={1}, timeout={2}, filter=\"{3}\"").format(dev, count.get_text(), time.get_text(), filter.get_text()))

        sniffer = pcapy.open_live(dev, 1024, False, int(time.get_text()))

        try:
            sniffer.setfilter(filter.get_text())
        except:
            self.log.warn(_("The provided filter is not valid (it should respects the BPF format"))
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
