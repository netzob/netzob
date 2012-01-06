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
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.Type.TypeConvertor import TypeConvertor



#+---------------------------------------------------------------------------+
#| BinaryVarible :
#|     Definition of a binary variable
#+---------------------------------------------------------------------------+
class BinaryVariable(Variable):
    
    def __init__(self, id, name, mutable, value):
        Variable.__init__(self, "Binary", id, name, mutable)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable.py')
        if value == "" or value == None :
            self.binVal = None
            self.strVal = None
        else :
            self.strVal = str(value)
            self.binVal = TypeConvertor.strBitarray2Bitarray(value)
            
    def compare(self, value, indice, negative, memory):
        self.log.info("Compare received : '" + str(value[indice:]) + "' with '" + str(self.binVal) + "' ")
        tmp = value[indice:]
        if len(tmp) >= len(self.binVal) :
            if tmp[:len(self.binVal)] == self.binVal :
                self.log.info("Compare successful")
                return indice + len(self.binVal)      
            else :
                self.log.info("error in the comparison")
                return -1
        else :
            self.log.info("Compare fail")
            return -1
            
    def send(self, negative, memory):
        return (self.binVal, self.strVal)
    
    def getValue(self):
        return (self.binVal, self.strVal)
    
    def getDescription(self):
        if self.isMutable() :
            mut = "[M]"
        else :
            mut = "[!M]"
        return "BinaryVariable " + mut + " (" + self.strVal + ")"
      
    def save(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("mutable", TypeConvertor.bool2str(self.isMutable()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:BinaryVariable")
        
        # Definition of a binary variable
        xmlWordVariableValue = etree.SubElement(xmlVariable, "{" + namespace + "}value")
        xmlWordVariableValue.text = TypeConvertor.bitarray2StrBitarray(self.binVal)

        
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            varIsMutable = TypeConvertor.str2bool(xmlRoot.get("mutable"))
            varValue = TypeConvertor.strBitarray2Bitarray(xmlRoot.find("{" + namespace + "}value").text)
            return BinaryVariable(varId, varName, varIsMutable, varValue)
            
        return None
    
