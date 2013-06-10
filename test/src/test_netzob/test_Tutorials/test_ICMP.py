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

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from common.NetzobTestCase import NetzobTestCase
from netzob import *


class test_ICMP(NetzobTestCase):

    def test_generateICMP(self):
        """test_generateICMP:
        """
        logging.debug("Test : generate some ICMP Echo Request.")

        # Build header : 3 fields
        pingHeader = [
            Field(name="Type"),
            Field(name="Code"),
            Field(name="Checksum")
        ]

        # Create a payload with a 1 single field
        pingPayload = [
            Field(name="Payload")
        ]

        # field 1 : type - 1 byte
        pingHeader[0].domain = Raw(size=8)

        # field 2 : code - 1 byte
        pingHeader[1].domain = Raw(size=8)

        # field 3 : checksum - 2 bytes
        pingHeader[2].domain = Raw(size=16)
        #pingHeader[2].domain = [Raw(CRC16(pingHeader + pingPayload), size=16)]

        # field 4 : we put an ascii of 50 chars in the payload
        pingPayload[0].domain = "hello"

        ping = Symbol(pingHeader + pingPayload)
        msg = ping.generate()

        logging.debug("MSG = '{0}'".format(repr(msg)))
