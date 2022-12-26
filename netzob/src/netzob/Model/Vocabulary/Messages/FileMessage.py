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


class FileMessage(AbstractMessage):
    """Represents a Message found in a file

    >>> msg = FileMessage(b"That's a simple message")
    >>> print(msg.data)
    b"That's a simple message"

    >>> msg = FileMessage(b"hello everyone", file_path="/tmp/server.dat", file_message_number=0)
    >>> print(msg.file_path)
    /tmp/server.dat
    >>> print(msg.file_message_number)
    0

    """

    def __init__(self, data=None, file_path=None, file_message_number=0):
        """
        :param data: the content of the message
        :type data: a :class:`object`
        :param file_path: path of the file where this message comes from
        :type file_path: `str`
        :param file_message_number: the position of the message in its file 
        :type file_message_number: `int`
        """
        super(FileMessage, self).__init__(
            data=data, date=None, source=file_path, destination=None, messageType = "File")

        self.file_path = file_path
        self.file_message_number = file_message_number

    def priority(self):
        """Return the value that will be used to represent the current message when sorted
        with the others.

        :type: int
        """
        
        return self.file_message_number

    @property
    def file_path(self):
        """The path of the file this message comes from

        :type: `str`
        """
        return self.__file_path

    @file_path.setter  # type: ignore
    @typeCheck(str)
    def file_path(self, _file_path):
        self.__file_path = _file_path
        
    @property
    def file_message_number(self):
        """The position of the current message in its file

        :type: `int`
        """

        return self.__file_message_number

    @file_message_number.setter  # type: ignore
    @typeCheck(int)
    def file_message_number(self, _file_message_number):
        if _file_message_number is None:
            raise TypeError("File_number_message cannot be None")
        if _file_message_number < 0:
            raise ValueError("File_number_message must be >= 0")
        
        self.__file_message_number = _file_message_number
