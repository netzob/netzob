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
from netzob.Common.MMSTD.Dictionary.VariableManagementToken import VariableManagementToken


class AbstractVariable:
    """AbstractVariable:
            An abstract variable defined in a dictionary.
    """

    def __init__(self, id, name):
        """Constructor of AbstractVariable:

                @type id: string
                @param id: a unique identifying string.
                @type name: string
                @param name: the name of the variable being constructed.
        """
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.AbstractVariable.py')
        self.id = id
        self.name = name
        self.mutable = True  # TODO: implement mutability.
        self.random = False  # TODO: implement randomness.

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

#+---------------------------------------------------------------------------+
#| Visitor functions                                                         |
#+---------------------------------------------------------------------------+
    def read(self, readingToken):
        """read:
                Grants a reading access to the variable. The value of readingToken is read bit by bit.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this reading access.
        """
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, readingToken)
                self.learn(self, readingToken)
                self.memorize(self, readingTokenreadingToken)

            else:
                # mutable and not defined
                self.learn(self, readingToken)
                self.memorize(self, readingToken)

        else:
            if self.defined:
                # not mutable and defined
                self.compare(self, readingToken)

            else:
                # not mutable and not defined
                readingToken.setOk(False)

    def write(self, writingToken):
        """write:
                Grants a writing access to the variable. A value is written according to encountered node variable rules. This value is stored in writingToken.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this writing access.
        """
        if self.mutable:
            if self.defined:
                # mutable and defined
                self.forget(self, writingToken)
                self.generate(self, writingToken)
                self.memorize(self, writingToken)
                valueToSend = self.getValue(self, writingToken)

            else:
                # mutable and not defined
                self.generate(self, writingToken)
                self.memorize(self, writingToken)
                valueToSend = self.getValue(self, writingToken)

        else:
            if self.defined:
                # not mutable and defined
                valueToSend = self.getValue(self, writingToken)

            else:
                # not mutable and not defined
                writingToken.setOk(False)

#+---------------------------------------------------------------------------+
#| Visitor abstract subFunctions                                             |
#+---------------------------------------------------------------------------+
    @abstractmethod
    def forget(self, processingToken):
        """forget:
                Removes the variable from the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'forget'."))

    @abstractmethod
    def memorize(self, processingToken):
        """memorize:
                Adds the variable to the memory cache.

                @type processingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.AbstractVariableProcessingToken.AbstractVariableProcessingToken
                @param processingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'memorize'."))

    @abstractmethod
    def learn(self, readingToken):
        """learn:
                Learns (starting at the "indice"-th character) value.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'learn'."))

    @abstractmethod
    def compare(self, readingToken):
        """compare:
                Compares (starting at the "indice"-th character) value to the current or a previously memorized value of variable.

                @type readingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableReadingToken.VariableReadingToken
                @param readingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'compare'."))

    @abstractmethod
    def generate(self, writingToken):
        """generate:
                Generates a value according to a given strategy and attribute it to the variable.

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'generate'."))

    @abstractmethod
    def getValue(self, writingToken):
        """getValue:

                @type writingToken: netzob.Common.MMSTD.Dictionary.VariableProcessingToken.VariableWritingToken.VariableWritingToken
                @param writingToken: a token which contains all critical information on this access.
        """
        raise NotImplementedError(_("The current variable does not implement 'getValueToSend'."))

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

    def setID(self, id):
        self.id = id

    def getName(self, name):
        self.name = name

    def setMutable(self, mutable):
        self.mutable = mutable

    def setRandom(self, random):
        self.random = random

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
            # Data Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DataVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.DataVariable import DataVariable
                return DataVariable.loadFromXML(xmlRoot, namespace, version, "IPv4")

            # Aggregate Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AggregateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable import AggregateVariable
                return AggregateVariable.loadFromXML(xmlRoot, namespace, version)

            # Alternate Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AlternateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.AlternateVariable import AlternateVariable
                return AlternateVariable.loadFromXML(xmlRoot, namespace, version)

            # Referenced Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ReferencedVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.ReferencedVariable import ReferencedVariable
                return ReferencedVariable.loadFromXML(xmlRoot, namespace, version)

            # Repeat Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:RepeatVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.RepeatVariable import RepeatVariable
                return RepeatVariable.loadFromXML(xmlRoot, namespace, version)
