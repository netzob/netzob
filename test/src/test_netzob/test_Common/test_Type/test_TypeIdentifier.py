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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import unittest
import random
import base64

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.Format import Format
from common.NetzobTestCase import NetzobTestCase


class test_TypeIdentifier(NetzobTestCase):

    def test_getTypesNum(self):
        number = random.randint(0, 10000)
        typeIdentifier = TypeIdentifier()
        self.assertIn(Format.DECIMAL, typeIdentifier.getTypes(number))

    def test_getTypesAlpha(self):
        alphabet = list(map(chr, list(range(97, 123))))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        self.assertIn(Format.ALPHA, typeIdentifier.getTypes(alpha))

    def test_getTypesAscii(self):
        alphabet = list(map(chr, list(range(97, 123))))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        self.assertIn(Format.ASCII, typeIdentifier.getTypes(alpha))

    def test_getTypesBase64(self):
        string = "Vive Netzob !"
        base64String = base64.encodestring(string)
        typeIdentifier = TypeIdentifier()
        self.assertIn(Format.BASE64_ENC, typeIdentifier.getTypes(base64String))

    def test_getTypesBinary(self):
        alphabet = list(map(chr, list(range(97, 123))))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        hexOfNumber = str(hex(ord(alpha)))[2:]
        self.assertIn(Format.BINARY, typeIdentifier.getTypes(hexOfNumber))
