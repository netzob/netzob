# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging
import os
import threading
import time
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobWidgets import NetzobInfoMessage, NetzobErrorMessage
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from netzob_plugins.Capturers.NetworkCapturer.NetworkCapturerView import NetworkCapturerView
from netzob_plugins.Capturers.NetworkCapturer.NetworkCapturer import NetworkCapturer
from netzob.Common.EnvironmentalDependencies import EnvironmentalDependencies
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage


class NetworkCapturerController(AbstractExporterController):
    """NetworkCapturerController:
            A controller liking the network capturer and its view in the netzob GUI.
    """

    def run(self):
        """run:
            Show the plugin view.
        """
        # Sanity check
        if self.netzob.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.view.dialog.show_all()
        self.view.hideWarning()
        self.update()

    def new(self):
        """new:
                Called when a user select a new trace.
        """
        pass

    def update(self):
        """update:
                Update the view. More precisely, it sets the symbol tree view which is its left part.
        """
        pass

    def clear(self):
        """clear:
        """
        pass

    def kill(self):
        """kill:
        """
        pass

    def __init__(self, netzob):
        """Constructor of NetworkCapturerController:

                @type netzob: netzob.NetzobGUI.NetzobGUI
                @param netzob: the main netzob project.
        """
        self.netzob = netzob
        self.model = NetworkCapturer(netzob)
        self.view = NetworkCapturerView()
        self.initCallbacks()
        self.envDeps = EnvironmentalDependencies()

    def initCallbacks(self):
        """initCallbacks:
                Link the callbacks.
        """
        self.view.butLaunchSniff.connect("clicked", self.launch_sniff_cb)
        self.view.selection.connect("changed", self.packet_details_cb)
        self.view.butSaveSelectedPackets.connect("clicked", self.save_packets_cb)

    #+----------------------------------------------
    #| Called when user select a list of packet
    #+----------------------------------------------
    def save_packets_cb(self, button):
        currentProject = self.netzob.getCurrentProject()
        # We compute the selected messages
        # Create the new XML structure
        messages = []
        selection = self.view.treeview.get_selection()
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
                l2Proto = "Ethernet"
                EthSrc = ethernet.get_ether_shost()
                EthDst = ethernet.get_ether_dhost()
                if ethernet.get_ether_type() == Packets.IP.ethertype:
                    ip = ip_decoder.decode(packetPayload[ethernet.get_header_size():])
                    IPsrc = ip.get_ip_src()
                    IPdst = ip.get_ip_dst()

                    if ip.get_ip_p() == Packets.UDP.protocol:
                        udp = udp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = udp.get_uh_sport()
                        Dport = udp.get_uh_dport()
                        Data = udp.get_data_as_string()
                        proto = "UDP"
                    if ip.get_ip_p() == Packets.TCP.protocol:
                        tcp = tcp_decoder.decode(packetPayload[ethernet.get_header_size() + ip.get_header_size():])
                        Sport = tcp.get_th_sport()
                        Dport = tcp.get_th_dport()
                        Data = tcp.get_data_as_string()
                        proto = "TCP"

                # Compute the messages
                message = L4NetworkMessage(uuid.uuid4(), timestamp,
                                           Data.encode("hex"), l2Proto, EthSrc, EthDst, "IP",
                                           IPsrc, IPdst, proto, Sport, Dport)
                messages.append(message)

        # We ask the confirmation
        md = Gtk.MessageDialog(None,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION,
                               Gtk.ButtonsType.OK_CANCEL, (_("Are you sure to import the %s selected packets in project %s?") % (str(len(messages)), currentProject.getName())))
#        md.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        resp = md.run()
        md.destroy()

        if resp == Gtk.ResponseType.OK:
            self.saveMessagesInProject(self.netzob.getCurrentWorkspace(), currentProject, messages)
        self.dialog.destroy()

        # We update the gui
        self.netzob.update()

    #+----------------------------------------------
    #| Called when user select a packet for details
    #+----------------------------------------------
    def packet_details_cb(self, selection):
        (model, paths) = selection.get_selected_rows()
        decoder = Decoders.EthDecoder()
        for path in paths[:1]:
            iter = model.get_iter(path)
            if(model.iter_is_valid(iter)):
                packetID = model.get_value(iter, 0)
                payload = self.packets[packetID]
                self.view.textview.get_buffer().set_text("")
                self.view.textview.get_buffer().insert_with_tags_by_name(self.view.textview.get_buffer().get_start_iter(), str(decoder.decode(payload)), "normalTag")

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launch_sniff_cb(self, button):
        button.set_sensitive(False)
        self.envDeps.captureEnvData()  # Retrieve the environmental data (os specific, system specific, etc.)
        self.packets = []
        self.view.treestore.clear()
        self.view.textview.get_buffer().set_text("")
        aSniffThread = threading.Thread(None, self.sniffingThread, None, (button), {})
        aSniffThread.start()

    #+----------------------------------------------
    #| Thread for sniffing work
    #+----------------------------------------------
    def sniffingThread(self, button):
        modele = self.view.listNetworkDevice.get_model()
        est_actif = self.view.listNetworkDevice.get_active()
        dev = ""
        if est_actif < 0:
            dev = ""
        dev = modele[est_actif][0]

        logging.info(_("Launching sniff process on dev {0} with : count={1}, timeout={2}, filter=\"{3}\"").format(dev, self.view.entry_count.get_text(), self.view.entry_time.get_text(), self.view.entry_filter.get_text()))

        sniffer = pcapy.open_live(dev, 1024, False, int(self.view.entry_time.get_text()))

        try:
            sniffer.setfilter(self.view.entry_filter.get_text())
        except:
            logging.warn(_("The provided filter is not valid (it should respects the BPF format"))
            button.set_sensitive(True)
            return

        sniffer.loop(int(self.view.entry_count.get_text()), self.packetHandler)
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
                    self.view.treestore.append(None, [len(self.packets), "UDP", ip.get_ip_src(), ip.get_ip_dst(), udp.get_uh_sport(), udp.get_uh_dport(), int(time.time())])
                    self.packets.append(payload)

            if ip.get_ip_p() == Packets.TCP.protocol:
                tcp = tcp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                if len(tcp.get_data_as_string()) > 0:
                    self.view.treestore.append(None, [len(self.packets), "TCP", ip.get_ip_src(), ip.get_ip_dst(), tcp.get_th_sport(), tcp.get_th_dport(), int(time.time())])
                    self.packets.append(payload)

    def getPanel(self):
        """getPanel:

                @rtype: netzob_plugins.NetworkCapturer.NetworkCapturerView.NetworkCapturerView
                @return: the plugin view.
        """
        return self.view
