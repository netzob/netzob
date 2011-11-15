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
#| Global Imports
#+----------------------------------------------
import logging
from bitarray import bitarray


#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser

class TypeConvertor():
    
    
    
    #+---------------------------------------------- 
    #| Transform an ascii string to its binary representation
    #| @param the ascii string to transform
    #| @endian the endian selected (little or big) (normal = big)
    #| @return 
    #+----------------------------------------------
    @staticmethod
    def ascii2bin(ascii, endian):
        result = bitarray(endian=endian)
        result.fromstring(ascii)
        return result
    
    #+---------------------------------------------- 
    #| Transform an hex to the bits [hex message ('1fdf')]
    #| @param the hex to transform
    #| @endian the endian selected (little or big) (normal = big)
    #| @return 
    #+----------------------------------------------
    @staticmethod
    def hex2bin(hex, endian):
        res = ""
        if len(hex) % 2 == 0: # Even length
            for i in range(0, len(hex), 2):
                res = res + chr(int(hex[i: i + 2], 16))
        else: # Odd length
            for i in range(0, len(hex) - 1, 2):
                res = res + chr(int(hex[i: i + 2], 16))
            res = res + chr(int(hex[-1], 16))
        
        result = bitarray(endian='big')
        result.fromstring(res)
        return result
        
    @staticmethod
    def bin2hex(bin):
        return bin.tostring()
    
    
