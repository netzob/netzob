#!/usr/bin/python
# coding: utf8


#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import base64
import logging

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import ConfigurationParser


#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

class TypeIdentifier():
    

    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.TypeIdentifier.py')
    
    
    
    
    #+---------------------------------------------- 
    #| Identify the possible types from a hexa string
    #+----------------------------------------------
    def getTypes(self, stringsTable):
        entireString = "".join(stringsTable)
        
        setSpace = set()
        for i in range(0, len(entireString), 2):
            setSpace.add(int(entireString[i:i + 2], 16))
        sorted(setSpace)

        aggregatedValues = ""
        for i in setSpace:
            aggregatedValues += chr(i)

        typesList = []
        if aggregatedValues == "":
            return typesList
        if aggregatedValues.isdigit():
            typesList.append("num")
        if aggregatedValues.isalpha():
            typesList.append("alpha")
        if aggregatedValues.isalnum():
            typesList.append("alphanum")
        if self.isAscii(aggregatedValues):
            typesList.append( "ascii")
        if self.isBase64(stringsTable):
            typesList.append("base64enc")
            typesList.append("base64dec")
        typesList.append("binary")

        return typesList
    
    #+---------------------------------------------- 
    #| Return True if the string parameter is ASCII
    #+----------------------------------------------
    def isAscii(self, string):
        try:
            string.decode('ascii')
            return True
        except UnicodeDecodeError:
            return False    

    #+---------------------------------------------- 
    #| Return True if the string parameter is base64
    #|  encoded
    #+----------------------------------------------
    def isBase64(self, stringsTable):
        res = True
        try:
            for string in stringsTable:
                s = ""
                for i in range(0, len(string), 2):
                    s += chr(int(string[i:i + 2], 16))
                tmp = base64.b64decode(s)
                if tmp == "":
                    res = False
        except TypeError:
            res = False

        return res    

    #+---------------------------------------------- 
    #| Return the string parameter in ASCII
    #+----------------------------------------------
    def toASCII(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even !")
            return raw

        res = ""
        for i in range(0, len(raw), 2):
            res = res + chr(int(raw[i: i+2], 16))
        return res

    #+---------------------------------------------- 
    #| Return the string parameter in numerical value
    #+----------------------------------------------
    def toNum(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even")
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isdigit():
            self.log.error("Not a digit")
            return raw

        return s

    #+---------------------------------------------- 
    #| Return the string parameter in alpha
    #+----------------------------------------------
    def toAlpha(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even")
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isalpha():
            self.log.error("Not an alpha string")
            return raw

        return s

    #+---------------------------------------------- 
    #| Return the string parameter in alphanum
    #+----------------------------------------------
    def toAlphanum(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even")
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        if not s.isalnum():
            self.log.error("Not an alphanumerical string")
            return raw

        return s

    #+---------------------------------------------- 
    #| Return the string parameter base64 encoded
    #+----------------------------------------------
    def toBase64Encoded(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even")
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        res = ""
        try:
            res = base64.b64decode(s)
            if res == "":
                res = raw
        except TypeError:
            res = raw

        return s

    #+---------------------------------------------- 
    #| Return the string parameter base64 decoded
    #+----------------------------------------------
    def toBase64Decoded(self, raw):
        if len(raw) % 2 != 0:
            self.log.error("Hex string len not even")
            return raw

        s = ""
        for i in range(0, len(raw), 2):
            s += chr(int(raw[i:i + 2], 16))

        res = ""
        try:
            res = base64.b64decode(s)
            if res == "":
                res = raw
        except TypeError:
            res = raw

        return res

    #+---------------------------------------------- 
    #| Transform the current hex message ( '1fdf' ) in binary ( '\x1f\xdf' )
    #+----------------------------------------------          
    def toBinary(self, msg):
        if len(msg) % 2 != 0:
            self.log.error("Hex string len not even")
            return msg

        res = ""
        for i in range(0, len(msg), 2):
            res = res + chr(int(msg[i: i+2], 16))
        return res
