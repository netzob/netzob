# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+
import uuid
import time
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
from netzob.Common.Utils.SortableObject import SortableObject
from netzob.Common.Utils.TypedList import TypedList
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.HexaString import HexaString
from netzob.Model.Types.Raw import Raw
from netzob.Model.Vocabulary.Functions.FunctionApplicationTable import FunctionApplicationTable
from netzob.Model.Vocabulary.Functions.VisualizationFunction import VisualizationFunction


@NetzobLogger
class AbstractMessage(SortableObject):
    """Every message must inherits from this class"""

    def __init__(self, data, _id=None, session=None, date=None, source=None, destination=None):
        """
        :parameter data: the content of the message
        :type data: a :class:`object`
        :parameter _id: the unique identifier of the message
        :type _id: :class:`uuid.UUID`
        :keyword session: the session in which the message was captures
        :type session: :class:`netzob.Model.Vocabulary.Session.Session`
        :parameter date: the timestamp of the message
        :type date: a :class:`int`
        :parameter source: the optional source address of the message
        :type source: a :class:`str`
        :parameter destination: the optional destination address of the message
        :type destination: a :class:`str`
        """
        if data is None:
            data = ''
        self.data = data
        self.session = session
        if _id is None:
            _id = uuid.uuid4()
        self.id = _id
        if date is None:
            date = time.mktime(time.gmtime())
        self.__date = date
        self.__source = source
        self.__destination = destination
        self.__visualizationFunctions = TypedList(VisualizationFunction)
        self.__metadata = OrderedDict()
        self.__semanticTags = OrderedDict()

    @typeCheck(AbstractField)
    def isValidForField(self, field):
        """Checks if the specified field can be used
        to parse the current message. It returns a boolean
        that indicates this.

        >>> from netzob.all import *
        >>> f0 = Field(Raw(nbBytes=4))
        >>> f1 = Field(b", hello ", name="F1")
        >>> f2 = Field(Raw(nbBytes=(2,5)), name="F2")
        >>> symbol = Symbol([f0, f1, f2], name="Symbol")
        >>> m2 = RawMessage(b"Toto, hello you", source="server", destination="client")
        >>> m2.isValidForField(symbol)
        True
        >>> m1 = RawMessage(b"Toto, hello !", source="server", destination="client")
        >>> m1.isValidForField(symbol)
        False

        :parameter field: the current message will be parsed with this field
        :type field: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :return: a boolean indicating if the current message can be parsed with the specified field
        :rtype: :class:`bool`

        """
        if field is None:
            raise TypeError("Field cannot be None")

        try:
            DataAlignment.align([self.data], field)
        except:
            return False
        return True

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

    def clearVisualizationFunctions(self):
        """Remove all the visualization functions attached to the current element"""

        while(len(self.__visualizationFunctions) > 0):
            self.__visualizationFunctions.pop()

    def priority(self):
        """Return the value that will be used to represent the current message when sorted
        with the others.

        :type: int
        """
        return int(self.id)

    def __str__(self):
        """Returns a string that describes the message.

        :warning: This string should only considered for debuging and/or fast visualization. Do not
        rely on it since its format can often be modified.
        """

        # Add visualization effects to the data
        functionTable = FunctionApplicationTable([self.data])
        for function in self.visualizationFunctions:
            start = (function.start / 8)
            end = (function.end / 8)
            functionTable.applyFunction(function, start, end)
        tmpData = b"".join(functionTable.getResult()).decode('utf-8')

        # Add header in front of the data
        HLS1 = "\033[0;32m"
        HLE1 = "\033[0;m"
        HLS2 = "\033[1;32m"
        HLE2 = "\033[1;m"
        header = HLS1 + "[{0} {1}{2}{3}->{4}{5}{6}]".format(self.date, HLE1 + HLS2, self.source, HLE2 + HLS1, HLE1 + HLS2, self.destination, HLE2 + HLS1) + HLE1
        return "{0} {1}".format(header, repr(tmpData))
    
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
    def date(self):
        """The date when the message was captured.
        The date must be encoded in the epoch format.

        :type:float
        :raise: a TypeError if date is not valid
        """
        return self.__date

    @date.setter
    @typeCheck(float)
    def date(self, date):
        if date is None:
            raise TypeError("Date cannot be None")
        self.__date = date

    @property
    def source(self):
        """The name or type of the source which emitted
        the current message

        :type: str
        """
        return self.__source

    @source.setter
    @typeCheck(str)
    def source(self, source):
        self.__source = source

    @property
    def destination(self):
        """The name or type of the destination which received
        the current message

        :type: str
        """
        return self.__destination

    @destination.setter
    @typeCheck(str)
    def destination(self, destination):
        self.__destination = destination

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
        for k in list(metadata.keys()):
            self.setMetadata(k, metadata[k])

    @property
    def visualizationFunctions(self):
        """Sorted list of visualization function to attach on message.

        :type: a list of :class:`netzob.Model.Vocabulary.Functions.VisualizationFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__visualizationFunctions

    @visualizationFunctions.setter
    def visualizationFunctions(self, visualizationFunctions):
        self.clearVisualizationFunctions()
        self.visualizationFunctions.extend(visualizationFunctions)

    @property
    def session(self):
        """The session from which message comes from.

        :type: :class:`netzob.Model.Vocabulary.Session.Session`
        """

        return self.__session

    @session.setter
    def session(self, session):
        self.__session = session

    @typeCheck(int, str)
    def addSemanticTag(self, position, tag):
        """Attach the specific semantic tag the specified position
        of the data.

        :parameter position: the position on which the semantic tag is attached
        :type position: :class:`int`
        :parameter tag: the name of the tag
        :type tag: :class:`str`
        """
        if position is None:
            raise TypeError("Position cannot be none")
        if tag is None:
            raise TypeError("Tag cannot be None")

        if position in list(self.semanticTags.keys()):
            tags = self.semanticTags[position]
        else:
            tags = []

        tags.append(tag)
        self.semanticTags[position] = tags

    @property
    def semanticTags(self):
        """Position of identified semantic tags found in the current data.

        :type: :class:`dict` with keys is int (position) and values is a list of str
        """
        return self.__semanticTags

    @semanticTags.setter
    @typeCheck(dict)
    def semanticTags(self, semanticTags):
        if semanticTags is None:
            self.__semanticTags = OrderedDict()

        # check
        for key, value in list(semanticTags.items()):
            if not isinstance(key, int):
                raise TypeError("At least one key is not a valid int position")
            if not isinstance(value, list):
                raise TypeError("At least one value of the provided dict is not a list of string")
            for x in value:
                if not isinstance(x, str):
                    raise TypeError("At least one value of the provided dict is not a list of string")

        self.__semanticTags = semanticTags
