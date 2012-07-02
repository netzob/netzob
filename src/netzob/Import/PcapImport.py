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
from gettext import gettext as _
from gi.repository import Gtk
import uuid
import errno
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
#|     Import of PCAP
#+----------------------------------------------
class PcapImport(AbstractImporter):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, netzob):
        AbstractImporter.__init__(self, "PCAP IMPORT")
        self.netzob = netzob
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.PcapImport.py')

        self.messages = []

    #+----------------------------------------------
    #| Called when launching sniffing process
    #+----------------------------------------------
    def launchSniff(self, pcapFile, aFilter, callback):
        self.messages = []
        errorMessage = ""

        # Before reading it we verify we have the necessary rights to open it
        # and to read it. If not we display an error message
        try:
            fp = open(pcapFile)
            fp.close()
        except IOError, e:
            errorMessage = _("Error while trying to open the file {0}.".format(pcapFile))
            if e.errno == errno.EACCES:
                errorMessage = _("Error while trying to open the file {0}, more permissions are required for reading it.".format(pcapFile))
            logging.warn(errorMessage)
            return (False, errorMessage)

        # read it with pcapy
        reader = pcapy.open_offline(pcapFile)

        filter = aFilter.get_text()
#        reader.setfilter(r'ip proto \tcp or \udp')
        try:
            reader.setfilter(filter)
        except:
            errorMessage = _("The provided filter is not valid (it should respects the BPF format)")
            self.log.warn(errorMessage)
            return (False, errorMessage)

        self.log.info(_("Starting import from {0} (linktype:{0})").format(pcapFile, str(reader.datalink())))
        self.datalink = reader.datalink()

        if self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL:
            errorMessage = _("This pcap cannot be imported since the layer 2 is not supported ({0})".format(str(self.datalink)))
            return (False, errorMessage)
        else:
            # I don't see a better way to have synchronous rendering of the GUI
            self.packetHandlerCallback = callback
            reader.loop(0, self.packetHandler)

        return (True, errorMessage)

    def packetHandler(self, header, payload):
        # Definition of the protocol decoders (impacket)
        if self.datalink == pcapy.DLT_EN10MB:
            layer2_decoder = Decoders.EthDecoder()
        elif self.datalink == pcapy.DLT_LINUX_SLL:
            layer2_decoder = Decoders.LinuxSLLDecoder()
        else:
            layer2_decoder = None
            self.log.warn(_("Cannot import one of the provided packets since its layer2 cannot be parsed (datalink = {0} has no decoder)").format(str(self.datalink)))
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
                    self.messages.append(payload)
                    if self.packetHandlerCallback != None:
                        # Yeah, this is not purely MVC... but it is needed to allow synchronous UI rendering
                        self.packetHandlerCallback([len(self.messages), "UDP", ip.get_ip_src(), ip.get_ip_dst(), udp.get_uh_sport(), udp.get_uh_dport(), int(time.time())])

            if ip.get_ip_p() == Packets.TCP.protocol:
                tcp = tcp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                if len(tcp.get_data_as_string()) > 0:
                    self.messages.append(payload)
                    if self.packetHandlerCallback != None:
                        self.packetHandlerCallback([len(self.messages), "TCP", ip.get_ip_src(), ip.get_ip_dst(), tcp.get_th_sport(), tcp.get_th_dport(), int(time.time())])

    #+----------------------------------------------
    #| Called when user wants to save a selection of packets
    #+----------------------------------------------
    def buildMessages(self, packetsToSave):
        currentProject = self.netzob.getCurrentProject()
        # We create the XML structure for the selected messages
        messagesToSave = []
        for (packetPayload, proto, timestamp) in packetsToSave:
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
            messagesToSave.append(message)

        return messagesToSave
