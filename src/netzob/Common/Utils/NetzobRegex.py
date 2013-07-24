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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.HexaString import HexaString


class NetzobRegex(object):
    """Represents a regex describing field boundaries. Static methods
    can be used to build the regex. Don't use the constructor unless you really
    know what you do. Instead we highly recommend the use of the static methods offered to
    build different types of regex.

    If still you want to use the constructor, don't specify the group since it will
    be automaticaly added. For example, if your regex is (.*), only specify .* and forget the
    () that will be added. In addition the constructor will also generate and add the group identifier. Your
    regex will therefore look like : (P<f45689676567987628>.*).

    """

    DEFAULT_REGEX = '.*'

    def __init__(self):
        self.id = 'f' + str(uuid.uuid4().hex)
        self.regex = NetzobRegex.DEFAULT_REGEX

    @property
    def regex(self):
        return self.__regex

    @regex.setter
    @typeCheck(str)
    def regex(self, regex):
        if regex is None:
            raise TypeError("The regex cannot be None")

        self.__regex = "(?P<{0}>{1})".format(self.id, regex)

    @property
    def id(self):
        return self.__id

    @id.setter
    @typeCheck(str)
    def id(self, _id):
        if _id is None:
            raise TypeError("Id cannot be None")
        if len(_id) == 0:
            raise ValueError("Id must be defined (len>0)")
        self.__id = _id

    def __str__(self):
        return str(self.regex)

    @staticmethod
    def buildDefaultRegex():
        """It creates the default regex which means
        we have to knowledge over the format of the field.

        >>> from netzob import *
        >>> import regex as re
        >>> data = "Hello netzob, a default regex grabs everything."
        >>> hexData = TypeConverter.convert(data, ASCII, HexaString)
        >>> nRegex = NetzobRegex.buildDefaultRegex()
        >>> compiledRegex = re.compile(str(nRegex))
        >>> dynamicDatas = compiledRegex.match(hexData)
        >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
        Hello netzob, a default regex grabs everything.

        :return: a .* default NetzobRegex
        :rtype: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
        """
        regex = NetzobRegex()
        regex.regex = '.*'
        return regex

    @staticmethod
    def buildRegexForStaticValue(value):
        """It creates a NetzobRegex which represents
        a regex with the specified Raw static value.

        >>> from netzob import *
        >>> import regex as re
        >>> data = "Hello netzob"
        >>> hexData = TypeConverter.convert(data, ASCII, HexaString)
        >>> nRegex = NetzobRegex.buildRegexForStaticValue(data)
        >>> compiledRegex = re.compile(str(nRegex))
        >>> dynamicDatas = compiledRegex.match(hexData)
        >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
        Hello netzob

        :param value: the static value the regex must represents
        :type value: python raw (will be encoded in HexaString in the regex)
        :return: the regex which represents the specified valued encoed in HexaString
        :type: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`

        """
        hexaStringValue = TypeConverter.convert(value, Raw, HexaString)
        return NetzobStaticRegex(hexaStringValue)

    @staticmethod
    def buildRegexForSizedValue(size):
        return NetzobSizedRegex(size)

    @staticmethod
    def buildRegexForAlternativeRegexes(regexes):
        return NetzobAlternativeRegex(regexes)

    @staticmethod
    def buildRegexForAggregateRegexes(regexes):
        return NetzobAggregateRegex(regexes)


class NetzobSizedRegex(NetzobRegex):
    """Represents an aggregate regex.

    >>> from netzob.Common.Utils.NetzobRegex import NetzobRegex

    >>> from netzob import *
    >>> import regex as re
    >>> data = "Hello netzob"
    >>> hexData = TypeConverter.convert(data, ASCII, HexaString)
    >>> nRegex = NetzobRegex.buildRegexForSizedValue((8*4,8*5))
    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello

    >>> nRegex = NetzobRegex.buildRegexForSizedValue((None, None))
    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello netzob

    >>> nRegex = NetzobRegex.buildRegexForSizedValue((16, None))
    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello netzob

    >>> nRegex = NetzobRegex.buildRegexForSizedValue((None, 80))
    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello netz

    """

    def __init__(self, size):
        super(NetzobSizedRegex, self).__init__()
        self.size = size

    def __updateRegex(self):
        (minSize, maxSize) = self.size
        if maxSize is None:
            maxSize = ''

        self.regex = ".{" + str(minSize) + "," + str(maxSize) + "}"

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        (minSize, maxSize) = size
        if minSize is None:
            minSize = 0
        minSize = minSize / 4
        if maxSize is not None:
            maxSize = maxSize / 4
            if minSize < 0 or maxSize < 0:
                raise ValueError("The value min and max cannot be inferior to 0")
            if maxSize <= minSize:
                raise ValueError("The max size must be superior to the min size")
        self.__size = (minSize, maxSize)
        self.__updateRegex()


