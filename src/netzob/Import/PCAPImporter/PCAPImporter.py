# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
import errno
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy

from impacket import ImpactPacket as Packets
from impacket import ImpactDecoder as Decoders

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Common.NetzobException import NetzobImportException
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.Messages.L2NetworkMessage import L2NetworkMessage
from netzob.Model.Vocabulary.Messages.L3NetworkMessage import L3NetworkMessage
from netzob.Model.Vocabulary.Messages.L4NetworkMessage import L4NetworkMessage


@NetzobLogger
class PCAPImporter(object):
    r"""PCAP importer to read pcaps and extract messages out of them.

    We recommend using static methods such as

    - PCAPImporter.readFiles(...)
    - PCAPimporter.readFile(...)

    Refer to their documentation to have an overview of the required parameters.

    >>> from netzob.all import *
    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap").values()
    >>> len(messages)
    14

    >>> for m in messages:
    ...    print(repr(m.data))
    b'CMDidentify#\x07\x00\x00\x00Roberto'
    b'RESidentify#\x00\x00\x00\x00\x00\x00\x00\x00'
    b'CMDinfo#\x00\x00\x00\x00'
    b'RESinfo#\x00\x00\x00\x00\x04\x00\x00\x00info'
    b'CMDstats#\x00\x00\x00\x00'
    b'RESstats#\x00\x00\x00\x00\x05\x00\x00\x00stats'
    b'CMDauthentify#\n\x00\x00\x00aStrongPwd'
    b'RESauthentify#\x00\x00\x00\x00\x00\x00\x00\x00'
    b'CMDencrypt#\x06\x00\x00\x00abcdef'
    b"RESencrypt#\x00\x00\x00\x00\x06\x00\x00\x00$ !&'$"
    b"CMDdecrypt#\x06\x00\x00\x00$ !&'$"
    b'RESdecrypt#\x00\x00\x00\x00\x06\x00\x00\x00abcdef'
    b'CMDbye#\x00\x00\x00\x00'
    b'RESbye#\x00\x00\x00\x00\x00\x00\x00\x00'

    PCAP Files with unsupported Layers on OSI Layer 2 can be imported as RawMessages if the importLayer is 1

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/atm_capture1.pcap", importLayer=1).values()
    >>> print(repr(messages[0].data[:-25]))
    b'E\x00\x00T\x17\x82\x00\x00@\x01U\xd3\xc0\xa8F\x01\xc0\xa8F\x02\x08\x00\xfa`Of\x00\x009\xd9\x121\x00\x08w#\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e'

    Raw frame (whole frame is "payload"):

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=1).values()
    >>> print(repr(messages[0].data))
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00E\x00\x003\xdc\x11@\x00@\x11`\xa6\x7f\x00\x00\x01\x7f\x00\x00\x01\xe1\xe7\x10\x92\x00\x1f\xfe2CMDidentify#\x07\x00\x00\x00Roberto'

    Layer 2, e. g. parse Ethernet frame (IP packet is payload)

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=2).values()
    >>> print(repr(messages[0].data))
    b'E\x00\x003\xdc\x11@\x00@\x11`\xa6\x7f\x00\x00\x01\x7f\x00\x00\x01\xe1\xe7\x10\x92\x00\x1f\xfe2CMDidentify#\x07\x00\x00\x00Roberto'

    Layer 3, e. g. parse IP packet (UDP datagram is payload)

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=3).values()
    >>> print(repr(messages[0].data))
    b'\xe1\xe7\x10\x92\x00\x1f\xfe2CMDidentify#\x07\x00\x00\x00Roberto'

    Layer 4, e. g. parse UDP packet (application protocol is payload)

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=4).values()
    >>> print(repr(messages[0].data))
    b'CMDidentify#\x07\x00\x00\x00Roberto'

    Layer > 4, does decode like layer=4

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=5).values()
    >>> print(repr(messages[0].data))
    b'CMDidentify#\x07\x00\x00\x00Roberto'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_http.pcap", importLayer=5, bpfFilter="tcp").values()
    >>> print(repr(messages[0].data))
    b'GET / HTTP/1.1\r\nHost: www.free.fr\r\nUser-Agent: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb)ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\n\r\n'

    Parameter `mergePacketsInFlow` can be use to merge consecutive messages that share the same source and destination (mimic a TCP flow). In practice, this parameter was introduced for L5 network messages to support TCP flows but it can be use for any level of network messages.

    >>> from netzob.all import *
    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_http_flow.pcap", mergePacketsInFlow=False).values()
    >>> len(messages)
    4
    >>> len(messages[1].data)
    1228
    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_http_flow.pcap", mergePacketsInFlow=True).values()
    >>> len(messages)
    2
    >>> len(messages[1].data)
    3224
    """

    INVALID_BPF_FILTER = 0
    INVALID_LAYER2 = 1
    INVALID_LAYER3 = 2
    INVALID_LAYER4 = 3

    PROTOCOL201 = 201

    # Supported datalinks (by pcapy)
    SUPPORTED_DATALINKS = {
        pcapy.DLT_ARCNET: "DLT_ARCNET",
        pcapy.DLT_FDDI: "DLT_FDDI",
        pcapy.DLT_LOOP: "DLT_LOOP",
        pcapy.DLT_PPP_ETHER: "DLT_PPP_ETHER",
        pcapy.DLT_ATM_RFC1483: "DLT_ATM_RFC1483",
        pcapy.DLT_IEEE802: "DLT_IEEE802",
        pcapy.DLT_LTALK: "DLT_LTALK",
        pcapy.DLT_PPP_SERIAL: "DLT_PPP_SERIAL",
        pcapy.DLT_C_HDLC: "DLT_C_HDLC",
        pcapy.DLT_IEEE802_11: "IEEE802_11",
        pcapy.DLT_NULL: "DLT_NULL",
        pcapy.DLT_RAW: "DLT_RAW",
        pcapy.DLT_EN10MB: "DLT_EN10MB",
        pcapy.DLT_LINUX_SLL: "LINUX_SLL",
        pcapy.DLT_PPP: "DLT_PPP",
        pcapy.DLT_SLIP: "DLT_SLIP",
    }

    def __init__(self):
        pass

    @typeCheck(str, str, int)
    def __readMessagesFromFile(self, filePath, bpfFilter, nbPackets):
        """Internal methods to read all messages from a given PCAP file."""
        if (filePath is None):
            raise TypeError("filePath cannot be None")
        if (nbPackets < 0):
            raise ValueError(
                "A positive (or null) value is required for the number of packets to read."
            )

        # Check file can be opened (and read)
        try:
            fp = open(filePath, 'r')
            fp.close()
        except IOError as e:
            if e.errno == errno.EACCES:
                raise IOError(
                    "Error while trying to open the file {0}, more permissions are required to read it."
                ).format(filePath)
            else:
                raise e

        # Check (and configure) the bpf filter
        packetReader = pcapy.open_offline(filePath)
        try:
            packetReader.setfilter(bpfFilter)
        except:
            raise ValueError(
                "The provided BPF filter is not valid (it should follow the BPF format)"
            )

        # Check the datalink
        self.datalink = packetReader.datalink()
        if self.datalink not in list(PCAPImporter.SUPPORTED_DATALINKS.keys()):
            self._logger.debug("Unkown datalinks")

        if self.importLayer > 1 and self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL \
                and self.datalink != pcapy.DLT_RAW and self.datalink != PCAPImporter.PROTOCOL201:
            self._logger.debug('Datalink: ' + str(self.datalink))
            errorMessage = _("This pcap cannot be imported since the " +
                             "layer 2 is not supported ({0})").format(
                                 str(self.datalink))
            raise NetzobImportException("PCAP", errorMessage,
                                        self.INVALID_LAYER2)
        else:
            packetReader.loop(nbPackets, self.__packetHandler)

    def __packetHandler(self, header, payload):
        """Internal callback executed on each packet when parsing the pcap"""
        (secs, usecs) = header.getts()
        epoch = secs + (usecs / 1000000.0)
        self._logger.debug('ImportLayer = '+ str(self.importLayer))
        if self.importLayer == 1:
            if len(payload) == 0:
                return
            # Build the RawMessage
            rawMessage = RawMessage(payload, epoch, source=None, destination=None)

            self.messages.add(rawMessage)

        elif self.importLayer == 2:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload,
                 etherType) = self.__decodeLayer2(header, payload)
            except NetzobImportException as e:
                self._logger.warn(
                    "An error occured while decoding layer2 of a packet: {0}".
                    format(e))
                return
            if len(l2Payload) == 0:
                return

            # Build the L2NetworkMessage
            l2Message = L2NetworkMessage(l2Payload, epoch, l2Proto, l2SrcAddr,
                                         l2DstAddr)

            self.messages.add(l2Message)

        elif self.importLayer == 3:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload,
                 etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload,
                 ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
            except NetzobImportException as e:
                self._logger.warn(
                    "An error occured while decoding layer2 and layer3 of a packet: {0}".
                    format(e))
                return

            if len(l3Payload) == 0:
                return

            # Build the L3NetworkMessage
            l3Message = L3NetworkMessage(l3Payload, epoch, l2Proto, l2SrcAddr,
                                         l2DstAddr, l3Proto, l3SrcAddr,
                                         l3DstAddr)
            self.messages.add(l3Message)

        elif self.importLayer == 4:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload,
                 etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload,
                 ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
                (l4Proto, l4SrcPort, l4DstPort,
                 l4Payload) = self.__decodeLayer4(ipProtocolNum, l3Payload)
            except NetzobImportException as e:
                self._logger.warn(
                    "An error occured while decoding layer2, layer3 or layer4 of a packet: {0}".
                    format(e))
                return
            if len(l4Payload) == 0:
                return

            # Build the L4NetworkMessage
            l4Message = L4NetworkMessage(
                l4Payload, epoch, l2Proto, l2SrcAddr, l2DstAddr, l3Proto,
                l3SrcAddr, l3DstAddr, l4Proto, l4SrcPort, l4DstPort)

            self.messages.add(l4Message)

        else:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload,
                 etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload,
                 ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
                (l4Proto, l4SrcPort, l4DstPort,
                 l4Payload) = self.__decodeLayer4(ipProtocolNum, l3Payload)
            except NetzobImportException as e:
                self._logger.warn(
                    "An error occured while decoding layer2, layer3, layer4 or layer5 of a packet: {0}".
                    format(e))
                return
            if len(l4Payload) == 0:
                return

            l5Message = L4NetworkMessage(
                l4Payload, epoch, l2Proto, l2SrcAddr, l2DstAddr, l3Proto,
                l3SrcAddr, l3DstAddr, l4Proto, l4SrcPort, l4DstPort)
            
            self.messages.add(l5Message)

    def __decodeLayer2(self, header, payload):
        """Internal method that parses the specified header and extracts
        layer2 related proprieties."""

        def formatMacAddress(arrayMac):
            return ":".join("{0:0>2}".format(hex(b)[2:])
                            for b in arrayMac.tolist())

        if self.datalink == pcapy.DLT_EN10MB:
            l2Decoder = Decoders.EthDecoder()
            l2Proto = "Ethernet"
            layer2 = l2Decoder.decode(payload)
            l2SrcAddr = formatMacAddress(layer2.get_ether_shost())
            l2DstAddr = formatMacAddress(layer2.get_ether_dhost())
            l2Payload = payload[layer2.get_header_size():]
            etherType = layer2.get_ether_type()
        elif self.datalink == pcapy.DLT_LINUX_SLL:
            l2Decoder = Decoders.LinuxSLLDecoder()
            l2Proto = "Linux SLL"
            layer2 = l2Decoder.decode(payload)
            l2SrcAddr = layer2.get_addr()
            l2DstAddr = None
            l2Payload = payload[layer2.get_header_size():]
            etherType = layer2.get_ether_type()
        elif self.datalink == PCAPImporter.PROTOCOL201:
            l2Proto = "Protocol 201"
            hdr = payload.encode('hex')[0:8]
            if hdr[6:] == "01":
                l2SrcAddr = "Received"
            else:
                l2SrcAddr = "Sent"
            l2DstAddr = None
            l2Payload = payload[8:]
            etherType = payload[4:6]
        elif self.datalink == pcapy.DLT_RAW:
            l2Proto = None
            l2SrcAddr = None
            l2DstAddr = None
            l2Payload = payload
            etherType = 0x0800

        return (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType)

    def __decodeLayer3(self, etherType, l2Payload):
        """Internal method that parses the specified header and extracts
        layer3 related proprieties."""

        if etherType == Packets.IP.ethertype:
            l3Proto = "IP"
            l3Decoder = Decoders.IPDecoder()
            layer3 = l3Decoder.decode(l2Payload)
            paddingSize = len(l2Payload) - layer3.get_ip_len()

            l3SrcAddr = layer3.get_ip_src()
            l3DstAddr = layer3.get_ip_dst()
            l3Payload = l2Payload[layer3.get_header_size():]
            if paddingSize > 0 and len(l3Payload) > paddingSize:
                l3Payload = l3Payload[:len(l3Payload) - paddingSize]
            ipProtocolNum = layer3.get_ip_p()
            return (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum)
        if etherType == Packets.ARP.ethertype:
            l3Proto = "ARP"
            l3Decoder = Decoders.ARPDecoder()
            layer3 = l3Decoder.decode(l2Payload)

            l3SrcAddr = layer3.get_ar_spa()
            l3DstAddr = layer3.get_ar_tpa()
            l3Payload = l2Payload[:layer3.get_header_size()]
            return (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, None)
        else:
            warnMessage = _("Cannot import one of the provided packets since "
                            + "its layer 3 is unsupported (Only IP is " +
                            "currently supported, packet ethernet " +
                            "type = {} -- {})").format(etherType, etherType.to_bytes(length=2, byteorder='big'))
            self._logger.warn(warnMessage)
            raise NetzobImportException("PCAP", warnMessage,
                                        self.INVALID_LAYER3)

    def __decodeLayer4(self, ipProtocolNum, l3Payload):
        """Internal method that parses the specified header and extracts
        layer4 related proprieties."""

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
            warnMessage = _("Cannot import one of the provided packets since "
                            + "its layer 4 is unsupported (Only UDP and TCP " +
                            "are currently supported, packet IP protocol " +
                            "number = {0})").format(ipProtocolNum)
            self._logger.warn(warnMessage)
            raise NetzobImportException("PCAP", warnMessage,
                                        self.INVALID_LAYER4)

    @typeCheck(list, str, int, int, bool)
    def readMessages(self,
                     filePathList,
                     bpfFilter="",
                     importLayer=5,
                     nbPackets=0,
                     mergePacketsInFlow=False,
                    ):
        """Read all messages from a list of PCAP files. A BPF filter
        can be set to limit the captured packets. The layer of import
        can also be specified:
          - When layer={1, 2}, it means we want to capture a raw layer (such as Ethernet).
          - If layer=3, we capture at the network level (such as IP).
          - If layer=4, we capture at the transport layer (such as TCP or UDP).
          - If layer=5, we capture at the applicative layer (such as the TCP or UDP payload).
         Finally, the number of packets to capture can be specified.

        :param filePathList: the messages to cluster.
        :type filePathList: a list of :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        :param nbPackets: the number of packets to import
        :type nbPackets: :class:`int`
        :param mergePacketsInFlow: if True, consecutive packets with same source and destination ar merged (i.e. to mimic a flow) 
        :type mergePacketsInFlow: :class:`bool`
        :return: a list of captured messages
        :rtype: a list of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """

        # Verify the existence of input files
        errorMessageList = []
        for filePath in filePathList:
            try:
                fp = open(filePath)
                fp.close()
            except IOError as e:
                errorMessage = _("Error while trying to open the " +
                                 "file {0}.").format(filePath)
                if e.errno == errno.EACCES:
                    errorMessage = _("Error while trying to open the file " +
                                     "{0}, more permissions are required for "
                                     + "reading it.").format(filePath)
                errorMessageList.append(errorMessage)
                self._logger.warn(errorMessage)

        if errorMessageList != []:
            raise NetzobImportException("PCAP", "\n".join(errorMessageList))

        # Verify the expected import layer
        availableLayers = [1, 2, 3, 4, 5]
        if not importLayer in availableLayers:
            raise Exception(
                "Only layers level {0} are available.".format(availableLayers))
        self.importLayer = importLayer

        # Call the method that does the import job for each PCAP file
        self.messages = SortedTypedList(AbstractMessage)
        for filePath in filePathList:
            self.__readMessagesFromFile(filePath, bpfFilter, nbPackets)
        
        # if requested, we merge consecutive messages that share same source and destination
        if mergePacketsInFlow:
            mergedMessages = SortedTypedList(AbstractMessage)
            previousMessage = None
            for message in self.messages.values():
                if previousMessage is not None and message.source == previousMessage.source and message.destination == previousMessage.destination:
                    previousMessage.data += message.data
                else:
                    mergedMessages.add(message)
                    previousMessage = message
            self.messages = mergedMessages
            
        return self.messages

    @staticmethod
    @typeCheck(list, str, int, int, bool)
    def readFiles(filePathList, bpfFilter="", importLayer=5, nbPackets=0, mergePacketsInFlow=False):
        """Read all messages from a list of PCAP files. A BPF filter
        can be set to limit the captured packets. The layer of import
        can also be specified:
          - When layer={1, 2}, it means we want to capture a raw layer (such as Ethernet).
          - If layer=3, we capture at the network level (such as IP).
          - If layer=4, we capture at the transport layer (such as TCP or UDP).
          - If layer=5, we capture at the applicative layer (such as the TCP or UDP payload)
         The number of packets to capture can be specified.

        :param filePathList: a list of pcap files to read
        :type filePathList: a list of :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        :param nbPackets: the number of packets to import
        :type nbPackets: :class:`int`
        :param mergePacketsInFlow: if True, consecutive packets with same source and destination ar merged (i.e. to mimic a flow) 
        :type mergePacketsInFlow: :class:`bool`        
        :return: a list of captured messages
        :rtype: a list of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """

        importer = PCAPImporter()
        return importer.readMessages(filePathList,bpfFilter, importLayer, nbPackets, mergePacketsInFlow)

    @staticmethod
    @typeCheck(str, str, int, int, bool)
    def readFile(filePath, bpfFilter="", importLayer=5, nbPackets=0, mergePacketsInFlow=False):
        """Read all messages from the specified PCAP file. A BPF filter
        can be set to limit the captured packets. The layer of import
        can also be specified:
          - When layer={1, 2}, it means we want to capture a raw layer (such as Ethernet).
          - If layer=3, we capture at the network level (such as IP).
          - If layer=4, we capture at the transport layer (such as TCP or UDP).
          - If layer=5, we capture at the applicative layer (such as the TCP or UDP payload) and merge consecutive messages with same source and destination.
         Finally, the number of packets to capture can be specified.

        :param filePath: the pcap path
        :type filePath: :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        :param nbPackets: the number of packets to import
        :type nbPackets: :class:`int`
        :param mergePacketsInFlow: if True, consecutive packets with same source and destination ar merged (i.e. to mimic a flow) 
        :type mergePacketsInFlow: :class:`bool`
        :return: a list of captured messages
        :rtype: a list of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """

        importer = PCAPImporter()
        return importer.readFiles([filePath], bpfFilter, importLayer,
                                  nbPackets, mergePacketsInFlow)

    @staticmethod
    @typeCheck(L2NetworkMessage)
    def getMessageDetails(message):
        """Decode a raw network message and print the content of each
        encapsulated layer.

        :param filePathList: the messages to cluster.
        :type filePathList: a list of :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        """

        decoder = Decoders.EthDecoder()
        return decoder.decode(message.data.convert(Raw))
