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
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Variable:
#|     Definition of a variable defined in a dictionary
#+---------------------------------------------------------------------------+
class Variable():

    def __init__(self, typeVariable, idVar, name):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.py')
        self.idVar = idVar
        self.name = name
        self.typeVariable = typeVariable

    def isMutable(self):
        return True

    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getValue")
        raise NotImplementedError("The current variable doesn't support 'getValue'.")

    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function send")
        raise NotImplementedError("The current variable doesn't support 'send'.")

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+
    def getUncontextualizedDescription(self):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function compare")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function compare")

    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function learn")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function learn")

    #+-----------------------------------------------------------------------+
    #| restore :
    #|     Restore learnt value from the last execution of the variable
    #+-----------------------------------------------------------------------+
    def restore(self, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function restore")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function restore")

    #+-----------------------------------------------------------------------+
    #| toXML
    #|     Returns the XML description of the variable
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function save")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function save")

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
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

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            # IPv4 Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:IPv4Variable":
                from netzob.Common.MMSTD.Dictionary.Variables.IPv4Variable import IPv4Variable
                return IPv4Variable.loadFromXML(xmlRoot, namespace, version)

            # Word Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:WordVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
                return WordVariable.loadFromXML(xmlRoot, namespace, version)

            # DecimalWord Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:DecimalWordVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.DecimalWordVariable import DecimalWordVariable
                return DecimalWordVariable.loadFromXML(xmlRoot, namespace, version)

            # Binary Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:BinaryVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable import BinaryVariable
                return BinaryVariable.loadFromXML(xmlRoot, namespace, version)

            # Hex Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:HexVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.HexVariable import HexVariable
                return HexVariable.loadFromXML(xmlRoot, namespace, version)

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
