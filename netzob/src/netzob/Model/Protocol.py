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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import imp
from os.path import join

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Symbols import Symbols
from netzob.Model.Grammar.Automata import Automata


@NetzobLogger
class Protocol(object):
    """The Protocol class provides a wrapper for the state machine model
    and the format messages model (i.e. the permitted symbols) of a
    protocol.

    The Protocol constructor expects some parameters:

    :param name: This parameter is the name of the protocol.
    :param path_zdl: The directory path containing the .zdl files of the format messages and the automaton. Default is None.
    :type name: an :class:`str`, required
    :type path_zdl: an :class:`str`, optional


    The Protocol class provides the following public variables:

    :var name: The name of the protocol.
    :var symbols: The defined symbols for the protocol.
    :var automata: The automaton defined for the protocol.
    :vartype name: :class:`str`
    :vartype symbols: a :class:`dict` where keys are symbol names and values are :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
    :vartype automata: an :class:`Automata <netzob.Model.Grammar.Automata.Automata>`


    If .zdl files are provided, they should follow a specific
    convention to contain the defined symbols and automaton:

    * The .zdl file for the format messages should be named
      ``{PROTOCOL_NAME}_format.zdl``, and should contain a variable
      named :attr:`symbols` that contains a :class:`list` of :class:`Symbol
      <netzob.Model.Vocabulary.Symbol.Symbol>`.
    * The .zdl file for the automaton should be named
      ``{PROTOCOL_NAME}_automata.zdl``, and should contain a variable
      named :attr:`automata` that contains an :class:`Automata
      <netzob.Model.Grammar.Automata.Automata>`.

    The following code describes the instantiation of a new Protocol,
    without .zdl files:

    >>> from netzob.all import *
    >>> icmp = Protocol("ICMP")
    >>> icmp.name
    'ICMP'

    The following code describes the instantiation of a new Protocol
    with provided protocol definition in .zdl files. The automaton is
    retrieved and rendered with a ``dot`` syntax.

    >>> udp = Protocol("UDP", path_zdl="test/resources/files/UDP_example/")
    >>> udp.name
    'UDP'
    >>> udp.symbols
    Symbols(udp)
    >>> dot_code = udp.automata.generateDotCode()
    >>> print(dot_code)  # doctest: +ELLIPSIS
    digraph G {
    "Initial state" [shape=doubleoctagon, label="Initial state", style=filled, fillcolor=white, URL="..."];
    "Channel opened" [shape=ellipse, label="Channel opened", style=filled, fillcolor=white, URL="..."];
    "Initial state" -> "Channel opened" [fontsize=5, label="OpenChannelTransition", URL="..."];
    }

    For visualization purposes, the following lines would generate
    a PNG file with the ``dot`` representation of the automaton::

      fd = open("/tmp/dotcode.dot", "w")
      fd.write(dotCode)
      fd.close()

    And then in a shell::

      $ dot -Tpng -o /tmp/dotcode.png /tmp/dotcode.dot
      $ xdg-open /tmp/dotcode.png

    """

    @public_api
    def __init__(self, name, path_zdl=None):
        self.__name = name
        self.__path_zdl = path_zdl

        # Initialize local variables
        self.__symbols = {}
        self.__automata = None

        # Load protocol from specified path
        if self.path_zdl is not None:
            self._load_zdl_files()

    @staticmethod
    @public_api
    def load_format(path):
        r"""Load and return the symbols contained in the provided ZDL format file.

        :param path: Path of the ZDL format file.
        :type path: :class:`str`
        :return: The list of symbols defined in the ZDL format file.
        :rtype: a :class:`dict` where keys are symbol names and values are :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`

        >>> from netzob.all import *
        >>> symbols = Protocol.load_format("test/resources/files/UDP_example/UDP_format.zdl")
        >>> type(symbols["udp"])
        <class 'netzob.Model.Vocabulary.Symbol.Symbol'>

        """
        modLoaded = imp.load_source("format", path)
        symbols = Symbols(modLoaded.symbols)
        return symbols

    def _load_zdl_files(self):
        format_zdl = join(self.path_zdl, self.name + "_format.zdl")
        automata_zdl = join(self.path_zdl, self.name + "_automata.zdl")

        if len(format_zdl) > 0:
            self._initializeSymbols(format_zdl)

        if len(automata_zdl) > 0:
            self._initializeAutomata(automata_zdl)

    def _initializeSymbols(self, path, modLoaded=None):
        """Parse a dictionary of symbols from a ZDL file.
        """
        if modLoaded is None:
            # Load module from source ZDL file
            modLoaded = imp.load_source("format", path)

        self.symbols = Symbols(modLoaded.symbols)

        if len(self.symbols) == 0:
            raise Exception("No symbol defined in '{}'.".format(path))

    def _initializeAutomata(self, path):
        """Parse an automata from a ZDL file.
        """
        # Load module from source ZDL file
        mod = imp.load_source("automata", path)
        self.automata = mod.automata

    @property
    def name(self):
        """
        The name of the protocol (ex: "ICMP", "HTTP", ...).

        :type: a :class:`str`, read-only
        """
        return self.__name

    @property
    def path_zdl(self):
        """
        The path to the ZDL files.

        :type: a :class:`str`, read-only
        """
        return self.__path_zdl

    # Note: name and path_zdl attributes are read-only, that's why no.setter  # type: ignore is implemented

    @property
    def symbols(self):
        """
        Property (getter.setter  # type: ignore).
        The dict of defined symbols for the protocol.

        :type: a :class:`dict` where keys are symbol string names and values are :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """
        return self.__symbols

    @symbols.setter  # type: ignore
    @typeCheck(dict)
    def symbols(self, symbols):
        self.__symbols = symbols

    @property
    def automata(self):
        """
        Property (getter.setter  # type: ignore).
        The Automata defined for the protocol.

        :type: an :class:`Automata <netzob.Model.Grammar.Automata.Automata>`
        """
        return self.__automata

    @automata.setter  # type: ignore
    @typeCheck(Automata)
    def automata(self, automata):
        self.__automata = automata
