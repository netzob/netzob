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
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Import.GOTPoisoning import HijackedFunction


#+---------------------------------------------------------------------------+
#| SharedLib:
#|     Model object of a shared lib
#+---------------------------------------------------------------------------+
class SharedLib(object):
    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param name     : name of the lib
    #| @param version  : version of the lib
    #| @param path     : full path of the lib
    #+-----------------------------------------------------------------------+
    def __init__(self, name, version, path):
        self.name = name
        self.version = version
        self.path = path
        self.functions = []

    @staticmethod
    def loadFromXML(rootElement):
        # First we verify rootElement is a message
        if rootElement.tag != "lib":
            raise NameError("The parsed xml doesn't represent a shared lib.")
        # Then we verify its a Network Message
        if rootElement.get("name", "none") == "none":
            raise NameError("The parsed xml doesn't represent a shared lib with a valid name.")

        # parse the name of the lib
        libName = rootElement.get("name", "none")
        libVersion = rootElement.get("version", "0.0")

        functions = []
        # parse the declared functions
        for xmlFunc in rootElement.findall("functions//function"):
            function = HijackedFunction.HijackedFunction.loadFromXML(xmlFunc)
            functions.append(function)

        lib = SharedLib(libName, libVersion, "")
        lib.setFunctions(functions)

        return lib

    @staticmethod
    def findNameAndVersion(path):

        nameWithoutPath = path.split(os.sep)[len(path.split(os.sep)) - 1]

        # Remove the extension
        if (len(nameWithoutPath) > 3 and nameWithoutPath[len(nameWithoutPath) - 3:] == ".so"):
            nameWithoutPath = nameWithoutPath[:len(nameWithoutPath) - 3]

        libName = nameWithoutPath
        libVersion = "0.0"

        # find version number
        try:
            if (string.index(nameWithoutPath, "-") > 1):
                libName = nameWithoutPath[:nameWithoutPath.index("-")]
                libVersion = nameWithoutPath[nameWithoutPath.index("-") + 1:]
        except:
            pass

        return (libName, libVersion)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def getVersion(self):
        return self.version

    def setVersion(self, version):
        self.version = version

    def getPath(self):
        return self.path

    def setPath(self, path):
        self.path = path

    def setFunctions(self, functions):
        self.functions = functions

    def getFunctions(self):
        return self.functions
