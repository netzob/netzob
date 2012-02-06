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
from netzob.Common.Type.Format import Format

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

class TypeIdentifier():
    
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.TypeIdentifier.py')
    
    #+---------------------------------------------- 
    #| Identify the possible types from a hexa string
    #+----------------------------------------------
    def getTypes(self, stringsTable):
        entireString = "".join(stringsTable)
        
        setSpace = set()
        for i in range(0, len(entireString), 2):
            setSpace.add(int(entireString[i:i + 2], 16))
        sorted(setSpace)

        aggregatedValues = ""
        for i in setSpace:
            aggregatedValues += chr(i)

        typesList = []
        if aggregatedValues == "":
            return typesList
        if aggregatedValues.isdigit():
            typesList.append(Format.DECIMAL)
        if aggregatedValues.isalpha():
            typesList.append(Format.ALPHA)
        if aggregatedValues.isalnum():
            typesList.append(Format.ALPHA_NUM)
        if self.isAscii(aggregatedValues):
            typesList.append(Format.ASCII)
        if self.isBase64(stringsTable):
            typesList.append(Format.BASE64_ENC)
            typesList.append(Format.BASE64_DEC)
        typesList.append(Format.BINARY)

        return typesList
    
    #+---------------------------------------------- 
    #| Return True if the string parameter is ASCII
    #+----------------------------------------------
    def isAscii(self, string):
        try:
            string.decode('ascii')
            return True
        except UnicodeDecodeError:
            return False 

    #+---------------------------------------------- 
    #| Return True if the string table parameter is base64
    #|  encoded
    #+----------------------------------------------
    def isBase64(self, stringsTable):
        res = True
        try:
            for string in stringsTable:
                s = ""
                for i in range(0, len(string), 2):
                    s += chr(int(string[i:i + 2], 16))
                tmp = base64.b64decode(s)
                if tmp == "":
                    res = False
        except TypeError:
            res = False

        return res    
