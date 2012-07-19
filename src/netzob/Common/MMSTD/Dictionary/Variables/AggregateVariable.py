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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from bitarray import bitarray
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable.AbstractNodeVariable import AbstractNodeVariable


class AggregateVariable(AbstractNodeVariable):
    """AggregateVariable:
            A data variable defined in a dictionary which is a logical and of several variables.
    """

    def __init__(self, id, name, children=None):
        """Constructor of AggregateVariable:

                @type children: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable List
                @param children: the list of this variable's children.
        """
        AbstractNodeVariable.__init__(self, id, name, children)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AggregateVariable.py')

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def learn(self, readingToken):
        self.log.debug(_("Variable {0} learn {1} (if their format are compatible) starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        toBeRestored = []
        for child in self.children:
            child.learn(readingToken)
            toBeRestored.append(child)
            if not readingToken.isOk():
                break
        # If it has failed we restore every executed children
        if not readingToken.isOk():
            for child in toBeRestored:
                child.restore(readingToken)

    def compare(self, readingToken):
        self.log.debug(_("Variable {0} compare its current value to {1} starting at {2}.").format(self.getName(), str(readingToken.getValue()), str(readingToken.getIndex())))
        for child in self.children:
            child.compare(readingToken)

    def getValue(self, writingToken):
        self.log.debug(_("Variable {0} get its value.").format(self.getName()))
        value = bitarray()
        for child in self.children:
            value += child.getValue(writingToken)
        writingToken.setValue(value)
