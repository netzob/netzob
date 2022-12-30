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
from threading import Thread, Event
import shlex
from subprocess import Popen, PIPE
from queue import Queue, Empty
import os
import signal
from datetime import datetime

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger


@NetzobLogger
class NonBlockingStreamReader:
    """
    A non blocking stream reader used to consume
    output buffers of the wrapped process
    """

    def __init__(self, stream):
        """
        The constructor of the stream

        :param stream the stream to read from. Usually a process' stdout or stderr.
        
        """

        self._s = stream
        self._q = Queue()
        self.__stopEvent = Event()

        def _populateQueue(stream, queue):
            """
            Collect lines from 'stream' and put them in 'queue'.
            """

            while not self.__stopEvent.isSet():
                line = stream.readline()
                if line:
                    queue.put(line)

        self._t = Thread(target = _populateQueue, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(
                block = timeout is not None,
                timeout = timeout)
        except Empty:
            return None

    def stop(self):
        self.__stopEvent.set()

class UnexpectedEndOfStream(Exception): pass


@NetzobLogger
class ProcessWrapper(Thread):
    """A wrapper for a targeted process.
    
    It can be use to start a process, collects its IO and finally stop it.

    # >>> import time
    # >>> p = ProcessWrapper(name='List current directory', command_line='ls .')
    # >>> print(p)
    # List current directory (CLI=ls .)
    # >>> p.start()
    # >>> while p.alive(): 
    # ...    time.sleep(1)
    # >>> time.sleep(2)
    # >>> p.stop()
    # >>> len(p.outputs) > 0
    # True


    """

    def __init__(self, command_line, name=None):
        """
        The constructor of a ProcessWrapper. 

        :param command_line: command line to start the process
        :type command_line: str
        :param name: name of the wrapped process
        :type name: str
        """
        Thread.__init__(self)
        self.__flag_stop = False
        self.__process_pid = None
        self.__process = None
        
        self.name = name
        self.command_line = command_line
        self.started_at = None

        self.outputs = []

    def __str__(self):
        if self.alive() and self.__process_pid is not None:
            return "{} alive since {} (PID={}, CLI={}) ".format(self.name, self.started_at, self.__process_pid, self.command_line)
        else:
            return "{} (CLI={})".format(self.name, self.command_line)
    
    def run(self):
        """
        This method is triggered when the thread is started. It triggers
        the execution of the wrapped process
        """
        
        self._logger.info("Starting process '{}' ({})".format(self.name, self.command_line))

        args = shlex.split(self.command_line)
        self.__process = Popen(args, stdout=PIPE, stderr=PIPE, shell=False)            
        self.__process_pid = self.__process.pid
        self.started_at = datetime.utcnow()

        self._logger.debug("Process {} started (PID={})".format(self.name, self.__process_pid))

        # while not requested to stop (see __flag_stop), it collects
        # stdout and sterr streams
        streamReader_stdout = NonBlockingStreamReader(self.__process.stdout)
        streamReader_stderr = NonBlockingStreamReader(self.__process.stderr)

        while not self.__flag_stop:
            output = streamReader_stdout.readline(0.01)
            if output:
                self.outputs.append(output)                
                self._logger.info(output.strip())
            error = streamReader_stderr.readline(0.01)
            if error:
                self._logger.error(error.strip())
                self.outputs.append(error)
                
        streamReader_stdout.stop()
        streamReader_stderr.stop()
            
    def stop(self):
        """
        This method stops the wrapped process.

        To achieve this, it first raises a flag to stop the stream readers
        and then kills the process.
        """

        self.__flag_stop = True
        
        self._logger.info("Stopping process '{}' (PID={})".format(self.name, self.__process_pid))

        if self.__process is not None:
            try:
                self.__process.kill()
            except Exception as e:
                self._logger.error("An error occurred while stopping process '{}': {}".format(self.name, e))
        else:
            self._logger.warn("No process named '{}' to stop".format(self.name))

        if self.__process_pid is not None:            
            os.kill(self.__process_pid, signal.SIGKILL)
            self._logger.debug("A SIGKILL signal triggered for process '{}' (PID={})".format(self.name, self.__process_pid))
        else:
            self._logger.warn("No process PID '{}' to stop".format(self.__process_pid))

        
    def alive(self):
        """
        This method returns True if the wrapped process is alive.

        """

        if self.__process is None:
            return False

        return self.__process.is_alive()
