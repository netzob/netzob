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
from abc import abstractmethod
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class AbstractVariable(object):
    """AbstractVariable:
            An abstract variable defined in a dictionary.
    """

    def __init__(self, _id, name, mutable, learnable, node):
        """Constructor of AbstractVariable:

                @type _id: string
                @param _id: a unique identifying string.
                @type name: string
                @param name: the name of the variable being constructed.
                @type mutable: boolean
                @param mutable: tells if the variable can be modified or not.
                @type learnable: boolean
                @param learnable: tells if the variable can learned a value, initialized itself or not.
                @type node: boolean
                @param node: tells if the variable is a node.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.py')
        self.id = _id
        self.name = name
        self.mutable = mutable
        self.learnable = learnable
        self.node = node
        self.fathers = []  # The variables just above the current variable in the tree representation.
        self.boundedVariables = []  # A list containing all variables which value is bind to the value of this variable.
        self.tokenChoppedIndexes = []  # An integer list which contain the index of each segment this variable is responsible for (they have been created from its value)
        self.currentValue = None  # The value we see from the current variable if we flatten the subtree which starts here.

    def toString(self):
        """toString:
                For debugging purpose.
        """
        return "Variable {0} ({3}) (mutable: {1}, learnable: {2})".format(self.name, str(self.mutable), str(self.learnable), self.id)

    def getProgeny(self):
        """getProgeny:
                Get this variable and all variable that descends from it. (i.e. son, grandson...). Return EVERY child variable, especially for alternate variable.
                Overwritten for AbstractNodeVariable.

                @rtype: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable List
                @return: a list of the whole progeny plus this variable.
        """
        progeny = []
        progeny.append(self)
        return progeny

    def notifyBoundedVariables(self, access, processingToken, value=None):
        """notifyBoundedVariables:
                Notify every variable that are bounded to the current variable with a set of segment of the read value.
                This set leads to no repetition in the final read value.

                @type access: integer list
                @param access: the list of chopped segments that have been modified before this notification.
                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
                @type value: bitarray
                @param value: the value of the notifying variable.
        """
        if access == "read":
            for bound in self.boundedVariables:
                bound.notifiedRead(processingToken, value)

        if access == "write":
            for bound in self.boundedVariables:
                bound.notifiedWrite(processingToken)

#+---------------------------------------------------------------------------+
#| Abstract methods                                                          |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def getVariableType(self):
        """getVariableType:
                Return the type of a variable.
        """
        raise NotImplementedError("The current variable doesn't support 'getType'.")

    @abstractmethod
    def getDescription(self, processingToken):
        """getDescription:
                Get the full description of the variable.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
                @rtype: string
                @return: the full description of the variable.
        """
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    @abstractmethod
    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).

                @rtype: string
                @return: the uncontextualized description of the variable.
        """
        raise NotImplementedError("The current variable doesn't support 'getUncontextualizedDescription'.")

    @abstractmethod
    def isDefined(self, processingToken):
        """isDefined:
                Tells if the variable is defined (i.e. has a value for a leaf, enough leaf have values for a node...)

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
                @rtype: boolean
                @return: True if the variable is defined.
        """
        raise NotImplementedError("The current variable does not implement 'isDefined'.")

    @abstractmethod
    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.

            @type root: lxml.etree.Element
            @param root: the root of the tree being built.
            @type namespace: string
            @param namespace: a namespace used as a precision in the variable tree.
        """
        raise NotImplementedError("The current variable does not implement 'toXML'.")

    @abstractmethod
    def restore(self, processingToken):
        """restore:
                Restore the variable on the memory cache from the real memory.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError("The current variable does not implement 'restore'.")

    @abstractmethod
    def getDictOfValues(self, processingToken):
        """getDictOfValues:
                Return a dictionary which contains the variable id as key and the value as value if the variable is a leaf and a dictionary containing all couples variable id - value of the children if the variable is a node.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
                @rtype: String*bitarray dict
                @return: a dictionary containing ids of variable and values in a bitarray format.
        """
        raise NotImplementedError("The current variable doesn't support 'getDictOfValues'.")

#+---------------------------------------------------------------------------+
#| Visitor abstract method                                                   |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def read(self, readingToken):
        """read:
                Grants a reading access to the variable. The value of readingToken is read bit by bit.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this reading access.
        """
        raise NotImplementedError("The current variable does not implement 'read'.")

    @abstractmethod
    def write(self, writingToken):
        """write:
                Grants a writing access to the variable. A value is written according to encountered node variable rules. This value is stored in writingToken.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
        raise NotImplementedError("The current variable does not implement 'write'.")

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def isMutable(self):
        return self.mutable

    def isLearnable(self):
        return self.learnable

    def isNode(self):
        return self.node

    def getFathers(self):
        return self.fathers

    def getBoundedVariables(self):
        return self.boundedVariables

    def getCurrentValue(self):
        return self.currentValue

    def setID(self, _id):
        self.id = _id

    def setMutable(self, mutable):
        self.mutable = mutable

    def setLearnable(self, learnable):
        self.learnable = learnable

    def setNode(self, node):
        self.node = node

    def addFather(self, father):
        self.fathers.append(father)

    def removeFather(self, father):
        self.fathers.remove(father)

    def bindVariable(self, variable):
        self.boundedVariables.append(variable)

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version, symbol):
        """loadFromXML:
                Load a variable from an XML definition.
                Calls its proper heir function for it to create the variable.

                @type xmlRoot: lxml.etree.Element
                @param xmlRoot: the root of the XML definition.
                @type namespace: string
                @param namespace: the namespace (precision) associated to the variable in the XML definition.
                @type version: string
                @param version: the load version.
                @rtype: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @type symbol: netzob.Common.Symbol
                @param symbol: the symbol in which the current variable is placed, used by relation variable.
                @return: a variable constructed from this XML definition.
        """
        if version == "0.1":
            logging.debug("[ AbstractVariable: loadFromXML:")
            # Data Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DataVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
                return DataVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            # Aggregate Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AggregateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
                return AggregateVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            # Alternate Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AlternateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
                return AlternateVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            # Repeat Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:RepeatVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import RepeatVariable
                return RepeatVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            # Direct Relation Variable
            #elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DirectRelationVariable":
            #    from netzob.Common.MMSTD.Dictionary.Variables.DirectRelationVariable import DirectRelationVariable
            #    return DirectRelationVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            # Computed Relation Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ComputedRelationVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.ComputedRelationVariable import ComputedRelationVariable
                return ComputedRelationVariable.loadFromXML(xmlRoot, namespace, version, symbol)

            else:
                logging.debug("xmlRoot.get(...) returns {0} which does not correspond to a true variable class.").format(xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract"))
            logging.debug("AbstractVariable: loadFromXML ]")
        else:
            logging.debug("Version != 0.1")
