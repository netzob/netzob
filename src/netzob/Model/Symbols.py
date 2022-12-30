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
#|       - Alexandre Pigné <alexandre.pigne (a) amossys.fr>                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from collections.abc import Iterable

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Symbol import Symbol

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+


class Symbols(dict):
    """The Symbols class provides a way to store definition of symbols in order
    and also provides a way to get them using their name.

    >>> symbols = Symbols(Symbol(name="s1"), Symbol(name="s2"))
    >>> symbols
    Symbols(s1, s2)
    >>> symbols["s2"].name
    's2'
    """

    def __init__(self, *symbols):
        # type: (Symbol) -> None
        super().__init__()

        # handle iterable at first argument
        if len(symbols) == 1 and isinstance(symbols[0], Iterable):
            symbols = symbols[0]

        for symbol in symbols:
            if not isinstance(symbol, Symbol):
                raise ValueError("Symbols only accept Symbol object, not '{}'"
                                 .format(type(symbol).__name__))
            self[symbol.name] = symbol

    def __iter__(self):
        return iter(self.values())

    def __repr__(self):
        return "Symbols({})".format(', '.join(map(repr, self.values())))
