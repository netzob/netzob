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
import logging
import os

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from common.NetzobTestCase import NetzobTestCase
from netzob.all import *


class test_ImportPCAP(NetzobTestCase):

    def test_createSymbolWithPCAPMessages(self):
        """Tests (and illustrates) how to import messages
        from a PCAP and store them in a dedicated symbol"""

        pcapFile = os.path.join("test", "resources", "pcaps", "botnet_irc_bot.pcap")
        symbol = Symbol(messages=list(PCAPImporter.readFile(pcapFile).values()))
        self.assertTrue(len(symbol.messages) == 17)

    def test_importPCAPApplicativeLayer(self):
        """Test (and illustrates) how to import messages
        out of a pcap. In this test, we only consider the payload
        of the applicative layer (L5) while headers of L5 and below layers
        will be stored as properties (e.g. metadata).

        """
        logging.debug("Test : Import messages from the applicative layer of a PCAP.")

        pcapFile = os.path.join("test", "resources", "pcaps", "botnet_irc_bot.pcap")
        messages = PCAPImporter.readFile(pcapFile)
        logging.debug(messages)
        self.assertTrue(len(messages) == 17)

    def test_importPCAPApplicativeLayerWithFilter(self):
        """Test (and illustrates) how to import messages
        out of a pcap prefiltered with BPF filter.

        """
        logging.debug("Test : Import messages from a PCAP with a specified BPF filter.")

        pcapFile = os.path.join("test", "resources", "pcaps", "botnet_irc_bot.pcap")
        messages = PCAPImporter.readFile(pcapFile, bpfFilter="tcp dst port 6667")
        logging.debug(messages)
        self.assertTrue(len(messages) == 8)

        messages = PCAPImporter.readFile(pcapFile, bpfFilter="tcp src port 6667")
        logging.debug(messages)
        self.assertTrue(len(messages) == 9)
