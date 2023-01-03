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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage


@NetzobLogger
class ChannelDownSymbol(Symbol):
    """A channel down symbol is a special type of symbol that is returned to represent that no messages could be received as related channel was down

    >>> from netzob.all import *
    >>> u = ChannelDownSymbol()
    >>> u.name
    'ChannelDown Symbol'

    >>> from netzob.all import *
    >>> msg = RawMessage("hello")
    >>> u = ChannelDownSymbol(msg)
    >>> u.name
    'ChannelDown Symbol'

    """

    def __init__(self, message=None):
        self.message = message
        super(ChannelDownSymbol, self).__init__(
            fields=None, name="ChannelDown Symbol", messages=[self.message])

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, ChannelDownSymbol)

    @property
    def message(self):
        """This message represents the message could not be sent as channel was down

        :type: class:`RawMessage`
        """
        return self.__message

    @message.setter  # type: ignore
    @typeCheck(AbstractMessage)
    def message(self, message):
        if message is None:
            message = RawMessage()

        self.__message = message
