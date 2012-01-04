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
from bitarray import bitarray


#+---------------------------------------------------------------------------+
#| AggregrateVariable :
#|     Definition of an aggregation of variables defined in a dictionary
#+---------------------------------------------------------------------------+
class AggregateVariable(Variable):
    
    def __init__(self, id, name, vars):
        Variable.__init__(self, "Aggregate", id, name, True)
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.AggregateVariable.py')
        self.vars = []
        if vars != None :
            self.vars.extend(vars)
            
    def addChild(self, variable):
        self.vars.append(variable)
        
    def compare(self, value, indice, negative, memory):
        result = indice
        for var in self.vars :
            self.log.debug("Indice = " + str(result) + " : " + var.getDescription())
            result = var.compare(value, result, negative, memory)
            if result == -1 or result == None :
                self.log.debug("Compare fail")
                return result
            else :
                self.log.debug("Compare successfull")
        return result
        
    def send(self, negative, memory):
        binResult = bitarray()
        strResult = ""
        for var in self.vars :
            (b, s) = var.send(negative, memory)
            print "==>" + str(b)
            binResult += b
            strResult = strResult + s
        return (binResult, strResult)

    
    def getDescription(self):
        values = []
        for var in self.vars :
            values.append(var.getDescription())            
        return "AggregateVariable [" + " AND ".join(values) + "]"
    
    def save(self, root, namespace):
        xmlVariable = etree.SubElement(root, "{" + namespace + "}variable")
        # Header specific to the definition of a variable
        xmlVariable.set("id", str(self.getID()))
        xmlVariable.set("name", str(self.getName()))
        xmlVariable.set("mutable", TypeConvertor.bool2str(self.isMutable()))
        xmlVariable.set("{http://www.w3.org/2001/XMLSchema-instance}type", "netzob:AggregateVariable")
        
        # Definition of the variables
        for var in self.vars :
            var.save(xmlVariable, namespace)
        
        
    @staticmethod
    def loadFromXML(xmlRoot, namespace, version):
        if version == "0.1" :
            varId = xmlRoot.get("id")
            varName = xmlRoot.get("name")
            
            children = []
            for xmlChildren in xmlRoot.findall("{" + namespace + "}variable") :
                child = Variable.loadFromXML(xmlChildren, namespace, version)
                children.append(child)
            
            return AggregateVariable(varId, varName, children)
            
        return None
    
    
    
#    def getValue(self, negative, dictionary):
#        binResult = []
#        strResult = []        
#        for idVar in self.vars :
#            var = dictionary.getVariableByID(int(idVar))
#            (binVal, strVal) = var.getValue(negative, dictionary)
#            if binVal == None :
#                return (None, None)
#            else :
#                binResult.append(binVal)
#                strResult.append(strVal)
#        return ("".join(binResult), "".join(strResult))       
#    
#    def generateValue(self, negative, dictionary):
#        for idVar in self.vars :
#            var = dictionary.getVariableByID(int(idVar))
#            var.generateValue(negative, dictionary)
#            
#    def learn(self, val, indice, isForced, dictionary):
#        new_indice = indice
#        for idVar in self.vars :
#            var = dictionary.getVariableByID(int(idVar))
#            tmp_indice = var.learn(val, new_indice, isForced, dictionary)
#            if tmp_indice != -1 :
#                new_indice = tmp_indice
#        return new_indice
