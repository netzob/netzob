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
from netzob.Common.Type.TypeIdentifier import TypeIdentifier


#+---------------------------------------------------------------------------+
#| WordVariable:
#|     Definition of a word variable 
#| a word is an ASCII set of characters (a-zA-Z)(a-zA-Z)*
#+---------------------------------------------------------------------------+
class WordVariable(Variable):
    
    # OriginalValue : must be an ASCII word
    def __init__(self, id, name, originalValue):
        Variable.__init__(self, "Word", id, name)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.WordVariable.py')
        self.originalValue = originalValue
        
        # Set the original value (in bitarray)
        self.computeCurrentValue(self.originalValue)
        
    
    #+-----------------------------------------------------------------------+
    #| computeCurrentValue :
    #|     Transform and save the provided ('toto') as current value
    #+-----------------------------------------------------------------------+
    def computeCurrentValue(self, strValue):
        if strValue != None:
            strCurrentValue = strValue
            binCurrentValue = TypeConvertor.string2bin(strValue)
            self.currentValue = (binCurrentValue, strCurrentValue)
        else:
            self.currentValue = None
     
    #+-----------------------------------------------------------------------+
    #| generateValue :
    #|     Generate a valid value for the variable ('babar'...)
    #+-----------------------------------------------------------------------+
    def generateValue(self):
        # todo
        return 'babar'
# Generate a WORD value
#        nb_letter = random.randint(0, 10)
#        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
#        self.binVal = self.string2bin(self.strVal)
#        self.log.debug("Generated : " + self.strVal)
#        self.log.debug("Generated -bin)= " + str(self.binVal))    

    
    #+-----------------------------------------------------------------------+
    #| getValue :
    #|     Returns the current value of the variable
    #|     it can be the original value if its set and not forget
    #|     or the value in memory if it has one
    #|     else its NONE
    #+-----------------------------------------------------------------------+
    def getValue(self, negative, vocabulary, memory):
        if self.getCurrentValue() != None:
            return self.getCurrentValue()

        if memory.hasMemorized(self):
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
        if self.getCurrentValue() != None:
            return self.getCurrentValue()

        if memory.hasMemorized(self):
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
        return "[WORD]" + str(self.getName()) + "= (orig=" + str(self.getOriginalValue()) + ")"

    #+-----------------------------------------------------------------------+
    #| getDescription :
    #|     Returns the full description of the variable
    #+-----------------------------------------------------------------------+
    def getDescription(self, negative, vocabulary, memory):
        return "[WORD]" + str(self.getName()) + "= (getValue=" + str(self.getValue(negative, vocabulary, memory)) + ")"

    #+-----------------------------------------------------------------------+
    #| compare :
    #|     Returns the number of letters which match the variable
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def compare(self, value, indice, negative, vocabulary, memory):
        localValue = self.getValue(negative, vocabulary, memory)
        # In case we can't compare with a known value, we compare only the possibility to learn it afterward
        if localValue == None:
            self.log.debug("We compare the format (will we be able to learn it afterwards ?")
            return self.compareFormat(value, indice, negative, vocabulary, memory)
        else:
            (binVal, strVal) = localValue
            self.log.info("Compare received : '" + str(value[indice:]) + "' with '" + strVal + "' ")
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
    #+-----------------------------------------------------------------------+
    #| compareFormat :
    #|     Compute if the provided data is "format-compliant"
    #|     and return the size of the biggest compliant data
    #+-----------------------------------------------------------------------+
    def compareFormat(self, value, indice, negative, vocabulary, memory):
        tmp = value[indice:]
        size = len(tmp)
        if size <= 16 :
            self.log.debug("Too small, not even 16 bits available (2 letters)")
            return -1
        
        for i in range(size, 16) :
            subValue = value[indice:indice + size - 1]
            str = TypeConvertor.bin2string(TypeConvertor.strBitarray2Bitarray(subValue))
            self.log.debug("Convert in str = " + str(str))
            if TypeIdentifier.isAscii(str) :
                self.log.debug("Its an ASCII, we verify if it contains only alphas")
                if (str.isalpha()) :
                    self.log.debug("Its an alpha")
                    return i
                else :
                    self.log.debug("Its not an alpha")
            else :
                self.log.debug("Its not an ASCII")
        
        return -1    
    
    #+-----------------------------------------------------------------------+
    #| learn :
    #|     Exactly like "compare" but it stores learns from the provided message
    #|     it can return the followings :
    #|     -1     : doesn't match
    #|     >=0    : it matchs and the following number of bits were eaten
    #+-----------------------------------------------------------------------+
    def learn(self, value, indice, negative, vocabulary, memory):
        self.log.warn("We should be learning but we dont do !!!!!!!")
        return self.compare(value, indice, negative, vocabulary, memory)
    
    #+-----------------------------------------------------------------------+
    #| restore :
    #|     Restore learnt value from the last execution of the variable
    #+-----------------------------------------------------------------------+
    def restore(self, vocabulary, memory):
        memory.restore(self)

    def getCurrentValue(self):
        return self.currentValue

    def getOriginalValue(self):
        return self.originalValue
#+-----------------------------------------------------------------------+
    #| toXML :
    #|     Returns the XML description of the variable
    #+-----------------------------------------------------------------------+
    def toXML(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:WordVariable")

        # Original Value
        if self.getOriginalValue() != None:
            xmlHexVariableOriginalValue = etree.SubElement(xmlVariable, "{" + namespace + "}originalValue")
            xmlHexVariableOriginalValue.text = self.getOriginalValue()

        

    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1":
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")

            xmlWordVariableOriginalValue = xmlRoot.find("{" + namespace + "}originalValue")
            if xmlWordVariableOriginalValue != None:
                originalValue = xmlWordVariableOriginalValue.text
            else:
                originalValue = None


            return WordVariable(varId, varName, originalValue)
        return None



