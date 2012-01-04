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
import binascii
import random
import string
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| WordVariable :
#|     Definition of a word variable defined in a dictionary
#+---------------------------------------------------------------------------+
class WordVariable(Variable):
    
    def __init__(self, id, name, mutable, value):
        Variable.__init__(self, "Word", id, name, mutable)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.WordVariable.py')
        
        self.strVal = value
        self.binVal = TypeConvertor.netzobRawToBinary(TypeConvertor.ASCIIToNetzobRaw(self.strVal))
            
    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)
    
    def getDescription(self):
        if self.isMutable() :
            mut = "[M]"
        else :
            mut = "[!M]"
        return "WordVariable " + mut + " (" + self.strVal + ")"
#    
#   
#    def generateValue(self, negative, dictionary):
#        # Generate a WORD value 
#        nb_letter = random.randint(0, 10)
#        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
#        self.binVal = self.ascii2bin(self.strVal)
#        self.log.debug("Generated : " + self.strVal)
#        self.log.debug("Generated -bin )= " + str(self.binVal))
#    
#    def learn(self, val, indice, isForced, dictionary):
#        self.log.debug("Received : " + str(val))
#        
#        if self.binVal == None or isForced :
#            tmp = val[indice:]
#            
#            res = ""
#            i = 0
#            finish = False
#            while not finish :
#                v = int(tmp[i: i + 2], 16)
#                if v > 0x21 and v <= 0x7e:
#                    res += chr(v)
#                    i = i + 2
#                else:
#                    finish = True
#                
#            if i > 0 :
#                self.strVal = res
#                self.binVal = binascii.unhexlify(self.strVal)
#
#                return indice + i
#            
#        
#                
#        return -1
    
    def save(self, root, namespace):
        xmlWordVariable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlWordVariable.set("id", str(self.getID()))
        xmlWordVariable.set("name", str(self.getName()))
        xmlWordVariable.set("mutable", TypeConvertor.bool2str(self.isMutable()))
        
        xmlWordVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:WordVariable")
        
        # Definition of a binary variable
        xmlWordVariableValue = etree.SubElement(xmlWordVariable, "{" + namespace + "}value")
        xmlWordVariableValue.text = self.strVal
        return xmlWordVariable
        
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            varIsMutable = TypeConvertor.str2bool(xmlRoot.get("mutable"))
            
            varValue = xmlRoot.find("{" + namespace + "}value").text
            return WordVariable(varId, varName, varIsMutable, varValue)
            
        return None    
    
