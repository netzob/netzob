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
#| BinaryVariable:
#|     Definition of a binary variable
#+---------------------------------------------------------------------------+
class BinaryVariable(Variable):
    
    # OriginalValue : must be a "real" bitarray (a binary one)
    # startValue : must be a "real" bitarray
    # endValue : must be a "real" bitarray
    # padding : the number of padding if activated must be an int > 0 (can be None)
    def __init__(self, id, name, originalValue, startValue, endValue, padding):
        Variable.__init__(self, "Binary", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.BinaryVariable.py')        
        self.originalValue = originalValue
        self.startValue = startValue
        self.endValue = endValue
        self.padding = padding
        
        # Set the current value
        self.computeCurrentValue(self.originalValue)
    
    def computeCurrentValue(self, strValue):
        if strValue != None :
            strCurrentValue = str(strValue)
            binCurrentValue = TypeConvertor.strBitarray2Bitarray(strValue)
            self.currentValue = (binCurrentValue, strCurrentValue)
        else :
            self.currentValue = None
    
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
        return "BinaryVariable [originalValue = " + str(self.getOriginalValue()) + "]"
    
    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        return "BinaryVariable [getValue = " + str(self.getValue(negative, vocabulary, memory)) + "]"
    
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
    
    def getPadding(self):
        return self.padding
               
    #+-----------------------------------------------------------------------+
    #| toXML :
    #|     Returns the XML description of the variable 
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:BinaryVariable")
        
        # Original Value
        if self.getOriginalValue() != None :
            xmlBinaryVariableOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlBinaryVariableOriginalValue.text = TypeConvertor.bitarray2StrBitarray(self.getOriginalValue())
        
        # Starting Value
        xmlBinaryVariableStartValue = etree.SubElement(xmlVariable, "{" + namespace + "}startValue")
        xmlBinaryVariableStartValue.text = TypeConvertor.bitarray2StrBitarray(self.getStartValue())
        
        # Ending Value
        xmlBinaryVariableEndValue = etree.SubElement(xmlVariable, "{" + namespace + "}endValue")
        xmlBinaryVariableEndValue.text = TypeConvertor.bitarray2StrBitarray(self.getEndValue())
        
        # Padding
        if self.getPadding() != None or self.getPadding() > 0 : 
            xmlBinaryVariablePaddingValue = etree.SubElement(xmlVariable, "{" + namespace + "}padding")
            xmlBinaryVariablePaddingValue.text = TypeConvertor.int2string(self.getPadding())
        

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            
            xmlBinaryVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlBinaryVariableOriginalValue != None :
                originalValue = TypeConvertor.strBitarray2Bitarray(xmlBinaryVariableOriginalValue.text)
            else :
                originalValue = None
            
            xmlBinaryVariableStartValue = xmlRoot.find("{" + namespace + "}startValue")
            startValue = TypeConvertor.strBitarray2Bitarray(xmlBinaryVariableStartValue.text)
            
            xmlBinaryVariableEndValue = xmlRoot.find("{" + namespace + "}endValue")
            endValue = TypeConvertor.strBitarray2Bitarray(xmlBinaryVariableEndValue.text)
            
            xmlBinaryVariablePaddingValue = xmlRoot.find("{" + namespace + "}padding")
            if xmlBinaryVariablePaddingValue != None :
                padding = TypeConvertor.string2int(xmlBinaryVariablePaddingValue.text)
            else :
                padding = None

            return BinaryVariable(varId, varName, originalValue, startValue, endValue, padding)
        return None
