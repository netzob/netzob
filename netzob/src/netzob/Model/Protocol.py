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
import imp

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.Automata import Automata


class Protocol(object):
    """The model of a protocol.

    It regroups both a vocabulary and a grammar.

    >>> icmp = Protocol("ICMP")
    >>> icmp.name
    'ICMP'
    >>> icmp.name = "HTTP"
    >>> icmp.name
    'HTTP'

    """

    def __init__(self, name=None, format_zdl=None, automata_zdl=None):
        """
        :keyword name: the name of the protocol
        :type name: an :class:`str`

        """
        self.__name = name
        self.__symbols = {}
        self.__automata = None

        if format_zdl is not None:
            self._initializeSymbols(format_zdl)

        if automata_zdl is not None:
            self._initializeAutomata(automata_zdl)

    def _initializeSymbols(self, path, modLoaded=None):
        """Parse a dictionary of symbols from a ZDL file.
        """

        if modLoaded is None:
            # Load module from source ZDL file
            modLoaded = imp.load_source("format", path)

        # Built dictionary of symbols
        for s in modLoaded.symbols:
            if s.name in self.symbols:
                raise Exception("Multiple symbols have the same name: {}. Symbol name should be unique.".format(s.name))
            self.symbols[s.name] = s

    def _initializeAutomata(self, path):
        """Parse an automata from a ZDL file.
        """

        # Load module from source ZDL file
        mod = imp.load_source("automata", path)

        # Retrieve automata
        self.automata = mod.automata

    @property
    def name(self):
        """
        The name of the protocol ("icmp", "http", ...)

        :type: a :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        self.__name = name

    @property
    def symbols(self):
        return self.__symbols

    @symbols.setter
    @typeCheck(dict)
    def symbols(self, symbols):
        self.__symbols = symbols

    @property
    def automata(self):
        return self.__automata

    @automata.setter
    @typeCheck(Automata)
    def automata(self, automata):
        self.__automata = automata
