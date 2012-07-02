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
from netzob.Common.Models.NetworkMessage import NetworkMessage
from netzob.Common.NetzobException import NetzobImportException
from netzob.Import.AbstractImporter import AbstractImporter
from netzob.UI.ModelReturnCodes import ERROR, WARNING, SUCCEDED
from twisted.plugins.twisted_qtstub import errorMessage

class PCAPImporter(AbstractImporter):
    """Model of PCAP importer plugin"""

    INVALID_BPF_FILTER = 0
    INVALID_LAYER2 = 1
    INVALID_LAYER3 = 2
    INVALID_LAYER4 = 3

    def __init__(self, currentWorkspace, currentProject):
        super(PCAPImporter, self).__init__("PCAP IMPORT")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.PcapImport.py')
        self.filePathList = []
        self.bpfFilter = None
        self.currentWorkspace = currentWorkspace
        self.currentProject = currentProject
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
        self.filePathList = filePathList

    def setBPFFilter(self, bpfFilter):
        self.bpfFilter = bpfFilter

    def readMessages(self):
        """Read all messages from all opened PCAP files"""
        self.messages = []
        for filePath in self.filePathList:
            self._readMessagesFromFile(filePath)

    def saveMessagesInProject(self, messageIDList):
        addMessages = []
        for messageID in messageIDList:
            message = self.getMessageByID(str(messageID))
            if message is not None:
                addMessages.append(message)
            else:
                errorMessage = _("Message ID: {0} not found in importer " +
                                "message list").format(messageID)
                raise NetzobImportException("PCAP", errorMessage, ERROR)
        super(PCAPImporter, self).saveMessagesInProject(self.currentWorkspace, 
                self.currentProject, addMessages, False)

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

        if self.datalink == pcapy.DLT_EN10MB:
            layer2_decoder = Decoders.EthDecoder()
        elif self.datalink == pcapy.DLT_LINUX_SLL:
            layer2_decoder = Decoders.LinuxSLLDecoder()
        ip_decoder = Decoders.IPDecoder()
        udp_decoder = Decoders.UDPDecoder()
        tcp_decoder = Decoders.TCPDecoder()

        ethernet = layer2_decoder.decode(payload)
        if ethernet.get_ether_type() == Packets.IP.ethertype:
            ip = ip_decoder.decode(payload[ethernet.get_header_size():])
            if ip.get_ip_p() == Packets.UDP.protocol:
                udp = udp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                udpData = udp.get_data_as_string()
                mUuid = uuid.uuid4()
                if len(udpData) > 0:
                    timestamp = int(time.time())
                    message = NetworkMessage(
                        mUuid,
                        timestamp,
                        udpData.encode("hex"),
                        ip.get_ip_src(),
                        ip.get_ip_dst(),
                        "UDP",
                        udp.get_uh_sport(),
                        udp.get_uh_dport())
                    self.messages.append(message)
                    self._payloadDict[mUuid] = payload
            elif ip.get_ip_p() == Packets.TCP.protocol:
                tcp = tcp_decoder.decode(payload[ethernet.get_header_size() + ip.get_header_size():])
                tcpData = tcp.get_data_as_string()
                if len(tcpData) > 0:
                    timestamp = int(time.time())
                    message = NetworkMessage(
                        mUuid,
                        timestamp,
                        tcpData.encode("hex"),
                        ip.get_ip_src(),
                        ip.get_ip_dst(),
                        "TCP",
                        tcp.get_th_sport(),
                        tcp.get_th_dport())
                    self.messages.append(message)
                    self._payloadDict[mUuid] = payload
            else:
                warnMessage = _("Cannot import one of the provided packets since " +
                               "its layer 4 is unsupported (Only UDP and TCP " +
                               "are currently supported, packet IP protocol " + 
                               "number = {0})").format(ip.get_ip_p())
                self.log.warn(warnMessage)
                raise NetzobImportException("PCAP", warnMessage, WARNING,
                                            self.INVALID_LAYER4)
        else:
                warnMessage = _("Cannot import one of the provided packets since " +
                              "its layer 3 is unsupported (Only IP is " +
                              "currently supported, packet ethernet " +
                              "type = {0})").format(ethernet.get_ether_type())
                self.log.warn(warnMessage)
                raise NetzobImportException("PCAP", warnMessage, WARNING,
                                            self.INVALID_LAYER3)

    def getMessageDetails(self, messageID):
        if not messageID in self._payloadDict:
            errorMessage = _("Message ID: {0} not found in importer " + 
                "message list").format(messageID)
            self.log.error(errorMessage)
            raise NetzobImportException("PCAP", errorMessage, ERROR)
        decoder = Decoders.EthDecoder()
        payload = self._payloadDict[messageID]
        return decoder.decode(payload)
