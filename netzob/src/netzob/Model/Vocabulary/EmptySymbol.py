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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage


class EmptySymbol(Symbol):
    """An empty symbol is a special type of symbol principaly used by the simulator.
    It represents the fact of having nothing received or to have nothing to send.

    The EmptySymbol constructor expects some parameters:

    :param receptionTimeout: The time above which no reception of
                             message triggers the reception of an
                             :class:`EmptySymbol
                             <netzob.Model.Vocabulary.EmptySymbol.EmptySymbol>`. Default
                             value is 5000. ms.
    :type receptionTimeout: a :class:`float`, optional


    Basic usage:

    >>> from netzob.all import *
    >>> e = EmptySymbol()

    """

    def __init__(self, receptionTimeout=None):
        super(EmptySymbol, self).__init__(
            fields=None, name="Empty Symbol", messages=[RawMessage()])
        if receptionTimeout is None:
            receptionTimeout = EmptySymbol.defaultReceptionTimeout()

        self.receptionTimeout = receptionTimeout

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, EmptySymbol)

    def __ne__(self, other):
        if other is None:
            return True
        return not isinstance(other, EmptySymbol)

    def __repr__(self):
        return "Empty Symbol"

    def __str__(self):
        return "Empty Symbol"

    @property
    def receptionTimeout(self):
        """This timeout represent how many milliseconds of no activity
        represents the reception of an empty symbol.

        :type: class:`float`
        """
        return self.__receptionTimeout

    @receptionTimeout.setter
    @typeCheck(float)
    def receptionTimeout(self, receptionTimeout):
        if receptionTimeout is None:
            raise TypeError("Reception timeout cannot be None")
        if receptionTimeout < 0:
            raise ValueError("Reception timeout must be positive")

        self.__receptionTimeout = receptionTimeout

    @staticmethod
    def defaultReceptionTimeout():
        """Returns the default reception timeout representing
        an empty symbol.

        :return: the default reception timeout in milliseconds
        :rtype: :class:`float`
        """
        return 5000.
