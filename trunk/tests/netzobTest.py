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
import sys
import logging
import os
from workspace.WorkspaceTest import WorkspaceTest
from netzob.Common.Workspace import Workspace

sys.path.append('lib/libNeedleman/')
sys.path.append('src')

from models.NetworkMessageTest import NetworkMessageTest
from models.FileMessageTest import FileMessageTest
from inference.SequencingTest import SequencingTest
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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

def addTestsForModels(suite):    
    suite.addTest(NetworkMessageTest('test_loadFromXml'))
    suite.addTest(NetworkMessageTest('test_saveInXML'))
    suite.addTest(FileMessageTest('test_loadFromXml'))

def addTestsForInference(suite):    
    suite.addTest(SequencingTest('test_alignment'))
    
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
#    addTestsForInference(globalTestSuite)
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
