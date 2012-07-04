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
import logging
import errno
import time
import uuid
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import pcapy
import impacket.ImpactDecoder as Decoders
import impacket.ImpactPacket as Packets

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.NetzobException import NetzobImportException
from netzob.Import.AbstractImporter import AbstractImporter
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED
from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage

class PCAPImporter(AbstractImporter):
    """Model of PCAP importer plugin"""

    INVALID_BPF_FILTER = 0
    INVALID_LAYER2 = 1
    INVALID_LAYER3 = 2
    INVALID_LAYER4 = 3

    def __init__(self, currentWorkspace, currentProject):
        super(PCAPImporter, self).__init__("PCAP IMPORT", currentWorkspace, currentProject)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.PcapImport.py')
        self.filesToBeImported = []
        self.bpfFilter = None
        self.importLayer = 4
        self._payloadDict = {}

    @property
    def payloadDict(self):
        return self._payloadDict.copy()

    def setSourceFiles(self, filePathList):
        errorMessageList = []
        for filePath in filePathList:
            try:
                fp = open(filePath)
                fp.close()
            except IOError, e:
                errorMessage = _("Error while trying to open the "
                        + "file {0}.").format(filePath)
                if e.errno == errno.EACCES:
                    errorMessage = _("Error while trying to open the file "
                            + "{0}, more permissions are required for "
                            + "reading it.").format(filePath)
                errorMessageList.append(errorMessage)
                self.log.warn(errorMessage)

        if errorMessageList != []:
            raise NetzobImportException("PCAP", "\n".join(errorMessageList),
                        ERROR)
        self.filesToBeImported = filePathList

    def setBPFFilter(self, bpfFilter):
        self.bpfFilter = bpfFilter

    def setImportLayer(self, importLayer):
        if not importLayer in [2, 3, 4]:
            raise
        self.importLayer = importLayer

    def readMessages(self):
        """Read all messages from all opened PCAP files"""
        self.messages = []
        for filePath in self.filesToBeImported:
            self._readMessagesFromFile(filePath)

    def _readMessagesFromFile(self, filePath):
        """Read all messages from a given PCAP file"""
        packetReader = pcapy.open_offline(filePath)
        try:
            packetReader.setfilter(self.bpfFilter)
        except:
            errorMessage = _("The provided filter is not valid "
                             + "(it should follow the BPF format)")
            self.log.warn(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR,
                        self.INVALID_BPF_FILTER)

        self.log.info(_("Starting import from {0} (linktype:{0})")\
                            .format(filePath, str(packetReader.datalink())))
        self.datalink = packetReader.datalink()

        if self.datalink != pcapy.DLT_EN10MB and self.datalink != pcapy.DLT_LINUX_SLL:
            errorMessage = _("This pcap cannot be imported since the "
                    + "layer 2 is not supported ({0})").format(str(self.datalink))
            self.log.warn(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR,
                        self.INVALID_LAYER2)
        else:
            packetReader.loop(0, self._packetHandler)

    def _packetHandler(self, header, payload):
        """Decode a packet"""
        mUuid = uuid.uuid4()
        mTimestamp = int(time.time())
        if self.importLayer == 2:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                    self.decodeLayer2(header, payload)
            self.messages.append(
                    L2NetworkMessage(
                            mUuid,
                            mTimestamp,
                            l2Payload.encode("hex"),
                            l2Proto,
                            l2SrcAddr,
                            l2DstAddr))
            self._payloadDict[mUuid] = payload
        elif self.importLayer == 3:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                    self.decodeLayer2(header, payload)
            (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = \
                    self.decodeLayer3(etherType, l2Payload)
            self.messages.append(
                    L3NetworkMessage(
                            mUuid,
                            mTimestamp,
                            l3Payload.encode("hex"),
                            l2Proto,
                            l2SrcAddr,
                            l2DstAddr,
                            l3Proto,
                            l3SrcAddr,
                            l3DstAddr))
            self._payloadDict[mUuid] = payload
        else:
            (l2Proto, l2SrcAddr, l2DstAddr, l2Payload, etherType) = \
                    self.decodeLayer2(header, payload)
            (l3Proto, l3SrcAddr, l3DstAddr, l3Payload, ipProtocolNum) = \
                    self.decodeLayer3(etherType, l2Payload)
            (l4Proto, l4SrcPort, l4DstPort, l4Payload) = \
                    self.decodeLayer4(ipProtocolNum, l3Payload)
            self.messages.append(
                    L4NetworkMessage(
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
                            l4DstPort))
            self._payloadDict[mUuid] = payload

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
            self.log.warn(warnMessage)
            raise NetzobImportException("PCAP", warnMessage, WARNING,
                        self.INVALID_LAYER3)

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
                warnMessage = _("Cannot import one of the provided packets since " +
               "its layer 4 is unsupported (Only UDP and TCP " +
               "are currently supported, packet IP protocol " +
               "number = {0})").format(ipProtocolNum.get_ip_p())
                self.log.warn(warnMessage)
                raise NetzobImportException("PCAP", warnMessage, WARNING,
                                            self.INVALID_LAYER4)
    def getMessageDetails(self, messageID):
        if not messageID in self._payloadDict:
            errorMessage = _("Message ID: {0} not found in importer " +
                "message list").format(messageID)
            self.log.error(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR)
        decoder = Decoders.EthDecoder()
        payload = self._payloadDict[messageID]
        return decoder.decode(payload)
