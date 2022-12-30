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
import binascii


class test_ManualFieldStatic(NetzobTestCase):

    def test_analyze(self):
        logging.info("Test : manual slicing of a field")

        # Step1 : import messages from PCAP
        samples = ["00ff1f000000", "00fe1f000000", "00fe1f000000", "00fe1f000000", "00ff1f000000", "00ff1f000000", "00ff0f000000", "00fe2f000000"]
        # Create a message for each data ...
        messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]

        # ... and attach them to a unique symbol
        symbol = Symbol(messages=messages)

        # lets consider this as hexastring
        symbol.encodingFunctions.add(TypeEncodingFunction(HexaString))

        # display symbol (and so its messages)
        logging.info(symbol)
        # 00ff1f000000
        # 00fe1f000000
        # 00fe1f000000
        # 00fe1f000000
        # 00ff1f000000
        # 00ff1f000000
        # 00ff0f000000
        # 00fe2f000000

        Format.splitStatic(symbol, unitSize=UnitSize.SIZE_8, mergeAdjacentStaticFields=False, mergeAdjacentDynamicFields=False)
        logging.info(symbol)
        # 00 | ff | 1f | 00 | 00 | 00
        # 00 | fe | 1f | 00 | 00 | 00
        # 00 | fe | 1f | 00 | 00 | 00
        # 00 | fe | 1f | 00 | 00 | 00
        # 00 | ff | 1f | 00 | 00 | 00
        # 00 | ff | 1f | 00 | 00 | 00
        # 00 | ff | 0f | 00 | 00 | 00
        # 00 | fe | 2f | 00 | 00 | 00

        Format.mergeFields(symbol.children[1], symbol.children[2])
        logging.info(symbol)
        # 00 | ff1f | 00 | 00 | 00
        # 00 | fe1f | 00 | 00 | 00
        # 00 | fe1f | 00 | 00 | 00
        # 00 | fe1f | 00 | 00 | 00
        # 00 | ff1f | 00 | 00 | 00
        # 00 | ff1f | 00 | 00 | 00
        # 00 | ff0f | 00 | 00 | 00
        # 00 | fe2f | 00 | 00 | 00

        Format.mergeFields(symbol.children[2], symbol.children[3])
        logging.info(symbol)
        # 00 | ff1f | 0000 | 00
        # 00 | fe1f | 0000 | 00
        # 00 | fe1f | 0000 | 00
        # 00 | fe1f | 0000 | 00
        # 00 | ff1f | 0000 | 00
        # 00 | ff1f | 0000 | 00
        # 00 | ff0f | 0000 | 00
        # 00 | fe2f | 0000 | 00

        logging.info(symbol._str_debug())
