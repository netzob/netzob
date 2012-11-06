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
import uuid
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
from netzob.Common.EnvironmentalDependencies import EnvironmentalDependencies
from netzob.Common.Plugins.Capturers.AbstractCapturer import AbstractCapturer
from netzob.Common.NetzobException import NetzobImportException
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage


#+---------------------------------------------------------------------------+
#| NetworkCapturer:
#|
#+---------------------------------------------------------------------------+
class NetworkCapturer(AbstractCapturer):
    """NetworkCapturer: This class offers the capability to capture
    traffic from live network.
    """

    INVALID_BPF_FILTER = 0
    INVALID_LAYER2 = 1
    INVALID_LAYER3 = 2
    INVALID_LAYER4 = 3

    def __init__(self, netzob):
        super(NetworkCapturer, self).__init__("NETWORK CAPTURER", netzob)
        # create logger with the given configuration
        self.bpfFilter = None
        self.importLayer = 4
        self._payloadDict = {}
        self.envDeps = EnvironmentalDependencies()

    @property
    def payloadDict(self):
        return self._payloadDict.copy()

    def setBPFFilter(self, bpfFilter):
        self.bpfFilter = bpfFilter

    def setImportLayer(self, importLayer):
        if not importLayer in [1, 2, 3, 4]:
            raise
        self.importLayer = importLayer

    def getNetworkDevices(self):
        interfaces = []
        # list of interfaces
        try:
            interfaces = pcapy.findalldevs()
        except:
            logging.warn("You don't have enough permissions to open any network interface on this system. Please look at the README.rst file for more information.")
        return interfaces

    def readMessages(self, callback_readMessage, device, count, time):
        """Read all messages from all opened PCAP files"""
        self.callback_readMessage = callback_readMessage
        self.envDeps.captureEnvData()  # Retrieve the environmental data (os specific, system specific, etc.)
        self.messages = []
        aSniffThread = threading.Thread(None, self.sniffingThread, None, (device, count, time), {})
        aSniffThread.start()

    #+----------------------------------------------
    #| Thread for sniffing work
    #+----------------------------------------------
    def sniffingThread(self, device, count, time):
        logging.info("Launching sniff process on dev {0} with: count={1}, timeout={2}, filter=\"{3}\"".format(device, count, time, self.bpfFilter))
        sniffer = pcapy.open_live(device, 1024, False, int(time))
        try:
            sniffer.setfilter(self.bpfFilter)
        except:
            logging.warn("The provided filter is not valid (it should respects the BPF format")
            return

        self.datalink = sniffer.datalink()
        if self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL:
            errorMessage = _("This device cannot be sniffed since the "
                             + "layer 2 is not supported ({0})").format(str(self.datalink))
            self.log.warn(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR,
                                        self.INVALID_LAYER2)
        else:
            sniffer.loop(int(count), self._packetHandler)

    def _packetHandler(self, header, payload):
        """Decode a packet"""
        mUuid = str(uuid.uuid4())
        mTimestamp = int(time.time())
        message = None
        if self.importLayer == 1:
            if len(payload) == 0:
                return
            message = RawMessage(
                mUuid,
                mTimestamp,
                payload.encode("hex"))
            self._payloadDict[mUuid] = payload
        elif self.importLayer == 2:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                self.decodeLayer2(header, payload)
            if len(l2Payload) == 0:
                return
            message = L2NetworkMessage(
                mUuid,
                mTimestamp,
                l2Payload.encode("hex"),
                l2Proto,
                l2SrcAddr,
                l2DstAddr)
            self._payloadDict[mUuid] = payload
        elif self.importLayer == 3:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                self.decodeLayer2(header, payload)
            try:
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = \
                    self.decodeLayer3(etherType, l2Payload)
            except TypeError:
                return
            if len(l3Payload) == 0:
                return
            message = L3NetworkMessage(
                mUuid,
                mTimestamp,
                l3Payload.encode("hex"),
                l2Proto,
                l2SrcAddr,
                l2DstAddr,
                l3Proto,
                l3SrcAddr,
                l3DstAddr)
            self._payloadDict[mUuid] = payload
        else:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                self.decodeLayer2(header, payload)
            try:
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = \
                    self.decodeLayer3(etherType, l2Payload)
                (l4Proto, l4SrcPort, l4DstPort, l4Payload) = \
                    self.decodeLayer4(ipProtocolNum, l3Payload)
            except TypeError:
                return
            if l4Payload.encode("hex") == "":
                return
            if len(l4Payload) == 0:
                return
            message = L4NetworkMessage(
                mUuid,
                mTimestamp,
                l4Payload.encode("hex"),
                l2Proto,
                l2SrcAddr,
                l2DstAddr,
                l3Proto,
                l3SrcAddr,
                l3DstAddr,
                l4Proto,
                l4SrcPort,
                l4DstPort)
            self._payloadDict[mUuid] = payload
        self.messages.append(message)
        self.callback_readMessage(message)

    def decodeLayer2(self, header, payload):
        def formatMacAddress(arrayMac):
            return ":".join("{0:0>2}".format(
                hex(b)[2:]) for b in arrayMac.tolist())

        if self.datalink == pcapy.DLT_EN10MB:
            l2Decoder = Decoders.EthDecoder()
            l2Proto = "Ethernet"
            layer2 = l2Decoder.decode(payload)
            l2SrcAddr = formatMacAddress(layer2.get_ether_shost())
            l2DstAddr = formatMacAddress(layer2.get_ether_dhost())
        elif self.datalink == pcapy.DLT_LINUX_SLL:
            l2Decoder = Decoders.LinuxSLLDecoder()
            l2Proto = "Linux SLL"
            layer2 = l2Decoder.decode(payload)
            l2SrcAddr = layer2.get_addr()
            l2DstAddr = None
        l2Payload = payload[layer2.get_header_size():]
        etherType = layer2.get_ether_type()
        return (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType)

    def decodeLayer3(self, etherType, l2Payload):
        if etherType == Packets.IP.ethertype:
            l3Proto = "IP"
            l3Decoder = Decoders.IPDecoder()
            layer3 = l3Decoder.decode(l2Payload)
            l3SrcAddr = layer3.get_ip_src()
            l3DstAddr = layer3.get_ip_dst()
            l3Payload = l2Payload[layer3.get_header_size():]
            ipProtocolNum = layer3.get_ip_p()
            return (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum)
        else:
            warnMessage = _("Cannot import one of the provided packets since " +
                            "its layer 3 is unsupported (Only IP is " +
                            "currently supported, packet ethernet " +
                            "type = {0})").format(etherType)
            logging.warn(warnMessage)

    def decodeLayer4(self, ipProtocolNum, l3Payload):
            if ipProtocolNum == Packets.UDP.protocol:
                l4Proto = "UDP"
                l4Decoder = Decoders.UDPDecoder()
                layer4 = l4Decoder.decode(l3Payload)
                l4SrcPort = layer4.get_uh_sport()
                l4DstPort = layer4.get_uh_dport()
                l4Payload = layer4.get_data_as_string()
                return (l4Proto, l4SrcPort, l4DstPort, l4Payload)
            elif ipProtocolNum == Packets.TCP.protocol:
                l4Proto = "TCP"
                l4Decoder = Decoders.TCPDecoder()
                layer4 = l4Decoder.decode(l3Payload)
                l4SrcPort = layer4.get_th_sport()
                l4DstPort = layer4.get_th_dport()
                l4Payload = layer4.get_data_as_string()
                return (l4Proto, l4SrcPort, l4DstPort, l4Payload)
            else:
                warnMessage = "Cannot import one of the provided packets since its layer 4 is unsupported (Only UDP and TCP are currently supported, packet IP protocol number = {0})".format(ipProtocolNum)
                logging.warn(warnMessage)

    def getMessageDetails(self, messageID):
        if not messageID in self._payloadDict:
            errorMessage = "Message ID: {0} not found in importer message list".format(messageID)
            logging.error(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR)
        decoder = Decoders.EthDecoder()
        payload = self._payloadDict[messageID]
        return decoder.decode(payload)
