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
import bz2

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Functions.TransformationFunction import TransformationFunction


#+---------------------------------------------------------------------------+
#| BZ2Function:
#|     Definition of a BZ2 transformation function
#+---------------------------------------------------------------------------+
class BZ2Function(TransformationFunction):

    TYPE = "BZ2Function"

    def __init__(self, name):
        TransformationFunction.__init__(self, BZ2Function.TYPE, name)

    def apply(self, message):
        """apply:
        This decompress the provided message in bz2"""
        result = message
        rawData = TypeConvertor.netzobRawToPythonRaw(message)
        try:
            rawResult = bz2.decompress(rawData)
            result = TypeConvertor.pythonRawToNetzobRaw(rawResult)
        except Exception as e:
            logging.info("Impossible to apply BZ2 function (decompress) on provided message (error= {0})".format(str(e)))
            result = ""
        return result

    def reverse(self, message):
        """reverse:
        This compress the provided message in bz2 format"""
        result = message
        rawData = TypeConvertor.netzobRawToPythonRaw(message)
        try:
            rawResult = bz2.compress(rawData)
            result = TypeConvertor.pythonRawToNetzobRaw(rawResult)
        except Exception as e:
            logging.info("Impossible to reverse BZ2 function (compress) on provided message (error= {0})".format(str(e)))
            result = ""
        return result
