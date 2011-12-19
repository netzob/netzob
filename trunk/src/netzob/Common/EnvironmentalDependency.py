# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| EnvironmentalDependency :
#|     Class definition of an environmental dependency
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class EnvironmentalDependency(object):
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value
        
    
    def save(self, root, namespace):
        environmental_dependency = etree.SubElement(root, "{" + namespace + "}environmental_dependency")
        environmental_dependency.set("name", str(self.name))
        environmental_dependency.set("type", str(self.type))
        environmental_dependency.text = str(self.value)
    
   
    def getName(self):
        return self.name
    def getType(self):
        return self.type
    def getValue(self):
        return self.value
    
    def setName(self, name):
        self.name = name
    def setType(self, type):
        self.type = type
    def setValue(self, value):
        self.value = value
