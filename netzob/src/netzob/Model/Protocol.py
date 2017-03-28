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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.Automata import Automata


class Protocol(object):
    """The model of a protocol.

    It regroups both a vocabulary and a grammar.

    >>> icmp = Protocol("ICMP")
    >>> icmp.name
    'ICMP'

    """

    # Constants
    SYMBOLS = 0
    AUTOMATA = 1

    # Static variables
    definitions = {}

    def __init__(self, name, path_zdl=None):
        """
        :keyword name: the name of the protocol
        :type name: an :class:`str`
        """
        self.__name = name
        self.definition = [{}, None]

        if self.name in Protocol.definitions:
            self.definition = Protocol.definitions[self.name]
        else:
            format_zdl = None
            automata_zdl = None
            Protocol.definitions[self.name] = self.definition

            if path_zdl is not None:
                format_zdl = join(path_zdl, name + "_format.zdl")
                automata_zdl = join(path_zdl, name + "_automata.zdl")

                if len(format_zdl) > 0:
                    self._initializeSymbols(format_zdl)
                    self.definition[Protocol.SYMBOLS] = self.symbols

                if len(automata_zdl) > 0:
                    self._initializeAutomata(automata_zdl)
                    self.definition[Protocol.AUTOMATA] = self.automata

    def _initializeSymbols(self, path, modLoaded=None):
        """Parse a dictionary of symbols from a ZDL file.
        """
        if modLoaded is None:
            # Load module from source ZDL file
            modLoaded = imp.load_source("format", path)

        symbols = {}
        # Built dictionary of symbols
        for s in modLoaded.symbols:
            if s.name in self.symbols:
                raise Exception("Multiple symbols have the same name: {}. "
                                "Symbol name should be unique."
                                .format(s.name))
            symbols[s.name] = s

        if len(symbols) > 0:
            self.definition[Protocol.SYMBOLS] = symbols
        else:
            raise Exception("List of symbols for {} protocol is empty."
                            .format(s.name))

    def _initializeAutomata(self, path):
        """Parse an automata from a ZDL file.
        """
        # Load module from source ZDL file
        mod = imp.load_source("automata", path)
        self.definition[Protocol.AUTOMATA] = mod.automata

    @property
    def name(self):
        """
        The name of the protocol ("icmp", "http", ...)

        :type: a :class:`str`
        :raises: :class:`TypeError`
        """
        return self.__name

    # Note: name attribute is read-only, that's why no setter is implemented

    @property
    def symbols(self):
        if self.name in Protocol.definitions:
            if Protocol.definitions[self.name][Protocol.SYMBOLS] is not None:
                return Protocol.definitions[self.name][Protocol.SYMBOLS]
            else:
                return {}
        else:
            return {}

    @symbols.setter
    @typeCheck(dict)
    def symbols(self, symbols):
        Protocol.definitions[self.name][Protocol.SYMBOLS] = symbols

    @property
    def automata(self):
        if self.name in Protocol.definitions:
            return Protocol.definitions[self.name][Protocol.AUTOMATA]
        else:
            return None

    @automata.setter
    @typeCheck(Automata)
    def automata(self, automata):
        Protocol.definitions[self.name][Protocol.AUTOMATA] = automata
