#!/usr/bin/python
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
import unittest
import sys
import logging
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
sys.path.append('lib/libNeedleman/')
sys.path.append('src')

from workspace.WorkspaceTest import WorkspaceTest
from netzob.Common.Workspace import Workspace


from models.NetworkMessageTest import NetworkMessageTest
from models.FileMessageTest import FileMessageTest
from inference.SequencingTest import SequencingTest
from inference.SymbolTest import SymbolTest
from inference.GrammarInferenceTest import GrammarInferenceTest
  
from importing.ParasiteGeneratorTest import ParasiteGeneratorTest
from importing.PrototypesRepositoryTest import PrototypesRepositoryTest

from MMSTD.ModelTest import ModelTest
from netzob.ExternalLibs.xmlrunner import XMLTestRunner
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.LoggingConfiguration import LoggingConfiguration
from netzob import NetzobResources
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

def addTestsForModels(suite):    
    suite.addTest(NetworkMessageTest('test_loadFromXml'))
    suite.addTest(NetworkMessageTest('test_saveInXML'))
    suite.addTest(FileMessageTest('test_loadFromXml'))

def addTestsForInference(suite):    
    suite.addTest(SequencingTest('test_alignment'))
    suite.addTest(SymbolTest('test_findSizeField'))
   
def addTestsForGotPoisoning(suite):    
    suite.addTest(ParasiteGeneratorTest('test_sourceCodeGenerator'))
    
def addTestsForPrototypesRepositoryTest(suite):
    suite.addTest(PrototypesRepositoryTest("test_loadFromXML"))
    
def addTestsForMMSTD(suite):
    suite.addTest(ModelTest("test_SimpleDynamic"))

def addTestsForGrammaticalInference(suite):
    suite.addTest(GrammarInferenceTest("test_WMethod"))
    suite.addTest(GrammarInferenceTest("test_grammarInference"))
    
def addTestsForWorkspace(suite):
    suite.addTest(WorkspaceTest("test_workspaceParsing"))    

    
if __name__ == "__main__":
    
    # Output is given through argument.
    # If no argument : output to stdout 
    
    outputStdout = True
    
    if (len(sys.argv) == 2) :
        outputStdout = False
        reportFile = sys.argv[1]
    
    
    # Configure the environment of execution
    NetzobResources.STATIC_DIR = "resources/static"
    NetzobResources.WORKSPACE_DIR = "resources/workspace"
#    NetzobResources.WORKSPACE_DIR = 
    
    currentWorkspace = Workspace.loadWorkspace(NetzobResources.WORKSPACE_DIR)
    if currentWorkspace == None :
        logging.error("Impossible to load the workspace") 
        exit()
    
    # Second we create the logging infrastructure
    LoggingConfiguration().initializeLogging(currentWorkspace)
    
    # Creates the main test suite
    globalTestSuite = unittest.TestSuite()
#    
#    # add the tests dedicated to the models
#    addTestsForModels(globalTestSuite)    

    # add the tests dedicated to the workspace config
    addTestsForWorkspace(globalTestSuite)
#
#    # add the tests dedicated to the inference process
    addTestsForInference(globalTestSuite)
#    
#    # add the tests dedicated to the GOT Poisoning
#    # addTestsForGotPoisoning(globalTestSuite)
#    
#    # addTestsForPrototypesRepositoryTest(globalTestSuite)
#    addTestsForMMSTD(globalTestSuite)
#    
#    # add the test dedicated to the inference of the grammar
#    addTestsForGrammaticalInference(globalTestSuite)
    
    if (outputStdout == True) :
        runner = unittest.TextTestRunner()
        testResult = runner.run(globalTestSuite)
    else :
        File = open(reportFile, "w")
        reporter = XMLTestRunner(File)
        reporter.run(globalTestSuite)
        File.close()
