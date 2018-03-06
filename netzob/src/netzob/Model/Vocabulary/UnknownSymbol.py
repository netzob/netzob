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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger, public_api
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage


@NetzobLogger
class UnknownSymbol(Symbol):
    """An unknown symbol is a special type of symbol that is returned to
    represent a message that cannot be abstracted.

    The UnknownSymbol constructor expects some parameters:

    :param message: The raw message that cannot be abstracted into a symbol.
                    Default value is None.
    :type message: :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`, optional


    The UnknownSymbol class provides the following public variable:

    :var message: The raw message that cannot be abstracted into a symbol.
    :vartype message: :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`


    >>> from netzob.all import *
    >>> u = UnknownSymbol()
    >>> u.name
    "Unknown message ''"


    .. ifconfig:: scope in ('netzob')

       >>> from netzob.all import *
       >>> msg = RawMessage("hello")
       >>> u = UnknownSymbol(msg)
       >>> u.name
       "Unknown message 'hello'"

    """

    @public_api
    def __init__(self, message=None):
        self.message = message
        name_suffix = ""
        if self.message is not None:
            data = self.message.data
            name_suffix = repr(data[:20])

        super(UnknownSymbol, self).__init__(
            fields=None,
            name="Unknown message {}".format(name_suffix),
            messages=[self.message])

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def message(self):
        """This message represents the unknown symbol

        :type: class:`RawMessage`
        """
        return self.__message

    @message.setter  # type: ignore
    @typeCheck(AbstractMessage)
    def message(self, message):
        if message is None:
            message = RawMessage()

        self.__message = message
