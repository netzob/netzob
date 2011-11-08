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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import logging
import gtk
import time
from threading import Thread

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------
from xml.etree import ElementTree
from xdot import DotWindow

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from .... import ConfigurationParser
#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| MMSTDViewer :
#|    Generates a viewer for the selected MMSTD
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class MMSTDViewer(Thread):
    
    def __init__(self, automata):
        Thread.__init__(self)
        self.terminated = False
        self.automata = automata
        
    def run(self): 
        pass       
#        dotCode = self.getDotCode()
#        window = DotWindow()
#        window.set_dotcode(dotCode)
#        window.connect('destroy', gtk.main_quit)
#        gtk.main() 
        
  
    def getDotCode(self):
        
        dotCode = "digraph G {\n"
        
        # first we include all the states declared in the automata
        states = self.automata.getAllStates()
        
        for state in states :
            dotCode = dotCode + "\"" + state.getName() + "\"\n"
            
            
        for inputState in states :
            for transition in inputState.getTransitions() :
                outputState = transition.getOutputState()                
                dotCode = dotCode + "\"" + inputState.getName() + "\" -> \"" + outputState.getName() + "\" [fontsize=5, label=\"" + transition.getDescription() + "\"]\n"
        
        dotCode = dotCode + "}"
        
        print dotCode
        
        return dotCode
#        
#        return """
#digraph G {
#  "Initial State" [URL="http://en.wikipedia.org/wiki/Hello"]
#  "Example of state" [URL="http://en.wikipedia.org/wiki/World"]
#    "Initial State"  -> "Example of state"
#}
#"""
