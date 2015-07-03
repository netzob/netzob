# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.TypeConverter import TypeConverter


class Symbol(AbstractField):
    """A symbol represents a common abstraction for all its messages.

    For example, we can create a symbol based on two raw messages

    >>> from netzob.all import *
    >>> m1 = RawMessage("hello world")
    >>> m2 = RawMessage("hello earth")
    >>> fields = [Field("hello "), Field(["world", "earth"])]

    >>> symbol = Symbol(fields, messages=[m1, m2])
    >>> print symbol
    'hello ' | 'world'
    'hello ' | 'earth'

    Another example
    >>> from netzob.all import *
    >>> s = Symbol([Field("hello "), Field(ASCII(nbChars=(0, 10)))])
    >>> s.messages.append(RawMessage("hello toto"))
    >>> print s
    'hello ' | 'toto'

    """

    def __init__(self, fields=None, messages=None, name="Symbol"):
        """
        :keyword fields: the fields which participate in symbol definition
        :type fields: a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Field`
        :keyword messages: the message that represent the symbol
        :type messages: a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :keyword name: the name of the symbol
        :type name: :class:`str`
        """
        super(Symbol, self).__init__(name, None, True)
        self.__messages = TypedList(AbstractMessage)
        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    @typeCheck(Memory, object)
    def specialize(self, memory=None, generationStrategy=None):
        """Specialize and generate an hexastring which content
        follows the fields definitions attached to the field of the symbol.

        >>> from netzob.all import *
        >>> f1 = Field(domain=ASCII(nbChars=5))
        >>> f0 = Field(domain=Size(f1))
        >>> s = Symbol(fields=[f0, f1])
        >>> result = s.specialize()
        >>> print result[0]
        \x05
        >>> print len(result)
        6

        :keyword generationStrategy: if set, the strategy will be used to generate the fields definitions
        :type generaionrStrategy: :class:``

        :return: a generated content represented as a Raw
        :rtype: :class:`str``
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.GenerationException` if an error occurs while generating a message
        """
        from netzob.Common.Models.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(memory=memory)
        spePath = msg.specializeSymbol(self)

        if spePath is not None:
            return TypeConverter.convert(spePath.generatedContent, BitArray, Raw)

    def clearMessages(self):
        """Delete all the messages attached to the current symbol"""
        while(len(self.__messages) > 0):
            self.__messages.pop()

    # Properties

    @property
    def messages(self):
        """A list containing all the messages that this symbol represent.

        :type : a :class:`list` of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        """
        return self.__messages

    @messages.setter
    def messages(self, messages):
        if messages is None:
            messages = []

        # First it checks the specified messages are all AbstractMessages
        for msg in messages:
            if not isinstance(msg, AbstractMessage):
                raise TypeError("Cannot add messages of type {0} in the session, only AbstractMessages are allowed.".format(type(msg)))

        self.clearMessages()
        for msg in messages:
            self.__messages.append(msg)
