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
from netzob.Common.Type.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| IPv4Variable :
#|     Definition of an IPv4 variable defined in a dictionary
#+---------------------------------------------------------------------------+
class IPv4Variable(Variable):
    
    def __init__(self, id, name, originalValue, startValue, endValue, format):
        Variable.__init__(self, "IPv4Variable", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.IP4Variable.py')
        
        # Save initial informations
        self.format = format
        self.startValue = startValue
        self.endValue = endValue
        self.originalValue = originalValue
        
        
        
        
    def compare(self, value, indice, negative, memory):
        self.log.debug("Compare received : '" + str(value[indice:]) + "' with '" + str(self.binVal) + "' ")
        tmp = value[indice:]
        if len(tmp) >= len(self.binVal) :
            if tmp[:len(self.binVal)] == self.binVal :
                self.log.debug("Compare successful")
                return indice + len(self.binVal)              
            else :
                self.log.info("error in the comparison : " + str(tmp[:len(self.binVal)]) + " != " + str(self.binVal))
                return -1                  
        else :
            self.log.debug("Compare fail")
            return -1
    
    def send(self, negative, memory):
        return (self.binVal, self.strVal)
            
    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)
    
    def getDescription(self):
        if self.isMutable() :
            mut = "[M]"
        else :
            mut = "[!M]"
            
        if self.originalValue != None :
            return "IPV4Variable " + mut + " (" + self.getOriginalValue() + ")"
        else :
            return "IPV4Variable " + mut + " (no value : " + +")"
    
    def save(self, root, namespace):
        xmlIPv4Variable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlIPv4Variable.set("id", str(self.getID()))
        xmlIPv4Variable.set("name", str(self.getName()))
        xmlIPv4Variable.set("mutable", TypeConvertor.bool2str(self.isMutable()))
        
        xmlIPv4Variable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:IPv4Variable")
        
        # Definition of the content of this variable in XML
        xmlIPv4VariableOriginalValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}originalValue")
        # optional original value
        if self.getOriginalValue() != None :
            xmlIPv4VariableOriginalValue.text = self.getOriginalValue()
        
        # mandatory starting value
        xmlIPv4VariableStartValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}startValue")
        xmlIPv4VariableStartValue.text = self.getStartValue()
        
        # mandatory ending value
        xmlIPv4VariableEndValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}endValue")
        xmlIPv4VariableEndValue.text = self.getEndValue()
        
        # mandatory formating value
        xmlIPv4VariableEndValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}endValue")
        xmlIPv4VariableEndValue.text = self.getEndValue()
        
        return xmlIPv4Variable
     
    def getOriginalValue(self):
        return self.originalValue
    def getStartValue(self):
        return self.startValue
    def getEndValue(self):
        return self.endValue
    def getFormat(self):
        return self.format
                       
     
       
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            varIsMutable = TypeConvertor.str2bool(xmlRoot.get("mutable"))
            
            varValue = xmlRoot.find("{" + namespace + "}value").text
            return IPv4Variable(varId, varName, varIsMutable, varValue)
            
        return None    
    
