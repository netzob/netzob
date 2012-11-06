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
from gettext import gettext as _
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

    def __init__(self, _id, name, mutable, random, children=None):
        """Constructor of AbstractNodeVariable:

                @type children: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable List
                @param children: the list of this variable's children.
        """
        AbstractVariable.__init__(self, _id, name, mutable, random, True)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractNodeVariable.py')
        self.children = []
        if children is not None:
            self.children.extend(children)
        self.learning = False  # (read access with mutable flag) Tells if the variable reads normally or through an attempt of learning.

    def moveChild(self, child, position):
        """removeVariable:
                move child to a given position

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the variable that is being moved.
                @type position: integer
                @param position: the position where the child is being moved.
        """
        if position < 0 or position > len(self.children):
            self.log.info("Wrong position given, nothing is done: the position {0} is without the boundaries [0, {1}]".format(str(position), str(len(self.children))))
        else:
            self.removeChild(child)
            self.insertChild(position, child)

    def removeChildByID(self, child):
        """removeVariable:
                Remove a variable having the same id as child. It can be a clone of child.

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
                Edit a variable having the same id as child. It can be a previous version of child.

                @type child: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param child: the variable that is being edited.
        """
        if self.children is not None:
            for son in self.children:
                if son.getID() == child.getID():
                    # We edit the element.
                    self.insertChild(self.indexOfChild(son), child)
                    self.removeChild(son)
                    break

    def shuffleChildren(self):
        """shuffleChildren:
                Randomly sort children of the variable.
        """
        self.log.debug("-  {0}: shuffleChildren.".format(self.toString()))
        if self.getChildren() is not None:
            random.shuffle(self.getChildren())

#+---------------------------------------------------------------------------+
#| Functions inherited from AbstractVariable                                 |
#+---------------------------------------------------------------------------+
    def getDescription(self, processingToken):
        """getDescription:
        """
        values = []
        for child in self.children:
            values.append(child.getDescription(processingToken))
        return "[ {0}, children:\n".format(self.toString()) + "\n".join(values) + " ]"

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
        """
        values = []
        for child in self.children:
            values.append(child.getUncontextualizedDescription())
        return "[ {0}, children:\n".format(self.toString()) + "\n".join(values) + " ]"

    def restore(self, processingToken):
        """restore:
                Restore all children on the memory cache.
        """
        self.log.debug("[ {0}: children's memorized value are restored.".format(self.toString()))
        for child in self.children:
            child.restore(processingToken)
        self.log.debug("Variable {0}: ]".format(self.getName()))

    def getDictOfValues(self, processingToken):
        """getDictOfValues
                We concatenate every dictOfValues of each child.
        """
        dictOfValues = dict()
        # self.log.debug("[ Dict of values:")
        for child in self.children:
            dictOfValue = child.getDictOfValues(processingToken)
            for key, val in dictOfValue.iteritems():
                dictOfValues[key] = val
        # self.log.debug(" Dict of values: {0} ]".format(str(dictOfValues)))
        return dictOfValues

    def getProgeny(self):
        """getProgeny:
                Get this variable and all variable that descends from it. (i.e. son, grandson...)
        """
        progeny = []
        progeny.append(self)
        if self.children is not None:
            for child in self.children:
                progeny.extend(child.getProgeny())
        return progeny

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getChildren(self):
        return self.children

    def isLearning(self):
        return self.isLearning()

    def setLearning(self, learning):
        self.learning = learning

#+---------------------------------------------------------------------------+
#| Implementation of list functions                                          |
#+---------------------------------------------------------------------------+
    def addChild(self, child):
        if self.children is not None:
            self.children.append(child)
            child.addFather(self)

    def removeChild(self, child):
        if self.children is not None:
            self.children.remove(child)
            child.removeFather(self)

    def insertChild(self, i, child):
        if self.children is not None:
            self.children.insert(i, child)
            child.addFather(self)

    def indexOfChild(self, child):
        if self.children is not None:
            return self.children.index(child)
        else:
            return None
