#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import uuid
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class ChannelDownException(Exception):
    pass


class AbstractChannel(object, metaclass=abc.ABCMeta):

    def __init__(self, isServer, _id=uuid.uuid4()):
        """Constructor for an Abstract Channel

        :parameter isServer: indicates if the channel is a server or not
        :type isServer: :class:`bool`
        :keyword _id: the unique identifier of the channel
        :type _id: :class:`uuid.UUID`
        :raise TypeError if parameters are not valid
        """

        self.isServer = isServer
        self.id = _id

    # OPEN, CLOSE, READ and WRITE methods

    @abc.abstractmethod
    def open(self, timeout=None):
        """Open the communication channel. If the channel is a server, it starts to listen
        and will create an instance for each different client.

        :keyword timeout: the maximum time to wait for a client to connect
        :type timout:
        """
        pass

    @abc.abstractmethod
    def close(self):
        """Close the communication channel."""
        pass

    @abc.abstractmethod
    def read(self, timeout=None):
        """Read the next message on the communication channel.

        @keyword timeout: the maximum time in millisecond to wait before a message can be reached
        @type timeout: :class:`int`
        """
        pass

    @abc.abstractmethod
    def write(self, data):
        """Write on the communication channel the specified data

        :parameter data: the data to write on the channel
        :type data: binary object
        """
        pass

    # Management methods

    @abc.abstractmethod
    def isOpen(self):
        """Returns if the communication channel is open

        :return: the status of the communication channel
        :type: :class:`bool`
        """
        pass

    # Properties

    @property
    def isServer(self):
        """isServer indicates if this side of the channel plays the role of a server.

        :type: :class:`bool`
        """
        return self.__isServer

    @isServer.setter
    @typeCheck(bool)
    def isServer(self, isServer):
        if isServer is None:
            raise TypeError("IsServer cannot be None")
        self.__isServer = isServer

    @property
    def id(self):
        """the unique identifier of the channel

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("ID cannot be None")
        self.__id = _id
