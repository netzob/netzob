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


#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------
from netzob.ExternalLibs.xdot import DotWidget

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------



#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------


#+---------------------------------------------- 
#| XDotWidget :
#|    Integrates an XDot graph in a PyGtk window
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class XDotWidget(DotWidget):
    
    def __init__(self):
        DotWidget.__init__(self)
        self.set_filter("dot")
    
    def drawAutomata(self, automata):
        self.set_dotcode(automata.getDotCode())
