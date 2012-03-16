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


#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Automata:
#|     Abstract class which describes an automata (of a grammar) like an MMSTD
#+---------------------------------------------------------------------------+
class Automata(object):

    MMSTD_TYPE = "mmstd"

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, type):
        self.type = type

    #+-----------------------------------------------------------------------+
    #| Getters & Setters
    #+-----------------------------------------------------------------------+
    def getType(self):
        return self.type

    #+-----------------------------------------------------------------------+
    #| Save & Load
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        self.log.error("Error, the current automata (declared as " + self.type + ") doesn't support function save")
        raise NotImplementedError("Error, the current automata (declared as " + self.type + ") doesn't support function save")

    @staticmethod
    def loadFromXML(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            automata_type = xmlRoot.get("type")
            from netzob.Common.MMSTD.MMSTD import MMSTD
            if automata_type == MMSTD.TYPE:
                automata = MMSTD.loadFromXML(xmlRoot, vocabulary, namespace, version)
                return automata
            else:
                logging.warn("The provided type of automata (" + automata_type + ") cannot be parsed.")
        return None
