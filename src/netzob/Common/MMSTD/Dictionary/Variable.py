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
        self.id = idVar
        self.name = name
        self.typeVariable = typeVariable

    def getValue(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getValue")
        raise NotImplementedError("The current variable doesn't support 'getValue'.")    
    # Returns (b, s)
    # b = bitarray
    # s = strvalue
    def send(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function send")
        raise NotImplementedError("The current variable doesn't support 'send'.")
    
    def getDescription(self, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")

    def compare(self, value, indice, negative, vocabulary, memory):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function compare")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function compare")

    def save(self, root, namespace):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function save")
        raise NotImplementedError("Error, the current variable (declared as " + self.type + ") doesn't support function save")

    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getTypeVariable(self):
        return self.typeVariable            

    def setID(self, idVar):
        self.id = idVar

    def setName(self, name):
        self.name = name

    def setTypeVariable(self, typeVariable):
        self.typeVariable = typeVariable
    
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :            
            # IPv4 Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:IPv4Variable" :
                from netzob.Common.MMSTD.Dictionary.Variables.IPv4Variable import IPv4Variable
                return IPv4Variable.loadFromXML(xmlRoot, namespace, version)

            # Word Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:WordVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
                return WordVariable.loadFromXML(xmlRoot, namespace, version)

            # Binary Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:BinaryVariable":
                from netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable import BinaryVariable
                return BinaryVariable.loadFromXML(xmlRoot, namespace, version)

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
