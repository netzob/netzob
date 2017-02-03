# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.BitArray import BitArray
from netzob.Model.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Parser.FieldParser import FieldParser


class InvalidParsingPathException(Exception):
    def __init__(self, msg):
        super(InvalidParsingPathException, self).__init__(msg)


@NetzobLogger
class MessageParser(object):
    """This class is used to produce the alignment of a message against a symbol
    specification. It can also be used to abstract a message against a symbol


    Below codes illustrates how to parse a message according to a single symbol.

    
    >>> from netzob.all import *
    >>> msg = RawMessage("hello world !")
    >>> msg1 = RawMessage("hello netzob !")
    >>> f0 = Field(name="F0", domain=ASCII(nbChars=(4,5)))
    >>> f1 = Field(name="F1", domain=ASCII(" "))
    >>> f2 = Field(name="F2", domain=Alt([ASCII("world"), ASCII("netzob")]))
    >>> f3 = Field(name="F3", domain=Agg([ASCII(" "), ASCII("!")]))
    >>> s = Symbol(name="S0", fields=[f0, f1, f2, f3])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('0110100001100101011011000110110001101111'), bitarray('00100000'), bitarray('0111011101101111011100100110110001100100'), bitarray('0010000000100001')]
    >>> print(mp.parseMessage(msg1, s))
    [bitarray('0110100001100101011011000110110001101111'), bitarray('00100000'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('0010000000100001')]


    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> data = bitarray("0000110001101110011001010111010001111010011011110110001000000000")
    >>> msg = RawMessage(TypeConverter.convert(data, BitArray, Raw))
    >>> f1 = Field(name="F1", domain=BitArray(nbBits=8))
    >>> f2 = Field(name="F2", domain=ASCII(nbChars=(3,9)))
    >>> f3 = Field(name="F3", domain=BitArray(nbBits=3))
    >>> f4 = Field(name="F4", domain=BitArray(nbBits=5))
    >>> s = Symbol(name="S0", fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('00001100'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('000'), bitarray('00000')]

    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> b = bitarray('01101110011001010111010001111010011011110110001000111011000001100110100001100101011011000110110001101111')
    >>> r = TypeConverter.convert(b, BitArray, Raw)
    >>> msg = RawMessage(r)
    >>> f1 = Field(ASCII(nbChars=(6)), name="F1")
    >>> f2 = Field(";", name="F2")
    >>> f3 = Field(Size(f1), name="F3")
    >>> f4 = Field(ASCII("hello"), name="F4")
    >>> s = Symbol(fields=[f1, f2, f3, f4])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011'), bitarray('00000110'), bitarray('0110100001100101011011000110110001101111')]

    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> b = bitarray('0000011001101110011001010111010001111010011011110110001000111011')
    >>> r = TypeConverter.convert(b, BitArray, Raw)
    >>> msg = RawMessage(r)
    >>> f2 = Field(ASCII(nbChars=(1,20)), name="F2")
    >>> f3 = Field(";", name="F3")
    >>> f1 = Field(Size(f2), name="F1")
    >>> s = Symbol(fields=[f1, f2, f3])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('00000110'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('00111011')]

    # Let's verify the abstraction of intra-relationships

    >>> from netzob.all import *
    >>> b = "netzob > my name is netzob"
    >>> r = TypeConverter.convert(b, ASCII, Raw)
    >>> msg = RawMessage(r)
    >>> f1 = Field(ASCII(nbChars=(1,20)), name="F1")
    >>> f2 = Field(" > my name is ", name="F2")
    >>> f3 = Field(Value(f1), name="F3")
    >>> s = Symbol(fields=[f1, f2, f3])
    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg, s))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('0010000000111110001000000110110101111001001000000110111001100001011011010110010100100000011010010111001100100000'), bitarray('011011100110010101110100011110100110111101100010')]

    # Let's test inter-symbol relationships

    >>> msg1 = RawMessage("my pseudo is: netzob!")
    >>> msg2 = RawMessage("welcome netzob")
    >>> msg3 = RawMessage("netzob > hello")

    >>> f11 = Field(domain=ASCII("my pseudo is: "), name="F11")
    >>> f12 = Field(domain=ASCII(nbChars=(3, 10)), name="F12")
    >>> f13 = Field(domain=ASCII("!"), name="F13")
    >>> s1 = Symbol(fields=[f11, f12, f13], name="PSEUDO")

    >>> f21 = Field(domain=ASCII("welcome "), name="F21")
    >>> f22 = Field(domain=Value(f12), name="F22")
    >>> s2 = Symbol(fields=[f21, f22], name="WELCOME")

    >>> f31 = Field(domain=Value(f12), name="F31")
    >>> f32 = Field(domain=ASCII(" > hello"), name="F32")
    >>> s3 = Symbol(fields=[f31, f32], name="HELLO")

    >>> mp = MessageParser()
    >>> print(mp.parseMessage(msg1, s1))
    [bitarray('0110110101111001001000000111000001110011011001010111010101100100011011110010000001101001011100110011101000100000'), bitarray('011011100110010101110100011110100110111101100010'), bitarray('00100001')]
    >>> print(mp.parseMessage(msg2, s2))
    [bitarray('0111011101100101011011000110001101101111011011010110010100100000'), bitarray('011011100110010101110100011110100110111101100010')]
    >>> print(mp.parseMessage(msg3, s3))
    [bitarray('011011100110010101110100011110100110111101100010'), bitarray('0010000000111110001000000110100001100101011011000110110001101111')]

    """

    def __init__(self, memory=None):
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory

                
    @typeCheck(AbstractMessage, Symbol)
    def parseMessage(self, message, symbol):
        """This method parses the specified message against the specification of the provided symbol.
        It either succeed and returns the alignment of the message or fails and raises an Exception"""
        if symbol is None:
            raise Exception("Specified symbol is None")
        if message is None:
            raise Exception("Specified message is None")

        # self._logger.debug("Parse message '{0}' according to symbol {1}".format(message.id, symbol.name))
        # we only consider the message data
        dataToParse = message.data

        fields = symbol._getLeafFields()
        return next(self.parseRaw(dataToParse, fields))

    @typeCheck(object)
    def parseRaw(self, dataToParse, fields):
        """This method parses the specified raw against the specification of the provided symbol."""
        if dataToParse is None or len(dataToParse) <= 0:
            raise Exception("Specified data to parse is empty (or None)")
        if fields is None:
            raise Exception("Specified fields is None")
        if len(fields) == 0:
            raise Exception("No field specified")

        bitArrayToParse = TypeConverter.convert(dataToParse, Raw, BitArray)

        return self.parseBitarray(bitArrayToParse, fields)        

    def parseBitarray(self, bitArrayToParse, fields, must_consume_everything = True):
        """This method parses the specified bitarray according to the specification of
        the specified fields.

        It returns an iterator over all the valid parsing path that can be found.
        
        """
            
        self._logger.debug("New parsing method executed on {}".format(bitArrayToParse))

        # building a new parsing path
        currentParsingPath = ParsingPath(bitArrayToParse.copy(), self.memory.duplicate())
        currentParsingPath.assignDataToField(bitArrayToParse.copy(), fields[0])

        # field iterator
        i_current_field = 0

        parsingResults = self._parseBitArrayWithField(currentParsingPath, fields, i_current_field, must_consume_everything = must_consume_everything)

        for parsingResult in parsingResults:
            result = []
            for field in fields:
                result.append(parsingResult.getDataAssignedToField(field))

            self.memory = parsingResult.memory

            yield result

        raise InvalidParsingPathException("No parsing path returned while parsing '{}'".format(TypeConverter.convert(bitArrayToParse, BitArray, Raw)))
        
    def _parseBitArrayWithField(self, parsingPath, fields, i_current_field, must_consume_everything = True):
        self._logger.debug("_parseBitArrayWithField executed for field {} with path : {}".format(i_current_field, parsingPath))
        currentField = fields[i_current_field]

        carnivorous_parsing = (i_current_field == len(fields) - 1)
        if must_consume_everything is False:
            carnivorous_parsing = False
        
        fp = FieldParser(currentField, carnivorous_parsing)
        value_before_parsing = parsingPath.getDataAssignedToField(currentField).copy()
        
        for newParsingPath in fp.parse(parsingPath):

            try:
                value_after_parsing = newParsingPath.getDataAssignedToField(currentField)
                remainingValue = value_before_parsing[len(value_after_parsing):].copy()

                if i_current_field < len(fields) - 1 :                    
                    newParsingPath.assignDataToField(remainingValue, fields[i_current_field+1])
                    
                    if must_consume_everything is False:
                        generator = self._parseBitArrayWithField(newParsingPath, fields, i_current_field + 1, must_consume_everything = False)
                    else:
                        generator = self._parseBitArrayWithField(newParsingPath, fields, i_current_field + 1)
                    for x in generator:
                        yield x

                        
                elif not must_consume_everything and len(remainingValue) >= 0:
                    yield newParsingPath
                elif len(remainingValue) == 0:
                    # valid parsing path must consume everything
                    yield newParsingPath
                
            except InvalidParsingPathException:
                pass

        raise StopIteration()
        # InvalidParsingPathException("No parsing path returned while parsing '{}'".format(TypeConverter.convert(value_before_parsing, BitArray, Raw)))
        
    
        

