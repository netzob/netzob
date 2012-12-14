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
import base64
import logging
import StringIO
import re

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.Format import Format


class TypeIdentifier():

    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Type.TypeIdentifier.py')

    #+----------------------------------------------
    #| Identify the possible types from a hexa string
    #+----------------------------------------------
    def getTypes(self, val):
        val = str(val)
        typesList = []
        if val == "":
            return typesList
        if val.isdigit():
            typesList.append(Format.DECIMAL)
        if val.isalpha():
            typesList.append(Format.ALPHA)
        if val.isalnum():
            typesList.append(Format.ALPHA_NUM)
        if self.isAscii(val):
            typesList.append(Format.ASCII)
        if self.isBase64(val):
            typesList.append(Format.BASE64_ENC)
            typesList.append(Format.BASE64_DEC)
        typesList.append(Format.BINARY)

        return typesList

    #+----------------------------------------------
    #| Return True if the string parameter is ASCII
    #+----------------------------------------------
    def isAscii(self, val):
        try:
            val.decode('ascii')
            return True
        except UnicodeDecodeError:
            return False

    #+----------------------------------------------
    #| Return True if the string table parameter is base64
    #|  encoded
    #+----------------------------------------------
    def isBase64(self, val):
        res = True
        try:
            tmp = base64.b64decode(val)
            if tmp == "":
                res = False
        except TypeError:
            res = False
        return res

    #+----------------------------------------------
    #| Return True if the string is an hexstring '1234abcd'
    #|  encoded
    #+----------------------------------------------
    def isHexString(self, val):
        if re.match("[0-9a-f]*", val) is not None:
            return True
        else:
            return False
