#-*- coding: utf-8 -*-

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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import logging
import os

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from functools import wraps

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+

# Definition of the ColorStreamHandler class only if dependency colorama is
# available on the current system.
try:
    from colorama import Fore, Back, Style

    class ColourStreamHandler(logging.StreamHandler):
        """ A colorized output SteamHandler """

        # Some basic colour scheme defaults
        colours = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARN': Fore.YELLOW,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRIT': Back.RED + Fore.WHITE,
            'CRITICAL': Back.RED + Fore.WHITE
        }

        @property
        def is_tty(self):
            """ Check if we are using a "real" TTY. If we are not using a TTY it means that
            the colour output should be disabled.

            :return: Using a TTY status
            :rtype: bool
            """
            try:
                return getattr(self.stream, 'isatty', None)()
            except:
                return False

        def emit(self, record):
            try:
                message = self.format(record)

                if not self.is_tty:
                    self.stream.write(message)
                else:
                    self.stream.write(self.colours[record.levelname] + message
                                      + Style.RESET_ALL)
                self.stream.write(getattr(self, 'terminator', '\n'))
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    has_colour = True
except Exception as e:
    has_colour = False


def NetzobLogger(klass):
    """This class decorator adds (if necessary) an instance
    of the logger (self.__logger) to the attached class
    and removes from the getState the logger.

    """

    # Verify if a logger already exists
    found = False
    for k, v in list(klass.__dict__.items()):
        if isinstance(v, logging.Logger):
            found = True
            break
    if not found:
        klass._logger = logging.getLogger(klass.__name__)
        try:
            klass._logger.setLevel(int(os.environ['NETZOB_LOG_LEVEL']))
        except:
            pass
        handler = ColourStreamHandler(
        ) if has_colour else logging.StreamHandler()
        fmt = '%(relativeCreated)d: [%(levelname)s] %(module)s:%(funcName)s: %(message)s'
        handler.setFormatter(logging.Formatter(fmt))
        klass._logger.addHandler(handler)
        klass._logger.propagate = False

    # Exclude logger from __getstate__
    def getState(self, **kwargs):
        r = dict()
        for k, v in list(self.__dict__.items()):
            if not isinstance(v, logging.Logger):
                r[k] = v
        return r

    def setState(self, dict):
        self.__dict__ = dict
        self.__logger = logging.getLogger(klass.__name__)

    klass.__getstate__ = getState
    klass.__setState__ = setState

    return klass


def typeCheck(*types):
    """Decorator which reduces the amount of code to type-check attributes.

    Its enables the following code replace:
    ::
        @id.setter  # type: ignore
        def id(self, id):
            if not isinstance(id, str):
               raise TypeError("Invalid types for argument id, must be an str")
            self.__id = id

    with:
    ::
        @id.setter  # type: ignore
        @typeCheck(str)
        def id(self, id):
           self.__id = id

    .. note:: set type = "SELF" to check the type of the self parameter
    .. note:: type checking can be bypassed by setting :val:`NETZOB_NO_TYPECHECK`
              as environment variable
    .. warning:: if argument is None, the type checking is not executed on it.

    """

    def _typeCheck_(func):
        def wrapped_f(*args, **kwargs):
            arguments = args[1:]
            if len(arguments) == len(types):
                # Replace "SELF" with args[0] type
                final_types = []
                for type in types:
                    if type == "SELF":
                        final_types.append(args[0].__class__)
                    else:
                        final_types.append(type)

                for i, argument in enumerate(arguments):
                    if argument is not None and not isinstance(argument,
                                                               final_types[i]):
                        raise TypeError(
                            "Invalid type for arguments, expecting: {0} and received {1}".
                            format(', '.join([t.__name__ for t in final_types
                                              ]), argument.__class__.__name__))
            return func(*args, **kwargs)

        if 'NETZOB_NO_TYPECHECK' in os.environ:
            return func
        return wraps(func)(wrapped_f)

    return _typeCheck_


def public_api(func):
    return func
