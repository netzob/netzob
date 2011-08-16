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
from models.netzobTestCase1 import NetzobTestCase1
from models.netzobTestCase2 import NetzobTestCase2

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

def addTestsForModels(suite):    
    suite.addTest(NetzobTestCase1('test_getName'))
    suite.addTest(NetzobTestCase1('test_average'))
    suite.addTest(NetzobTestCase2('test_getName'))
    suite.addTest(NetzobTestCase2('test_average'))

if __name__ == "__main__":
    
    # Creates the main test suite
    globalTestSuite = unittest.TestSuite()
    
    # add the tests dedicated to the models
    addTestsForModels(globalTestSuite)
    
    # Execute the global test suite
    runner = unittest.TextTestRunner()
    runner.run(globalTestSuite)
