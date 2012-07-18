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
import os

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.SharedLib import SharedLib


#+---------------------------------------------------------------------------+
#| Process:
#|     Model object of a simple process definition
#+---------------------------------------------------------------------------+
class Process(object):
    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param name : name of the process
    #|        pid : pid of the process
    #|        user : the owner of the process
    #+-----------------------------------------------------------------------+
    def __init__(self, name, pid, user):
        self.name = name
        self.pid = int(pid)
        self.user = user

    #+-----------------------------------------------------------------------+
    #| getSharedLibs
    #| @return a list of shared libraries linked with current process
    #+-----------------------------------------------------------------------+
    def getSharedLibs(self):
        libs = []
        # the command to execute
        cmd = "cat /proc/" + str(self.pid) + "/maps | grep \"\.so\" | awk -F\" \" {'print $1\";\"$2\";\"$6'}"
        lines = os.popen(cmd).readlines()
        for line in lines:
            ar = line.split(";")
            mem = ar[0]
            perm = ar[1]
            path = ar[2][:len(ar[2]) - 1]
            found = False
            for l in libs:
                if l.getPath() == path:
                    found = True
            if found is False:
                (libName, libVersion) = SharedLib.findNameAndVersion(path)

                lib = SharedLib(libName, libVersion, path)
                libs.append(lib)
        return libs

    def setPid(self, pid):
        self.pid = int(pid)

    def setName(self, name):
        self.name = name

    def setUser(self, user):
        self.user = user

    def getPid(self):
        return self.pid

    def getName(self):
        return self.name

    def getUser(self):
        return self.user
