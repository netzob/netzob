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
import subprocess

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.Process import Process


#+---------------------------------------------------------------------------+
#| ExecutionContext :
#|    A set of methods to extract the current
#|    context of the execution (processes,
#|    env vars, ...)
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class ExecutionContext(object):
  
    def __init__(self):
        pass
    
    @staticmethod
    def getCurrentProcesses():
        result = []
        ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
        processes = ps.split('\n')
        # this specifies the number of splits, so the splitted lines
        # will have (nfields+1) elements
        nfields = len(processes[0].split()) - 1
        for row in processes[1:]:
            infos = row.split(None, nfields)
            if len(infos) > 1 :
                user = infos[0]
                pid = infos[1]
                cmd = infos[len(infos) - 1]
                process = Process(cmd, pid, user)
                result.append(process)
            
        return result
