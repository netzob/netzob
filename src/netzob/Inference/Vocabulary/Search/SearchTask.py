#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class SearchTask(object):
    """A Search Task is the unitary element used by the search engine
    when executing. Each search task describes a different mutations to search after.
    The data used must be specified as a bitarray.


    >>> from netzob.all import *
    >>> data = TypeConverter.convert("netzob", ASCII, BitArray)
    >>> searchTask = SearchTask(data, "original version")
    >>> print searchTask.description
    original version
    >>> print searchTask.data
    bitarray('011101101010011000101110010111101111011001000110')

    """

    def __init__(self, data, description=None):
        """Create a search task to search for the specified data.

        :parameter data: the data to search after specified in bitarray
        :type data::class:`bitarray.bitarray`

        """

        self.data = data
        self.description = description

    @property
    def data(self):
        """Data that will be searched.

        :type: :class:`netzob.Common.Models.Types.AbstractType.AbstractType`
        """

        return self.__data

    @data.setter
    @typeCheck(bitarray)
    def data(self, data):
        if data is None:
            raise TypeError("Specified data cannot be None")
        self.__data = data

    @property
    def description(self):
        """The description of the search task. Default description is
        "unknown"

        :type: :class:`str`
        """
        return self.__description

    @description.setter
    @typeCheck(str)
    def description(self, description):
        if description is None:
            description = "Unknown"
        self.__description = description
