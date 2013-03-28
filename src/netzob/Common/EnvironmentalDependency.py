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
from gettext import gettext as _
from lxml.etree import ElementTree
from lxml import etree


#+---------------------------------------------------------------------------+
#| EnvironmentalDependency:
#|     Class definition of an environmental dependency
#+---------------------------------------------------------------------------+
class EnvironmentalDependency(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, name, aType, value):
        self.name = name
        self.type = aType
        self.value = value

    def save(self, root, namespace):
        environmental_dependency = etree.SubElement(root, "{" + namespace + "}environmental_dependency")
        environmental_dependency.set("name", str(self.name))
        environmental_dependency.set("type", str(self.type))
        environmental_dependency.text = str(self.value)

    #+-----------------------------------------------------------------------+
    #| GETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getValue(self):
        return self.value

    #+-----------------------------------------------------------------------+
    #| SETTERS
    #+-----------------------------------------------------------------------+
    def setName(self, name):
        self.name = name

    def setType(self, type):
        self.type = type

    def setValue(self, value):
        self.value = value
