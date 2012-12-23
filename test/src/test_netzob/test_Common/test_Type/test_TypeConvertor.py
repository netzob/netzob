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
import unittest
import random
import string
import uuid
import time
from bitarray import bitarray

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Models.RawMessage import RawMessage
from netzob.Common.Symbol import Symbol
from common.NetzobTestCase import NetzobTestCase


class test_TypeConvertor(NetzobTestCase):

    def generateRandomString(self, min_len, max_len):
        return ''.join((random.choice(string.letters + string.digits) for _ in xrange(random.randint(min_len, max_len))))

    def test_serializeValues(self):
        # Generate randoms values and retrieve their
        # serializations
        nb_test = 100
        for i_test in range(0, nb_test):
            values = []

            nb_values = random.randint(5, 200)
            for i_value in range(0, nb_values):
                # Generate the content of a random value
                value = TypeConvertor.stringToNetzobRaw(self.generateRandomString(5, 100))
                values.append(value)

            # start the serialization process
            (serializedValues, format) = TypeConvertor.serializeValues(values, 8)

            # start the deserialisation process
            deserializedValues = TypeConvertor.deserializeValues(serializedValues, format)

            for i_value in range(0, len(values)):
                value = values[i_value]
                self.assertEqual(value, deserializedValues[i_value])

    def test_pythonRaw2bitarray(self):
        value = TypeConvertor.pythonRaw2bitarray("\xab\xcd")
        self.assertEqual(value, bitarray('1010101111001101'))

    def test_bitarray2pythonRaw(self):
        value = TypeConvertor.bitarray2pythonRaw(bitarray('1010101111001101'))
        self.assertEqual(value, '\xab\xcd')

    def test_str2bool(self):
        value = TypeConvertor.str2bool("true")
        self.assertEqual(value, True)

    def test_bool2str(self):
        value = TypeConvertor.bool2str(True)
        self.assertEqual(value, 'true')

    def test_bitarray2StrBitarray(self):
        value = TypeConvertor.bitarray2StrBitarray(bitarray('1010101111001101'))
        self.assertEqual(value, '1010101111001101')

    def test_strBitarray2Bitarray(self):
        value = TypeConvertor.strBitarray2Bitarray('1010101111001101')
        self.assertEqual(value, bitarray('1010101111001101'))

    def test_bitarray2strHex(self):
        value = TypeConvertor.bitarray2strHex(bitarray('1010101111001101'))
        self.assertEqual(value, '0xabcd')

    def test_int2bitarray(self):
        value = TypeConvertor.int2bitarray(4242, 16)
        self.assertEqual(value, bitarray('0001000010010010'))

    def test_bitarray2int(self):
        value = TypeConvertor.bitarray2int(bitarray('0001000010010010'))
        self.assertEqual(value, 4242)

    def test_netzobRaw2bitarray(self):
        value = TypeConvertor.netzobRaw2bitarray("abcd")
        self.assertEqual(value, bitarray('1010101111001101'))

    def test_bitarray2NetzobRaw(self):
        value = TypeConvertor.bitarray2NetzobRaw(bitarray('1010101111001101'))
        self.assertEqual(value, 'abcd')
