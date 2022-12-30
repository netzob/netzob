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
import zlib

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
class ZLibEncodingFunction(EncodingFunction):
    r"""This encoding function can be used to compress or decompress data in zlib.

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
    >>> f1.addEncodingFunction(ZLibEncodingFunction())
    >>> print(s.str_data())
    f0           | f1                                | f2       
    ------------ | --------------------------------- | ---------
    'Helloworld' | b'x\x9csI,I\x04\x00\x03\x80\x01{' | 'Content'
    'Helloworld' | b'x\x9csI,I\x04\x00\x03\x80\x01{' | 'Content'
    'Helloworld' | b'x\x9csI,I\x04\x00\x03\x80\x01{' | 'Content'
    ------------ | --------------------------------- | ---------

    This function can also be used to display the uncompress version of a zlib field

    >>> m1 = b"hello x\x9csI,I\xe4\x02\x00\x05\x05\x01\x85 !"
    >>> f0 = Field(name="f0", domain=String("hello "))
    >>> f1 = Field(name="f1", domain=Raw(nbBytes=(0, 30)))
    >>> f2 = Field(name="f2", domain=String(" !"))
    >>> s = Symbol(fields = [f0, f1, f2], messages = [RawMessage(m1)])
    >>> print(s.str_data())
    f0       | f1                                       | f2  
    -------- | ---------------------------------------- | ----
    'hello ' | b'x\x9csI,I\xe4\x02\x00\x05\x05\x01\x85' | ' !'
    -------- | ---------------------------------------- | ----
    >>> f1.addEncodingFunction(ZLibEncodingFunction(compress_data = False))
    >>> print(s.str_data())
    f0       | f1       | f2  
    -------- | -------- | ----
    'hello ' | 'Data\n' | ' !'
    -------- | -------- | ----

    """

    def __init__(self, compress_data=True, compression_level=6):
        """Creates a new encoding function that will compress or decompress data with zlib algorithm

        :parameter compress_data: if set to true, this function compress in zlib the original value
        :type compress_data: :class:`bool`
        :parameter compression_level: An integer from 0 to 9 controlling the level of compression; 1 is fastest and produces the least compression, 9 is slowest and produces the most, 0 is no compression. Default value is 6.
        :type compression_level: :class:`int`
        """
        self.compress_data = compress_data
        self.compression_level = compression_level

    def encode(self, data):
        data_raw = TypeConverter.convert(data, BitArray, Raw)

        result = None
        if self.compress_data:
            result = zlib.compress(data_raw, self.compression_level)
        else:
            result = zlib.decompress(data_raw)
            
        return result

    def priority(self):
        """Returns the priority of the current encoding filter."""
        return 100

    @property
    def compress_data(self):
        return self.__compress_data
    
    @compress_data.setter  # type: ignore
    @typeCheck(bool)        
    def compress_data(self, _compress_data):
        self.__compress_data = _compress_data

    @property
    def compression_level(self):
        return self.__compression_level
    
    @compression_level.setter  # type: ignore
    @typeCheck(int)        
    def compression_level(self, _compression_level):
        if _compression_level < 0 or _compression_level > 9:
            raise ValueError("Compression level must be positive and inferior to 10")
        self.__compression_level = _compression_level
        
