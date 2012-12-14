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
import uuid

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob.Common.Functions.RenderingFunction import RenderingFunction


#+---------------------------------------------------------------------------+
#| TransformationFunction :
#|     Class definition of a function for transformation purposes (b64, rot13, ...)
#+---------------------------------------------------------------------------+
class TransformationFunction(RenderingFunction):

    TYPE = "TransformationFunction"

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, type, name):
        RenderingFunction.__init__(self, TransformationFunction.TYPE)
        self.type = type
        self.name = name

    #+-----------------------------------------------------------------------+
    #| apply
    #|     Abstract method to apply the function on a provided message
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def apply(self, message):
        """apply:
        Apply the function on the provided message"""

        self.log.error("The function class (" + self.getType() + ") doesn't define 'apply' !")
        raise NotImplementedError("The function class (" + self.getType() + ") doesn't define 'apply' !")

    #+-----------------------------------------------------------------------+
    #| reverse
    #|     Abstract method to reverse the function on a provided message (
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def reverse(self, message):
        """reverse:
        Apply the reverse function on the provided message"""

        self.log.error("The function class (" + self.getType() + ") doesn't define 'reverse' !")
        raise NotImplementedError("The function class (" + self.getType() + ") doesn't define 'reverse' !")

    def save(self, root, namespace_common):
        """Save under the provided XML root the current transformation function"""
        self.log.error("The function class ({0}) doesn't define the 'save' method !".format(self.getType()))
        raise NotImplemented("The function class ({0}) doesn't define the 'save' method !".format(self.getType()))

    #+-----------------------------------------------------------------------+
    #| getConversionAddressingTable
    #|     Retrieve a table which describes the conversion addressing
    #+-----------------------------------------------------------------------+
    def getConversionAddressingTable(self, message):
        return None

    #+-----------------------------------------------------------------------+
    #| Getter & Setters
    #+-----------------------------------------------------------------------+
    def getType(self):
        return self.type

    def getName(self):
        return self.name

    def setType(self, type):
        self.type = type

    def setName(self, name):
        self.name = name
