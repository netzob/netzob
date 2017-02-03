# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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

## FIXME: Temporary deactivate this module as it is not currently supported in Python3
# import impacket.ImpactDecoder as Decoders
# import impacket.ImpactPacket as Packets
## Instead, import local adapted files
from netzob.Import.PCAPImporter import ImpactPacket as Packets
from netzob.Import.PCAPImporter import ImpactDecoder as Decoders

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Common.NetzobException import NetzobImportException
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.HexaString import HexaString
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Messages.L2NetworkMessage import L2NetworkMessage
from netzob.Model.Vocabulary.Messages.L3NetworkMessage import L3NetworkMessage
from netzob.Model.Vocabulary.Messages.L4NetworkMessage import L4NetworkMessage


@NetzobLogger
class PCAPImporter(object):
    """PCAP importer to read pcaps and extract messages out of them.
    We recommend to use static methods such as
    - PCAPImporter.readFiles(...)
    - PCAPimporter.readFile(...)
    refer to their documentation to have an overview of the required parameters.

    >>> from netzob.all import *
    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap").values()
    >>> print(len(messages))
    14

    >>> for m in messages:
    ...    print(repr(m.data))
    b'CMDidentify#\\x07\\x00\\x00\\x00Roberto'
    b'RESidentify#\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'
    b'CMDinfo#\\x00\\x00\\x00\\x00'
    b'RESinfo#\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00info'
    b'CMDstats#\\x00\\x00\\x00\\x00'
    b'RESstats#\\x00\\x00\\x00\\x00\\x05\\x00\\x00\\x00stats'
    b'CMDauthentify#\\n\\x00\\x00\\x00aStrongPwd'
    b'RESauthentify#\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'
    b'CMDencrypt#\\x06\\x00\\x00\\x00abcdef'
    b"RESencrypt#\\x00\\x00\\x00\\x00\\x06\\x00\\x00\\x00$ !&'$"
    b"CMDdecrypt#\\x06\\x00\\x00\\x00$ !&'$"
    b'RESdecrypt#\\x00\\x00\\x00\\x00\\x06\\x00\\x00\\x00abcdef'
    b'CMDbye#\\x00\\x00\\x00\\x00'
    b'RESbye#\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=2).values()
    >>> print(repr(messages[0].data))
    b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x08\\x00E\\x00\\x003\\xdc\\x11@\\x00@\\x11`\\xa6\\x7f\\x00\\x00\\x01\\x7f\\x00\\x00\\x01\\xe1\\xe7\\x10\\x92\\x00\\x1f\\xfe2CMDidentify#\\x07\\x00\\x00\\x00Roberto'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=3).values()
    >>> print(repr(messages[0].data))
    b'E\\x00\\x003\\xdc\\x11@\\x00@\\x11`\\xa6\\x7f\\x00\\x00\\x01\\x7f\\x00\\x00\\x01\\xe1\\xe7\\x10\\x92\\x00\\x1f\\xfe2CMDidentify#\\x07\\x00\\x00\\x00Roberto'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=4).values()
    >>> print(repr(messages[0].data))
    b'\\xe1\\xe7\\x10\\x92\\x00\\x1f\\xfe2CMDidentify#\\x07\\x00\\x00\\x00Roberto'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_udp.pcap", importLayer=5).values()
    >>> print(repr(messages[0].data))
    b'CMDidentify#\\x07\\x00\\x00\\x00Roberto'

    >>> messages = PCAPImporter.readFile("./test/resources/pcaps/test_import_http.pcap", importLayer=5, bpfFilter="tcp").values()
    >>> print(repr(messages[0].data))
    b'GET / HTTP/1.1\\r\\nHost: www.free.fr\\r\\nUser-Agent: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa(bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb)ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\\r\\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\\r\\nAccept-Language: en-US,en;q=0.5\\r\\nAccept-Encoding: gzip, deflate\\r\\nConnection: keep-alive\\r\\n\\r\\n'


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
            raise ValueError("A positive (or null) value is required for the number of packets to read.")

        # Check file can be opened (and read)
        try:
            fp = open(filePath, 'r')
            fp.close()
        except IOError as e:
            if e.errno == errno.EACCES:
                raise IOError("Error while trying to open the file {0}, more permissions are required to read it.").format(filePath)
            else:
                raise e

        # Check (and configure) the bpf filter
        packetReader = pcapy.open_offline(filePath)
        try:
            packetReader.setfilter(bpfFilter)
        except:
            raise ValueError("The provided BPF filter is not valid (it should follow the BPF format)")

        # Check the datalink
        self.datalink = packetReader.datalink()
        if self.datalink not in list(PCAPImporter.SUPPORTED_DATALINKS.keys()):
            self._logger.debug("Unkown datalinks")

        if self.importLayer > 1 and self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL and self.datalink != PCAPImporter.PROTOCOL201:
            errorMessage = _("This pcap cannot be imported since the "
                             + "layer 2 is not supported ({0})").format(str(self.datalink))
            raise NetzobImportException("PCAP", errorMessage, self.INVALID_LAYER2)
        else:
            packetReader.loop(nbPackets, self.__packetHandler)

    def __packetHandler(self, header, payload):
        """Internal callback executed on each packet when parsing the pcap"""
        (secs, usecs) = header.getts()
        epoch = secs + (usecs / 1000000.0)

        if self.importLayer == 1 or self.importLayer == 2:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = self.__decodeLayer2(header, payload)
            except NetzobImportException as e:
                self._logger.warn("An error occured while decoding layer2 of a packet: {0}".format(e))
                return
            if len(l2Payload) == 0:
                return

            # Build the L2NetworkMessage
            l2Message = L2NetworkMessage(payload, epoch, l2Proto, l2SrcAddr, l2DstAddr)

            self.messages.add(l2Message)

        elif self.importLayer == 3:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
            except NetzobImportException as e:
                self._logger.warn("An error occured while decoding layer2 and layer3 of a packet: {0}".format(e))
                return

            if len(l3Payload) == 0:
                return

            # Build the L3NetworkMessage
            l3Message = L3NetworkMessage(l2Payload, epoch, l2Proto, l2SrcAddr, l2DstAddr, l3Proto, l3SrcAddr, l3DstAddr)
            self.messages.add(l3Message)

        elif self.importLayer == 4:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
                (l4Proto, l4SrcPort, l4DstPort, l4Payload) = self.__decodeLayer4(ipProtocolNum, l3Payload)
            except NetzobImportException as e:
                self._logger.warn("An error occured while decoding layer2, layer3 or layer4 of a packet: {0}".format(e))
                return
            if len(l4Payload) == 0:
                return

            # Build the L4NetworkMessage
            l4Message = L4NetworkMessage(l3Payload, epoch, l2Proto, l2SrcAddr, l2DstAddr,
                                         l3Proto, l3SrcAddr, l3DstAddr, l4Proto, l4SrcPort, l4DstPort)

            self.messages.add(l4Message)

        else:
            try:
                (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = self.__decodeLayer2(header, payload)
                (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = self.__decodeLayer3(etherType, l2Payload)
                (l4Proto, l4SrcPort, l4DstPort, l4Payload) = self.__decodeLayer4(ipProtocolNum, l3Payload)
            except NetzobImportException as e:
                self._logger.warn("An error occured while decoding layer2, layer3, layer4 or layer5 of a packet: {0}".format(e))
                return
            if len(l4Payload) == 0:
                return

            l5Message = L4NetworkMessage(l4Payload, epoch, l2Proto, l2SrcAddr, l2DstAddr,
                                         l3Proto, l3SrcAddr, l3DstAddr, l4Proto, l4SrcPort, l4DstPort)

            self.messages.add(l5Message)

    def __decodeLayer2(self, header, payload):
        """Internal method that parses the specified header and extracts
        layer2 related proprieties."""

        def formatMacAddress(arrayMac):
            return ":".join("{0:0>2}".format(
                hex(b)[2:]) for b in arrayMac.tolist())

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
        else:
            warnMessage = _("Cannot import one of the provided packets since " +
                            "its layer 3 is unsupported (Only IP is " +
                            "currently supported, packet ethernet " +
                            "type = {0})").format(etherType)
            self._logger.warn(warnMessage)
            raise NetzobImportException("PCAP", warnMessage, self.INVALID_LAYER3)

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
            warnMessage = _("Cannot import one of the provided packets since " +
                            "its layer 4 is unsupported (Only UDP and TCP " +
                            "are currently supported, packet IP protocol " +
                            "number = {0})").format(ipProtocolNum)
            self._logger.warn(warnMessage)
            raise NetzobImportException("PCAP", warnMessage, self.INVALID_LAYER4)

    @typeCheck(list, str, int, int)
    def readMessages(self, filePathList, bpfFilter="", importLayer=5, nbPackets=0):
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
        :return: a list of captured messages
        :rtype: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        """

        # Verify the existence of input files
        errorMessageList = []
        for filePath in filePathList:
            try:
                fp = open(filePath)
                fp.close()
            except IOError as e:
                errorMessage = _("Error while trying to open the "
                                 + "file {0}.").format(filePath)
                if e.errno == errno.EACCES:
                    errorMessage = _("Error while trying to open the file "
                                     + "{0}, more permissions are required for "
                                     + "reading it.").format(filePath)
                errorMessageList.append(errorMessage)
                self._logger.warn(errorMessage)

        if errorMessageList != []:
            raise NetzobImportException("PCAP", "\n".join(errorMessageList))

        # Verify the expected import layer
        availableLayers = [1, 2, 3, 4, 5]
        if not importLayer in availableLayers:
            raise Exception("Only layers level {0} are available.".format(availableLayers))
        self.importLayer = importLayer

        # Call the method that does the import job for each PCAP file
        self.messages = SortedTypedList(AbstractMessage)
        for filePath in filePathList:
            self.__readMessagesFromFile(filePath, bpfFilter, nbPackets)
        return self.messages

    @staticmethod
    @typeCheck(list, str, int, int)
    def readFiles(filePathList, bpfFilter="", importLayer=5, nbPackets=0):
        """Read all messages from a list of PCAP files. A BPF filter
        can be set to limit the captured packets. The layer of import
        can also be specified:
          - When layer={1, 2}, it means we want to capture a raw layer (such as Ethernet).
          - If layer=3, we capture at the network level (such as IP).
          - If layer=4, we capture at the transport layer (such as TCP or UDP).
          - If layer=5, we capture at the applicative layer (such as the TCP or UDP payload).
         Finally, the number of packets to capture can be specified.

        :param filePathList: a list of pcap files to read
        :type filePathList: a list of :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        :param nbPackets: the number of packets to import
        :type nbPackets: :class:`int`
        :return: a list of captured messages
        :rtype: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        """

        importer = PCAPImporter()
        return importer.readMessages(filePathList, bpfFilter, importLayer, nbPackets)

    @staticmethod
    @typeCheck(str, str, int, int)
    def readFile(filePath, bpfFilter="", importLayer=5, nbPackets=0):
        """Read all messages from the specified PCAP file. A BPF filter
        can be set to limit the captured packets. The layer of import
        can also be specified:
          - When layer={1, 2}, it means we want to capture a raw layer (such as Ethernet).
          - If layer=3, we capture at the network level (such as IP).
          - If layer=4, we capture at the transport layer (such as TCP or UDP).
          - If layer=5, we capture at the applicative layer (such as the TCP or UDP payload).
         Finally, the number of packets to capture can be specified.

        :param filePath: the pcap path
        :type filePath: :class:`str`
        :param bpfFilter: a string representing a BPF filter.
        :type bpfFilter: :class:`str`
        :param importLayer: an integer representing the protocol layer to start importing.
        :type importLayer: :class:`int`
        :param nbPackets: the number of packets to import
        :type nbPackets: :class:`int`
        :return: a list of captured messages
        :rtype: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        """

        importer = PCAPImporter()
        return importer.readFiles([filePath], bpfFilter, importLayer, nbPackets)

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
        return decoder.decode(TypeConverter.convert(message.data, HexaString, Raw))
