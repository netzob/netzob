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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging


#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------

#+---------------------------------------------- 
#| Searcher :
#|     Provides multiple algorithms for a searching after a pattern in a 
#|     set of computed messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class Searcher(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #| @param messages the list of messages it will search in
    #+----------------------------------------------   
    def __init__(self, messages):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.Searcher.py')
        self.messages = messages
    
    #+---------------------------------------------- 
    #| searchBinary :
    #|   search for a value provided in Binary
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchBinary(self, value):
        return []
    
    #+---------------------------------------------- 
    #| searchOctal :
    #|   search for a value provided in octal
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchOctal(self, value):
        return []
    
    #+---------------------------------------------- 
    #| searchHexadecimal :
    #|   search for a value provided in hex
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchHexadecimal(self, value):
        return []
    
    #+---------------------------------------------- 
    #| searchASCII :
    #|   search for a value provided in ASCII
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchASCII(self, value):
        return []
    
    #+---------------------------------------------- 
    #| searchIP :
    #|   search for a value provided in IP
    #| @param value the value to search for
    #+---------------------------------------------- 
    def searchIP(self, value):
        return []
        


