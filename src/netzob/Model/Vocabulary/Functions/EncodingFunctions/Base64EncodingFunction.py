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
#|       - Georges Bossert <gbossert@miskin.fr>                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import base64

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, typeCheck
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType


@NetzobLogger
class Base64EncodingFunction(EncodingFunction):
    r"""This encoding function can be used to encode or decode data in base64.

    >>> from netzob.all import *
    >>> f0 = Field(name="f0", domain=String("Helloworld"))
    >>> f1 = Field(name="f1", domain=String("Data"))
    >>> f2 = Field(name="f2", domain=String("Content"))
    >>> s = Symbol(fields=[f0, f1, f2])
    >>> s.messages = [RawMessage(next(s.specialize()))]*3
    >>> print(s.str_data())
    f0           | f1     | f2       
    ------------ | ------ | ---------
    'Helloworld' | 'Data' | 'Content'
    'Helloworld' | 'Data' | 'Content'
    'Helloworld' | 'Data' | 'Content'
    ------------ | ------ | ---------
    >>> f1.addEncodingFunction(Base64EncodingFunction())
    >>> print(s.str_data())
    f0           | f1         | f2       
    ------------ | ---------- | ---------
    'Helloworld' | 'RGF0YQ==' | 'Content'
    'Helloworld' | 'RGF0YQ==' | 'Content'
    'Helloworld' | 'RGF0YQ==' | 'Content'
    ------------ | ---------- | ---------

    This function can also be used to display the decoded version of a base64 field

    >>> m1 = "hello YWxs !"
    >>> m2 = "hello bXkgbG9yZA== !"    
    >>> m3 = "hello d29ybGQ= !"
    >>> f0 = Field(name="f0", domain=String("hello "))
    >>> f1 = Field(name="f1", domain=String(nbChars=(0, 20)))
    >>> f2 = Field(name="f2", domain=String(" !"))
    >>> s = Symbol(fields = [f0, f1, f2], messages = [RawMessage(m1), RawMessage(m2), RawMessage(m3)])
    >>> print(s.str_data())
    f0       | f1             | f2  
    -------- | -------------- | ----
    'hello ' | 'YWxs'         | ' !'
    'hello ' | 'bXkgbG9yZA==' | ' !'
    'hello ' | 'd29ybGQ='     | ' !'
    -------- | -------------- | ----
    >>> f1.addEncodingFunction(Base64EncodingFunction(encode_data = False))
    >>> print(s.str_data())
    f0       | f1        | f2  
    -------- | --------- | ----
    'hello ' | 'all'     | ' !'
    'hello ' | 'my lord' | ' !'
    'hello ' | 'world'   | ' !'
    -------- | --------- | ----

    """

    def __init__(self, encode_data=True):
        """Creates a new encoding function that will encode or decode data with base64

        :parameter encode_data: if set to true, this function encodes in base64 the original value
        :type encode_data: :class:`bool`
        """
        self.encode_data = encode_data

    def encode(self, data):
        data_raw = TypeConverter.convert(data,BitArray,Raw)
        result = None
        if self.encode_data:
            result = base64.b64encode(data_raw)
        else:
            result = base64.b64decode(data_raw)
        return result

    def priority(self):
        """Returns the priority of the current encoding filter."""
        return 100

    @property
    def encode_data(self):
        return self.__encode_data
    
    @encode_data.setter  # type: ignore
    @typeCheck(bool)        
    def encode_data(self, _encode_data):
        self.__encode_data = _encode_data
