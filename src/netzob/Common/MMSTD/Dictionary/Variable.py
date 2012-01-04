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
#| Variable :
#|     Definition of a variable defined in a dictionary
#+---------------------------------------------------------------------------+
class Variable():
    
    def __init__(self, type, id, name, mutable):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.py')
        self.id = id
        self.name = name
        self.type = type
        self.mutable = mutable
 
    def getValue(self, negative, dictionary):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getValue")
        raise NotImplementedError("The current variable doesn't support 'getValue'.")
    
    def getDescription(self):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function getDescription")
        raise NotImplementedError("The current variable doesn't support 'getDescription'.")
    
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
    def getType(self):
        return self.type    
    def isMutable(self):
        return self.mutable
        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    def setType(self, type):
        self.type = type
    def setMutable(self, mutable):
        self.mutable = mutable
        
    
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :            
            # Word Variable
            if xmlRoot.get("{http://www.w3.org/2001/XMLSchema-instance}type", "abstract") == "netzob:WordVariable" :
                from netzob.Common.MMSTD.Dictionary.Variables.WordVariable import WordVariable
                return WordVariable.loadFromXML(xmlRoot, namespace, version)