class NetzobAggregateRegex(NetzobRegex):
    """Represents an aggregate regex.

    Below is an example of such aggregate regex with two aggregated regexes..

    >>> from netzob import *
    >>> import regex as re
    >>> data = "Hello netzob, what's up ?"
    >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

    >>> regex1 = NetzobRegex.buildRegexForStaticValue("Hello netzob")
    >>> regex2 = NetzobRegex.buildRegexForStaticValue(", what's up ?")
    >>> nRegex = NetzobRegex.buildRegexForAggregateRegexes([regex1, regex2])

    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(regex1.id):dynamicDatas.end(regex1.id)], HexaString, ASCII)
    Hello netzob
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(regex2.id):dynamicDatas.end(regex2.id)], HexaString, ASCII)
    , what's up ?
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello netzob, what's up ?

    """

    def __init__(self, children):
        super(NetzobAggregateRegex, self).__init__()
        self.__children = TypedList(NetzobRegex)
        self.children = children

    def __updateRegex(self):
        self.regex = "".join([str(child) for child in self.children])

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children):
        for child in children:
            if child is None:
                raise TypeError("No child can be None")
        for child in children:
            self.__children.append(child)
        self.__updateRegex()


class NetzobAlternativeRegex(NetzobRegex):
    """Represents an alternative regex.

    >>> from netzob import *
    >>> import random
    >>> import regex as re
    >>> possibleData =["Netzob", "Zoby"]
    >>> data = random.choice(possibleData)
    >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

    >>> regex1 = NetzobRegex.buildRegexForStaticValue("Netzob")
    >>> regex2 = NetzobRegex.buildRegexForStaticValue("Zoby")
    >>> nRegex = NetzobRegex.buildRegexForAlternativeRegexes([regex1, regex2])

    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> matchedData = TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    >>> matchedData in possibleData
    True

    """

    def __init__(self, children):
        super(NetzobAlternativeRegex, self).__init__()
        self.__children = TypedList(NetzobRegex)
        self.children = children

    def __updateRegex(self):
        self.regex = "|".join([str(child) for child in self.children])

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children):
        for child in children:
            if child is None:
                raise TypeError("No child can be None")
        for child in children:
            self.__children.append(child)
        self.__updateRegex()


class NetzobStaticRegex(NetzobRegex):
    """Represents a regex with a static value.

    Example of a static regex:

    >>> from netzob import *
    >>> import regex as re
    >>> data = "Hello netzob !"
    >>> hexData = TypeConverter.convert(data, ASCII, HexaString)

    >>> nRegex = NetzobRegex.buildRegexForStaticValue("Hello netzob !")

    >>> compiledRegex = re.compile(str(nRegex))
    >>> dynamicDatas = compiledRegex.match(hexData)
    >>> print TypeConverter.convert(hexData[dynamicDatas.start(nRegex.id):dynamicDatas.end(nRegex.id)], HexaString, ASCII)
    Hello netzob !

    To illustrate that only an hexastring can be specified

    >>> regex = NetzobStaticRegex("toto")
    Traceback (most recent call last):
    ...
    ValueError: The specified value cannot be parse as an HexaString

    """

    def __init__(self, staticValue):
        super(NetzobStaticRegex, self).__init__()
        self.staticValue = staticValue

    def __updateRegex(self):
        """This method must be called everytime the static
        value is modified"""
        self.regex = self.staticValue

    @property
    def staticValue(self):
        """The static value which current regex represents.

        :type: str: an hexastring
        :raise: TypeError is param not valid
        """
        return self.__staticValue

    @staticValue.setter
    @typeCheck(str)
    def staticValue(self, staticValue):
        if staticValue is None:
            raise TypeError("Static value cannot be None")
        if not HexaString.canParse(staticValue):
            raise ValueError("The specified value cannot be parse as an HexaString")

        self.__staticValue = staticValue.lower()
        self.__updateRegex()
