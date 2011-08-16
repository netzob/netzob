#!/usr/bin/python
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
import unittest
from models.NetworkMessageTest import NetworkMessageTest

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

def addTestsForModels(suite):    
    suite.addTest(NetworkMessageTest('test_loadFromXml'))

if __name__ == "__main__":
    
    # Creates the main test suite
    globalTestSuite = unittest.TestSuite()
    
    # add the tests dedicated to the models
    addTestsForModels(globalTestSuite)
    
    # Execute the global test suite
    runner = unittest.TextTestRunner()
    runner.run(globalTestSuite)
