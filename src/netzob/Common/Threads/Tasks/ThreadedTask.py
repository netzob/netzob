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

from threading import Thread
from gi.repository import GObject

from netzob.Common.Threads.Task import Task
from multiprocessing import Queue


class TaskError(Exception):
    pass


class ThreadedTask(Task):
    """Run a function in a new thread and return its output."""
    def __init__(self, fun, *args, **kwargs):
        self.function = (fun, args, kwargs)

    def run(self):
        """Start thread and set callback to get the result value."""
        queue = Queue()
        thread = Thread(target=self._thread, args=(self.function, queue))
        thread.setDaemon(True)
        thread.start()
        self.source_id = GObject.timeout_add(50, self._queue_manager, thread, queue)

    def cancel(self):
        self.function

    def _queue_manager(self, thread, queue):
        if queue.empty():
            if not thread.isAlive():
                # Thread is not active and the queue is empty: something went wrong!
                self.exception_cb(TaskError)
                return False
            return True
        rtype, rvalue = queue.get()
        if rtype == "return":
            self.return_cb(rvalue)
        else:
            self.exception_cb(rvalue)
        return False

    def _thread(self, function, queue):
        fun, args, kwargs = function
        try:
            result = fun(*args, **kwargs)
        except Exception, exception:
            queue.put(("exception", exception))
            raise
        queue.put(("return", result))
