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
import base64

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Type.TypeConvertor import TypeConvertor
from netzob.Common.Functions.TransformationFunction import TransformationFunction


#+---------------------------------------------------------------------------+
#| Base64Function:
#|     Definition of a base64 transformation function
#+---------------------------------------------------------------------------+
class Base64Function(TransformationFunction):

    TYPE = "FormatFunction"

    def __init__(self, name):
        TransformationFunction.__init__(self, Base64Function.TYPE, name)

    def apply(self, message):
        """apply:
        Decode in B64 the provided message"""
        result = message
        try:
            rawContent = TypeConvertor.netzobRawToPythonRaw(message)
            b64Content = base64.b64decode(rawContent)
            result = TypeConvertor.pythonRawToNetzobRaw(b64Content)
        except TypeError as error:
            logging.warning("Impossible to compute the base64 value of message (error={0})".format(str(error)))
            result = ""
        return result

    def reverse(self, message):
        """reverse:
        Encode in B64 the provided message"""
        result = message
        try:
            rawContent = TypeConvertor.netzobRawToPythonRaw(message)
            b64Content = base64.b64encode(rawContent)
            result = TypeConvertor.pythonRawToNetzobRaw(b64Content)
        except TypeError as error:
            logging.warning("Impossible to compute the base64 value of message (error={0})".format(str(error)))
            result = ""
        return result
