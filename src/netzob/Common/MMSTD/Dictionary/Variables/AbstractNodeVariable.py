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
import logging
import random

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variables.AbstractVariable import AbstractVariable


class AbstractNodeVariable(AbstractVariable):
    """AbstractNodeVariable:
            An abstract variable defined in a dictionary which is a node (alternate, aggregate...) in the global variable tree.
    """

    def __init__(self, id, name, mutable, random, children=None):
        """Constructor of AbstractNodeVariable:

                @type children: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable List
                @param children: the list of this variable's children.
        """
        AbstractVariable.__init__(self, id, name, mutable, random, True)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractNodeVariable.py')
        self.children = []
        if children is not None:
            self.children.extend(children)

    def removeChildByID(self, child):
        """removeVariable:
                Remove a variable having the same idea as child.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the variable that is being removed.
        """
        if self.children is not None:
            for son in self.children:
                if son.getID() == child.getID():
                    # We edit the element.
                    self.removeChild(son)
                    break

    def editChildByID(self, child):
        """editVariable:
                Edit a variable having the same idea as child.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the variable that is being edited.
        """
        if self.children is not None:
            for son in self.children:
                if son.getID() == child.getID():
                    # We edit the element.
                    self.removeChild(son)
                    self.addChild(child)
                    break

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getChildren(self):
        if self.isRandom():
            if self.children is not None:
                random.shuffle(self.children)
        return self.children

    def addChild(self, child):
        if self.children is not None:
            self.children.append(child)

    def removeChild(self, child):
        if self.children is not None:
            self.children.remove(child)
