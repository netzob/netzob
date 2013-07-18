# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class AbstractMessage(object):
    """Every message must inherits from this class"""

    def __init__(self, data, _id=None):
        """
        :parameter data: the content of the message
        :type data: a :class:`object`
        :parameter _id: the unique identifier of the message
        :type _id: :class:`uuid.UUID`
        """
        self.data = data
        if _id is None:
            _id = uuid.uuid4()
        self.id = _id
        self.__metadata = dict()

    @typeCheck(str, object)
    def setMetadata(self, name, value):
        """Modify the value of the current metadata which name
        is specified with the provided value.

        :parameter name: the name of the metadata to edit
        :type name: :str
        :parameter value: the new value of the specified metadata
        :type value: object
        :raise TypeError if parameters are not valid and ValueError if the
        specified value is incompatible with the metadata.
        """

        if not self.isValueForMetadataValid(name, value):
            raise ValueError("The value of metadata {0} is not valid.")
        self.__metadata[name] = value

    def isValueForMetadataValid(self, name, value):
        """Computes if the specified value is compatible for the provided name of metadata
        It should be redefined to support specifities of certain metadata

        :parameter name: the name of the metadata
        :type name: str
        :parameter value: the value of the metadata to check
        :type value: object
        :raise TypeError if parameters are not valid"""
        if name is None:
            raise TypeError("name cannot be none")

        return True

    @property
    def id(self):
        """The unique identified of the message

        :type: UUID
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            return TypeError("Id cannot be None")
        self.__id = _id

    @property
    def data(self):
        """The content of the message

        :type: :class:`object`
        """

        return self.__data

    @data.setter
    def data(self, data):
        self.__data = data

    @property
    def metadata(self):
        """The metadata or properties of the message.

        :type: a dict<str, Object>
        """
        return self.__metadata

    @metadata.setter
    @typeCheck(dict)
    def metadata(self, metadata):
        if metadata is None:
            return TypeError("Metadata cannot be None")
        for k in metadata.keys():
            self.setMetadata(k, metadata[k])
