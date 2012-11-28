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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class Variable():
    """Variable:
            Definition of a variable defined in a dictionary
    """

    def __init__(self, typeVariable, idVar, name):
        """Constructor of Variable:

                @type typeVariable: string
                @param typeVariable: the type of the variable being constructed.
                @type idVar: string
                @param idvar: a unique identifying string.
                @type name: string
                @param name: the name of the variable being constructed.
        """
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.py')
        self.idVar = idVar
        self.name = name
        self.typeVariable = typeVariable

    def isMutable(self):
        return True

    def getValue(self, negative, vocabulary, memory):
        """getValue:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one else its NONE.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: (bitarray.bitarray, string)
                @return: the current or memorized value of the variable in both bitarray and string format.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getValue")
        raise NotImplementedError("The current variable doesn't support 'getValue'.")

    def getValueToSend(self, negative, vocabulary, memory):
        """getValueToSend:
                Get the current value of the variable it can be the original value if its set and not forget or the value in memory if it has one or it generates one and save its value in memory.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: (bitarray.bitarray, string)
                @return: the current, memorized value or a generated value of the variable in both bitarray and string format.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function send")
        raise NotImplementedError("The current variable doesn't support 'send'.")

    def getDescription(self, negative, vocabulary, memory):
        """getDescription:
                Get the full description of the variable.

                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: string
                @return: the full description of the variable.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    def getUncontextualizedDescription(self):
        """getUncontextualizedDescription:
                Get the uncontextualized description of the variable (no use of memory or vocabulary).

                @rtype: string
                @return: the uncontextualized description of the variable.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    def compare(self, value, indice, negative, vocabulary, memory):
        """compare:
                Compare the current variable to the end (starting at the "indice"-th character) of value.

                @type value: bitarray.bitarray
                @param value: a bit array a subarray of which we compare to the current variable binray value.
                @type indice: integer
                @param indice: the starting point of comparison in value.
                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: integer
                @return: the number of letters that matches, -1 if it does not match.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function compare")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function compare")

    def learn(self, value, indice, negative, vocabulary, memory):
        """learn:
                Compare the current variable to the end (starting at the "indice"-th character) of value.
                Moreover it stores learns from the provided message.

                @type value: bitarray.bitarray
                @param value: a bit array a subarray of which we compare to the current variable binray value.
                @type indice: integer
                @param indice: the starting point of comparison in value.
                @type negative: boolean
                @param negative: tells if we use the variable or a logical not of it.
                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
                @rtype: integer
                @return: the number of letters that matches, -1 if it does not match.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function learn")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function learn")

    def restore(self, vocabulary, memory):
        """restore:
                Restore learned value from the last execution of the variable.

                @type vocabulary: netzob.Common.Vocabulary.Vocabulary
                @param vocabulary: the vocabulary of the current project.
                @type memory: netzob.Common.MMSTD.Memory.Memory
                @param memory: a memory which can contain a former value of the variable.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function restore")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function restore")

    def toXML(self, root, namespace):
        """toXML:
            Create the xml tree associated to this variable.

            @type root: lxml.etree.Element
            @param root: the root of the tree being built.
            @type namespace: string
            @param namespace: a namespace used as a precision in the variable tree.
        """
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function save")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function save")

#+---------------------------------------------------------------------------+
#| Getters and setters                                                       |
#+---------------------------------------------------------------------------+
    def getID(self):
        return self.idVar

    def getName(self):
        return self.name

    def getTypeVariable(self):
        return self.typeVariable

    def setID(self, idVar):
        self.idVar = idVar

    def setName(self, name):
        self.name = name

    def setTypeVariable(self, typeVariable):
        self.typeVariable = typeVariable

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
                @param version: the version of the load needed.
                @rtype: netzob.Common.MMSTD.Dictionary.Variable.Variable
                @return: a variable constructed from this XML definition.
        """
        if version == "0.1":
            # IPv4 Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:IPv4Variable":
                from netzob.Common.MMSTD.Dictionary.Variables._IPv4Variable import IPv4Variable
                return IPv4Variable.loadFromXML(xmlRoot, namespace, version)

            # Word Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:WordVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._WordVariable import WordVariable
                return WordVariable.loadFromXML(xmlRoot, namespace, version)

            # DecimalWord Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DecimalWordVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._DecimalWordVariable import DecimalWordVariable
                return DecimalWordVariable.loadFromXML(xmlRoot, namespace, version)

            # Binary Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:BinaryVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._BinaryVariable import BinaryVariable
                return BinaryVariable.loadFromXML(xmlRoot, namespace, version)

            # Hex Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:HexVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._HexVariable import HexVariable
                return HexVariable.loadFromXML(xmlRoot, namespace, version)

            # Aggregate Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AggregateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._AggregateVariable import AggregateVariable
                return AggregateVariable.loadFromXML(xmlRoot, namespace, version)

            # Alternate Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:AlternateVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._AlternateVariable import AlternateVariable
                return AlternateVariable.loadFromXML(xmlRoot, namespace, version)

            # Referenced Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:ReferencedVariable":
                from netzob.Common.MMSTD.Dictionary.Variables._ReferencedVariable import ReferencedVariable
                return ReferencedVariable.loadFromXML(xmlRoot, namespace, version)
