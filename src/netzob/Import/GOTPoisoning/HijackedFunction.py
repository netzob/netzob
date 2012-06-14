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
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| HijackedFunction:
#|     Definition of a function to hijack
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| A function to hijack has the following members:
#|     - a name
#|     - a return type
#|     - a set of parameter
#+---------------------------------------------------------------------------+
class HijackedFunction():
    def __init__(self, name, returnType, parameters, source):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.GOTPoisoning.HijackedFunction.py')
        self.name = name
        self.returnType = returnType
        self.parameters = parameters
        self.source = source

    def getSource(self):
        return self.source

    def getEndOfFunction(self):
        source = ""
        # add the return part of the function
        source += "\t" + self.returnType + " (*origfunc)("
        i = 0
        params = ""
        for param in self.parameters:
            params += param[0] + " " + param[1] + "_"
            if i != len(self.parameters) - 1:
                params += ", "
            i = i + 1
        source += params + ") = 0x00000000;\n\n"

        paramNames = ""
        i = 0
        for param in self.parameters:
            paramNames += param[1]
            if i != len(self.parameters) - 1:
                paramNames += ", "
            i = i + 1

#        source += "\tchar new_string[5];\n"
#        source += "\tnew_string[0] = 'e';\n"
#        source += "\tnew_string[1] = '.';\n"
#        source += "\tnew_string[2] = 'l';\n"
#        source += "\tnew_string[3] = 'g';\n"
#        source += "\tnew_string[4] = 0;\n"
        source += "\torigfunc(" + paramNames + ");\n"

        return source

    #+-----------------------------------------------------------------------+
    #| getPrototype
    #|    returns the official prototype of the function to hijack
    #| @return a string which contains the prototype
    #+-----------------------------------------------------------------------+
    def getPrototype(self):
        params = ""
        i = 0
        for param in self.parameters:
            params = params + param[0] + " " + param[1]
            if i < len(self.parameters) - 1:
                params = params + ", "
            i = i + 1
        prototype = self.returnType + " " + self.name + " (" + params + ")"
        return prototype

    #+-----------------------------------------------------------------------+
    #| getParasitePrototype
    #|    returns the prototype of the parasite of the function to hijack
    #| @return a string which contains the prototype
    #+-----------------------------------------------------------------------+
    def getParasitePrototype(self):
        params = ""
        i = 0
        for param in self.parameters:
            params = params + param[0] + " " + param[1]
            if i < len(self.parameters) - 1:
                params = params + ", "
            i = i + 1

        prototype = self.returnType + " netzobParasite_" + self.name + " (" + params + ")"
        return prototype

    #+-----------------------------------------------------------------------+
    #| getParasiteFunctionDeclaration
    #|    returns the function declaration of the parasite
    #| @return a string which contains the declaration of the function
    #+-----------------------------------------------------------------------+
    def getParasiteFunctionDeclaration(self):
        params = ""
        i = 0
        for param in self.parameters:
            params += param[0] + " " + param[1]
            if i != len(self.parameters) - 1:
                params += ", "
            i = i + 1

        functionDeclaration = self.returnType + " netzobParasite_" + self.name + " (" + params + ")"
        return functionDeclaration

    @staticmethod
    def loadFromXML(rootElement):
        if rootElement.tag != "function":
            raise NameError("The parsed xml doesn't represent a function of a shared a lib.")
        if rootElement.get("name", "none") == "none":
            raise NameError("The parsed xml doesn't have a valid name which is mandatory for a function")

        funcName = rootElement.get("name", "none")
        funcReturnType = rootElement.get("returnType", "void")
        funcParams = []

        # parse the parameters
        for xmlParam in rootElement.findall("params//param"):
            if xmlParam.get("name", "none") == "none":
                raise NameError("The parsed xml doesn't have a valid param name")
            if xmlParam.get("type", "none") == "none":
                raise NameError("The parsed xml doesn't have a valid type")
            pName = xmlParam.get("name", "none")
            pType = xmlParam.get("type", "none")
            p = [pType, pName]
            funcParams.append(p)

        source = rootElement.find("source").text
#        source = "\tint fd = _open(\"/tmp/content2.log\");\n"
#
#        # parse the exports
#        for xmlExport in rootElement.findall("exports//export"):
#            if xmlExport.get("var", "none") == "none":
#                raise NameError("The exported var should have a name")
#
#            exportVar = xmlExport.get("var", "none")
#            exportSize = ""
#            if (xmlExport.get("size", "none")!="none"):
#                exportSize = xmlExport.get("size", "none")
#
#            source = source + "\t _write(fd, "+exportVar+" , "+exportSize+");\n"
#
#
#
#        source = source + "\t_close(fd);\n\t";

        result = HijackedFunction(funcName, funcReturnType, funcParams, source)
        return result

    #+------------------------------------------------------------------------
    #| GETTERS AND SETTERS
    #+------------------------------------------------------------------------
    def getName(self):
        return self.name

    def getReturnType(self):
        return self.returnType

    def getParameters(self):
        return self.parameters

    def setName(self, name):
        self.name = name

    def setReturnType(self, returnType):
        self.returnType = returnType

    def setParameters(self, parameters):
        self.parameters = parameters

    def setSource(self, source):
        self.source = source
