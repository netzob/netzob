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
from netzob.Common.Type.Format import Format

#+---------------------------------------------------------------------------+
#| IPv4Variable :
#|     Definition of an IPv4 variable defined in a dictionary
#+---------------------------------------------------------------------------+
class IPv4Variable(Variable):
    
    # OriginalValue : must be a "real" ip address declared in ASCII like : "192.168.0.10"
    # startValue :  must be a "real" ip address declared in ASCII like : "192.168.0.10"
    # endValue :  must be a "real" ip address declared in ASCII like : "192.168.0.11"
    # format : must be a string value of a format (hex or ascii)
    def __init__(self, id, name, originalValue, startValue, endValue, format):
        Variable.__init__(self, "IPv4Variable", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.IP4Variable.py')
        
        # Save initial informations
        self.format = format
        self.startValue = startValue
        self.endValue = endValue
        self.originalValue = originalValue
        
        # Set the current value
        self.computeCurrentValue(self.originalValue)
    
    #+-----------------------------------------------------------------------+
    #| computeCurrentValue :
    #|     Transform and save the provided "192.168.0.10" as current value
    #+-----------------------------------------------------------------------+
    def computeCurrentValue(self, strValue):
        if strValue != None :            
            if self.format == Format.ASCII :
                strCurrentValue = str(strValue)
                binCurrentValue = TypeConvertor.string2bin(strValue, 'big')
            elif self.format == Format.HEX :
                hexVal = TypeConvertor.ipToNetzobRaw(strValue)
                if hexVal != None :
                    strCurrentValue = str(strValue)
                    binCurrentValue = TypeConvertor.netzobRawToBitArray(hexVal)
                else :
                    strCurrentValue = str("None:Error")
                    binCurrentValue = None
            self.currentValue = (binCurrentValue, strCurrentValue)
        else :
            self.currentValue = None    
            
            
    #+-----------------------------------------------------------------------+
    #| generateValue :
    #|     Generate a valid value for the variable
    #+-----------------------------------------------------------------------+        
    def generateValue(self):
        self.log.error("Error, the current variable (declared as " + self.type + ") doesn't support function generateValue")
        raise NotImplementedError("The current variable doesn't support 'generateValue'.")
            
    
    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        if self.getCurrentValue() != None :
            return self.getCurrentValue()
        
        if memory.hasMemorized(self) :
            return memory.recall(self)
        
        return None     
            
            
    #+-----------------------------------------------------------------------+
    #| getValueToSend :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     or it generates one and save its value in memory
    #+-----------------------------------------------------------------------+
    def getValueToSend(self, negative, vocabulary, memory):
        if self.getCurrentValue() != None :
            return self.getCurrentValue()
        
        if memory.hasMemorized(self) :
            return memory.recall(self)
        
        # We generate a new value
        self.computeCurrentValue(self.generateValue())
        
        # We save in memory the current value
        memory.memorize(self, self.getCurrentValue())
        
        # We return the newly generated and memorized value
        return self.getCurrentValue()
            
            
            
    #+-----------------------------------------------------------------------+
    #| getUncontextualizedDescription :
    #|     Returns the uncontextualized description of the variable (no use of memory or vocabulary)
    #+-----------------------------------------------------------------------+   
    def getUncontextualizedDescription(self):
        return "IPv4Variable [originalValue = " + str(self.getOriginalValue()) + "]"
    
    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        return "IPv4Variable [getValue = " + str(self.getValue(negative, vocabulary, memory)) + "]"
            
    
    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten 
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        
        (binVal, strVal) = self.getValue(negative, vocabulary, memory)
        
        self.log.info("Compare received : '" + str(value[indice:]) + "' with '" + str(binVal) + "' ")
        tmp = value[indice:]
               
        if len(tmp) >= len(binVal):
            if tmp[:len(binVal)] == binVal:
                self.log.info("Compare successful")
                return indice + len(binVal)
            else:
                self.log.info("error in the comparison")
                return -1
        else:
            self.log.info("Compare fail")
            return -1
        
    def getCurrentValue(self) :
        return self.currentValue
    
    def getOriginalValue(self):
        return self.originalValue
    
    def getStartValue(self):
        return self.startValue
    
    def getEndValue(self):
        return self.endValue
    
    def getFormat(self):
        return self.format    
 
    def toXML(self, root, namespace):
        xmlIPv4Variable = etree.SubElement(root, "{" + namespace + "}variable")
        xmlIPv4Variable.set("id", str(self.getID()))
        xmlIPv4Variable.set("name", str(self.getName()))
        
        xmlIPv4Variable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:IPv4Variable")
        
        # Original Value
        if self.getOriginalValue() != None :
            xmlIPVariableOriginalValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}originalValue")
            xmlIPVariableOriginalValue.text = str(self.getOriginalValue())
        
        # Starting Value
        xmlIPVariableStartValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}startValue")
        xmlIPVariableStartValue.text = str(self.getStartValue())
        
        # Ending Value
        xmlIPVariableEndValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}endValue")
        xmlIPVariableEndValue.text = str(self.getEndValue())
        
        # Format 
        xmlIPVariableFormatValue = etree.SubElement(xmlIPv4Variable, "{" + namespace + "}format")
        xmlIPVariableFormatValue.text = str(self.getFormat())
        
        return xmlIPv4Variable
 
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            
            xmlIPVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlIPVariableOriginalValue != None :
                originalValue = xmlIPVariableOriginalValue.text
            else :
                originalValue = None
            
            xmlIPVariableStartValue = xmlRoot.find("{" + namespace + "}startValue")
            startValue = xmlIPVariableStartValue.text
            
            xmlIPVariableEndValue = xmlRoot.find("{" + namespace + "}endValue")
            endValue = xmlIPVariableEndValue.text
            
            xmlIPVariablePaddingValue = xmlRoot.find("{" + namespace + "}format")
            format = str(xmlIPVariablePaddingValue.text)
            
            return IPv4Variable(varId, varName, originalValue, startValue, endValue, format)
            
        return None    
    
