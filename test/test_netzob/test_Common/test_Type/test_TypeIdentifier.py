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
import base64

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeIdentifier import TypeIdentifier
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Type.Format import Format


class test_TypeIdentifier(unittest.TestCase):
    
    def test_getTypesNum(self):        
        number = random.randint(0, 10000)
        typeIdentifier = TypeIdentifier()
        hexOfNumber = str(hex(number))[2:]
        self.assertIn(Format.DECIMAL, typeIdentifier.getTypes(hexOfNumber))
    
    def test_getTypesAlpha(self):    
        alphabet = map(chr, range(97, 123))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        hexOfNumber = str(hex(ord(alpha)))[2:]
        self.assertIn(Format.ALPHA, typeIdentifier.getTypes(hexOfNumber))
        
    def test_getTypesAscii(self):    
        alphabet = map(chr, range(97, 123))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        hexOfNumber = str(hex(ord(alpha)))[2:]
        self.assertIn(Format.ASCII, typeIdentifier.getTypes(hexOfNumber))
        
    def test_getTypesBase64(self):    
        string = "Vive Netzob !"
        base64String = base64.encodestring(string)
        hexBase64String = TypeConvertor.stringToNetzobRaw(base64String)
        typeIdentifier = TypeIdentifier()
        self.assertIn(Format.BASE64_ENC, typeIdentifier.getTypes(hexBase64String))
        
    def test_getTypesBinary(self):    
        alphabet = map(chr, range(97, 123))
        alpha = alphabet[random.randint(0, len(alphabet) - 1)]
        typeIdentifier = TypeIdentifier()
        hexOfNumber = str(hex(ord(alpha)))[2:]
        self.assertIn(Format.BINARY, typeIdentifier.getTypes(hexOfNumber))
        
        # Alphanum
        
        # ASCII
        
        # Base64
        
        # Binary
        
        
#        
#        
#        if aggregatedValues.isdigit():
#            typesList.append("num")
#        if aggregatedValues.isalpha():
#            typesList.append("alpha")
#        if aggregatedValues.isalnum():
#            typesList.append("alphanum")
#        if self.isAscii(aggregatedValues):
#            typesList.append("ascii")
#        if self.isBase64(stringsTable):
#            typesList.append("base64enc")
#            typesList.append("base64dec")
#        typesList.append("binary")
#        
##        
#        
#    def test_isAscii(self, string):
#        pass
#    def isBase64(self, stringsTable):
#        pass
