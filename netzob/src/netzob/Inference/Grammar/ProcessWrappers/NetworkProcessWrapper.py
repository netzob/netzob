# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
#| File contributors :                                                       |
#|       - Georges Bossert <gbossert (a) miskin.fr                           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import socket

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Inference.Grammar.ProcessWrappers.ProcessWrapper import ProcessWrapper


@NetzobLogger
class NetworkProcessWrapperMaker(object):
    """This class can be use to instantiate consecutively multiple
    instance of a NetworkProcessWrapper.
    Everytime it is started, a new instance is created.

    """

    def __init__(self, command_line, listen_ip, listen_port, restart_process=True, name=None):
        self.name = name
        self.command_line = command_line
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.restart_process = restart_process
        self.__current_wrapper = None

    def is_ready(self):
        if self.__current_wrapper is None:
            raise Exception("No current wrapper known, cannot stop it")
        return self.__current_wrapper.is_ready()

    def start(self):
        """
        This method creates a NetworkProcessWrapper given the constructor
        parameters and starts it
        """

        if self.__current_wrapper is not None:
            if not self.restart_process:
                return self.__current_wrapper
        
            raise Exception("Cannot start a new Network process wrapper, one already exists")

        self.__current_wrapper = NetworkProcessWrapper(
            name=self.name,
            command_line=self.command_line,
            listen_ip=self.listen_ip,
            listen_port=self.listen_port)

        self.__current_wrapper.start()

    def stop(self, force=False):
        """
        This method stops the current network process wrapper
        """

        if self.__current_wrapper is None:
            raise Exception("No current wrapper known, cannot stop it")

        if force or self.restart_process:
            self.__current_wrapper.stop()
            self.__current_wrapper = None    

@NetzobLogger
class NetworkProcessWrapper(ProcessWrapper):
    """
    This class can be use to wrap a process that listens on the network

    >>> n = NetworkProcessWrapper("./test", listen_ip="127.0.0.1", listen_port=8000)
    >>> print(n)
    Process 'None' (CLI=./test, listen=127.0.0.1:8000)

    """

    def __init__(self, command_line, listen_ip, listen_port, name=None):
        super(NetworkProcessWrapper, self).__init__(command_line=command_line, name=name)
        self.listen_ip = listen_ip
        self.listen_port = listen_port

    def __str__(self):
        if self.alive() and self.__process_pid is not None:
            return "Process '{}' alive since {} (PID={}, CLI={}, listen={}:{}) ".format(self.name, self.started_at, self.__process_pid, self.command_line, self.listen_ip, self.listen_port)
        else:
            return "Process '{}' (CLI={}, listen={}:{})".format(self.name, self.command_line, self.listen_ip, self.listen_port)
    

    def is_ready(self):
        """
        This method returns True, when the wrapped process
        is reachable via its listen ip and ports
        """
        try:
            sock = socket.socket()
            # Reuse the connection
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((self.listen_ip, self.listen_port))
            sock.close()
            return True
        except Exception as e:
            self._logger.debug(e)

        return False
