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
import logging
import os

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
import ConfigurationParser
import SharedLib

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Process :
#|     Model object of a simple process definition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
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
        cmd = "cat /proc/"+str(self.pid)+"/maps | grep \"\.so\" | awk -F\" \" {'print $1\";\"$2\";\"$6'}"
        lines = os.popen(cmd).readlines()
        for line in lines:
            ar = line.split(";")
            mem = ar[0]
            perm = ar[1]
            path = ar[2][:len(ar[2])-1]
            found = False
            for l in libs :
                if l.getPath() == path :
                    found = True
            if found == False :
                (libName,libVersion) = SharedLib.SharedLib.findNameAndVersion(path)
                
                
                
                lib = SharedLib.SharedLib(libName, libVersion, path)
                libs.append(lib)
        return libs
        
        
    def setPid(self, pid):
        self.pid = int(pid)
    def setName(self, name):
        self.name = name
    def setUser(self, user):
        self.user = user
    def getPid(self):
        return self.pid;
    def getName(self):
        return self.name
    def getUser(self):
        return self.user
