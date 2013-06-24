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
    can be used to build the regex
    """

    def __init__(self):
        self.regex = ""

    @property
    def regex(self):
        return self.__regex

    @regex.setter
    def regex(self, regex):
        self.__regex = regex

    def __str__(self):
        return str(self.regex)

    @staticmethod
    def buildRegexForStaticValue(value):
        """It creates a NetzobRegex which represents
        a regex with the specified static value.

        >>> nRegex = NetzobRegex.buildRegexForStaticValue("Hello netzob")
        >>> print nRegex
        (48656c6c6f206e65747a6f62)
        >>> print nRegex.regex
        (48656c6c6f206e65747a6f62)

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
    >>> regex = NetzobRegex.buildRegexForSizedValue((8, 80))
    >>> print regex
    (*{8,80})

    >>> regex = NetzobRegex.buildRegexForSizedValue((None, None))
    >>> print regex
    (*{0,})

    >>> regex = NetzobRegex.buildRegexForSizedValue((10, None))
    >>> print regex
    (*{10,})

    >>> regex = NetzobRegex.buildRegexForSizedValue((None, 80))
    >>> print regex
    (*{0,80})

    """

    def __init__(self, size):
        self.size = size

    def __updateRegex(self):
        (minSize, maxSize) = self.size
        if maxSize is None:
            maxSize = ''
        self.regex = "(*{" + str(minSize) + "," + str(maxSize) + "})"

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        (minSize, maxSize) = size
        if minSize is None:
            minSize = 0
        if maxSize is not None:
            if minSize < 0 or maxSize < 0:
                raise ValueError("The value min and max cannot be inferior to 0")
            if maxSize <= minSize:
                raise ValueError("The max size must be superior to the min size")
        self.__size = (minSize, maxSize)
        self.__updateRegex()


class NetzobAggregateRegex(NetzobRegex):
    """Represents an aggregate regex.

    >>> from netzob.Common.Utils.NetzobRegex import NetzobRegex
    >>> regex1 = NetzobRegex.buildRegexForStaticValue("hello netzob")
    >>> regex2 = NetzobRegex.buildRegexForStaticValue("42")
    >>> regex = NetzobRegex.buildRegexForAggregateRegexes([regex1, regex2])
    >>> print regex
    ((68656c6c6f206e65747a6f62)(3432))

    """

    def __init__(self, children):
        self.__children = TypedList(NetzobRegex)
        self.children = children

    def __updateRegex(self):
        self.regex = "({0})".format("".join([str(child) for child in self.children]))

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

    >>> from netzob.Common.Utils.NetzobRegex import NetzobRegex
    >>> regex1 = NetzobRegex.buildRegexForStaticValue("hello netzob")
    >>> regex2 = NetzobRegex.buildRegexForStaticValue("42")
    >>> regex = NetzobRegex.buildRegexForAlternativeRegexes([regex1, regex2])
    >>> print regex
    ((68656c6c6f206e65747a6f62)|(3432))

    """

    def __init__(self, children):
        self.__children = TypedList(NetzobRegex)
        self.children = children

    def __updateRegex(self):
        self.regex = "({0})".format("|".join([str(child) for child in self.children]))

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
    >>> regex = NetzobStaticRegex("0A10")
    >>> print regex.regex
    (0a10)
    >>> print regex.staticValue
    0a10

    To illustrate that only an hexastring can be specified

    >>> regex = NetzobStaticRegex("toto")
    Traceback (most recent call last):
    ...
    ValueError: The specified value cannot be parse as an HexaString

    """

    def __init__(self, staticValue):
        self.staticValue = staticValue

    def __updateRegex(self):
        """This method must be called everytime the static
        value is modified"""
        self.regex = "({0})".format(self.staticValue)

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
