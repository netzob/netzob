# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage


class RawMessage(AbstractMessage):
    """Represents a raw Message which is a single message with some content and very few meta-data.

    >>> msg = RawMessage(b"That's a simple message")
    >>> print(msg.data)
    b"That's a simple message"

    >>> msg = RawMessage(b"hello everyone", source="server", destination="client")
    >>> print(msg.source)
    server
    >>> print(msg.destination)
    client
    >>> print(msg.metadata)
    OrderedDict()
    >>> msg.metadata["metadata1"]="value"
    >>> print(msg.metadata)
    OrderedDict([('metadata1', 'value')])

    """

    def __init__(self, data=None, date=None, source=None, destination=None, messageType="Raw"):
        """
        :parameter data: the content of the message
        :type data: a :class:`object`
        """
        super(RawMessage, self).__init__(
            data=data, date=date, source=source, destination=destination, messageType = messageType)

    def priority(self):
        """Return the value that will be used to represent the current message when sorted
        with the others.

        :type: int
        """
        return int(self.date * 1000)
