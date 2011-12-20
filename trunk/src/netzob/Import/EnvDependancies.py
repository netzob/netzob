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
import os
import logging
import socket
from uuid import getnode as get_mac_address
import time

#+---------------------------------------------- 
#| EnvDependancies :
#|     Handle environmental dependancies
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class EnvDependancies(object):
    
    #+---------------------------------------------- 
    #| Constructor :
    #+----------------------------------------------   
    def __init__(self):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Import.EnvDependancies.py')
        self.envData = {} # Dict containing environment data

    #+---------------------------------------------- 
    #| retrieveEnvData: 
    #|   Retrieve environmental data,
    #|   like local IP address, Ethernet address, etc.
    #+----------------------------------------------
    def retrieveEnvData(self):
        # OS specific
        self.envData['os_name'] = [ os.uname()[0] ] # for example 'Linux'
        self.envData['os_family'] = [ os.name ] # for example 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'
        self.envData['os_version'] = [ os.uname()[2] ] # result of 'uname -r' under linux
        self.envData['os_arch'] = [ os.uname()[4] ] # result of 'uname -m' under linux

        # User specific
        self.envData['user_home_dir'] = [ os.environ['HOME'] ]
        self.envData['user_name'] = [ os.environ['USERNAME'] ]
        self.envData['user_lang'] = [ os.environ['LANG'] ]

        # System specific
        self.envData['hostname'] = [ socket.gethostname() ]
        self.envData['domainname'] = [ "".join( socket.getfqdn().split(".", 1)[1:] ) ]

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip_address = s.getsockname()[0]
        s.close()

        self.envData['ip_addresses'] = [ "127.0.0.1", ip_address ]
        self.envData['mac_addresses'] = [ hex(int(get_mac_address()))[2:-1] ]

        # Misc        
        self.envData['date'] = [ str(time.time()) ] # elapsed second since epoch in UTC

    #+---------------------------------------------- 
    #| getXML: 
    #|   Retrieve the XML format of the self.envData dict
    #+----------------------------------------------
    def getXML(self):
        res = []
        for (name,value) in self.envData.items():
            res.append( "<envData name=\"" + name + "\" value=\"" + ";".join(value) + "\" />" )
        return "\n".join(res)
