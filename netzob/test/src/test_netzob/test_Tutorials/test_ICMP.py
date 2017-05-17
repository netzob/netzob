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

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from common.NetzobTestCase import NetzobTestCase
from netzob.all import *


class test_ICMP(NetzobTestCase):

    def test_generateICMP(self):
        """test_generateICMP:
        """
        logging.debug("Test : generate some ICMP Echo Request.")

        # Build header : 3 fields
        pingHeader = Field(name="Header")

        pingHeaders = [
            Field(name="Type"),
            Field(name="Code"),
            Field(name="Checksum")
        ]
        pingHeader.children = pingHeaders
        pingHeader.domain.learnable = False

        # Create a payload with a 1 single field
        pingPayload = Field(name="Payload")

        # field 1 : type - 1 byte
        pingHeaders[0].domain = Raw(nbBytes=1)
        pingHeaders[0].domain.learnable = False

        # field 2 : code - 1 byte
        pingHeaders[1].domain = Raw(nbBytes=1)
        pingHeaders[1].domain.learnable = False

        # field 3 : checksum - 2 bytes
        pingHeaders[2].domain = [Raw(CRC16(pingHeader + pingPayload), size=16)]
        #pingHeaders[2].domain = Raw(nbBytes=2)
        pingHeaders[2].domain.learnable = False


        # field 4 : we put an ascii of 10 to 50 chars in the payload
        pingPayload.domain = ASCII(nbChars=(10, 50))
        pingPayload.domain.learnable = False

        ping = Symbol([pingHeader, pingPayload])

        ping.messages = [RawMessage(ping.specialize()) for i in range(0, 20)]
        cells = ping.getCells()
        print(cells)
