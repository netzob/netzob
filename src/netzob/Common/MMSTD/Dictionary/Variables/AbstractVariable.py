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


class AbstractVariable:
    """AbstractVariable:
            An abstract variable defined in a dictionary.
    """

    def __init__(self, _id, name, mutable, random, node):
        """Constructor of AbstractVariable:

                @type _id: string
                @param _id: a unique identifying string.
                @type name: string
                @param name: the name of the variable being constructed.
                @type mutable: boolean
                @param mutable: tells if the variable can be modified or not.
                @type random: boolean
                @param random: tells if the variable has a fixed or a dynamic and randomly driven value.
                @type node: boolean
                @param node: tells if the variable is a node.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.py')
        self.id = _id
        self.name = name
        self.mutable = mutable
        self.random = random
        self.node = node

    def toString(self):
        """toString:
                For debugging purpose.
        """
        return _("Variable {0} (mutable: {1}, random: {2})").format(self.name, str(self.mutable), str(self.random))

    def findMotherNode(self, rootVariable):
        """findMotherNode:
                Find the node that is just above the variable in the global tree structure.
                Start the search of this node from a given root variable which is supposed to be an ancestor of the variable.
                May be recursive.

                @type rootVariable: netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.AbstractVariable
                @param rootVariable: a root ancestor of the being searched node.
        """
        # If the variable is the root of the tree.
        if self.getID() == rootVariable.getID():
            return None

        motherNode = None
        # We assume that variable IDs are unique.
        if rootVariable.isNode():
            if rootVariable.getChildren() is not None:
                for child in rootVariable.getChildren():
                    if self.getID() == child.getID():
                        # We find it
                        return rootVariable
                    else:
                        # It may be in a child's children.
                        node = self.findMotherNode(child)
                        if node is not None:
                            motherNode = node
        return motherNode

#+---------------------------------------------------------------------------+
#| abstract method                                                           |
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
    def isDefined(self):
        """isDefined:
                Tells if the variable is defined (i.e. has a value for a leaf, enough leaf have values for a node...)
        """
        raise NotImplementedError(_("The current variable does not implement 'isDefined'."))

    @abstractmethod
    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.

            @type root: lxml.etree.Element
            @param root: the root of the tree being built.
            @type namespace: string
            @param namespace: a namespace used as a precision in the variable tree.
        """
        raise NotImplementedError(_("The current variable does not implement 'toXML'."))

    @abstractmethod
    def restore(self, processingToken):
        """restore:
                Restore the variable on the memory cache from the real memory.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'recall'."))

    @abstractmethod
    def getDictOfValues(self, processingToken):
        """getDictOfValues:
                Return a dictionary which contains the variable id as key and the value as value of the variable is a leaf and a dictionary containing all couples variable id - value of the children if the variable is a node.

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
        raise NotImplementedError(_("The current variable does not implement 'read'."))

    @abstractmethod
    def write(self, writingToken):
        """write:
                Grants a writing access to the variable. A value is written according to encountered node variable rules. This value is stored in writingToken.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
        raise NotImplementedError(_("The current variable does not implement 'write'."))

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def isMutable(self):
        return self.mutable

    def isRandom(self):
        return self.random

    def isNode(self):
        return self.node

    def setID(self, _id):
        self.id = _id

    def setMutable(self, mutable):
        self.mutable = mutable

    def setRandom(self, random):
        self.random = random

    def setNode(self, node):
        self.node = node

#+---------------------------------------------------------------------------+
#| Static methods                                                            |
#+---------------------------------------------------------------------------+
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
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
                @return: a variable constructed from this XML definition.
        """
        if version == "0.1":
            logging.debug(_("[ AbstractVariable: loadFromXML:"))
            # Data Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DataVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
                return DataVariable.loadFromXML(xmlRoot, namespace, version)

            # Aggregate Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AggregateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
                return AggregateVariable.loadFromXML(xmlRoot, namespace, version)

            # Alternate Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AlternateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
                return AlternateVariable.loadFromXML(xmlRoot, namespace, version)

            # Referenced Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ReferencedVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable import ReferencedVariable
                return ReferencedVariable.loadFromXML(xmlRoot, namespace, version)

            # Repeat Variable
            elif xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:RepeatVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import RepeatVariable
                return RepeatVariable.loadFromXML(xmlRoot, namespace, version)

            else:
                logging.debug(_("xmlRoot.get(...) returns {0} which does not correspond to a true variable class.").format(xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract")))
            logging.debug(_("AbstractVariable: loadFromXML ]"))
        else:
            logging.debug(_("Version != 0.1"))
