# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Models.Vocabulary.Domain.Parser.MessageParser import MessageParser, InvalidParsingPathException
from netzob.Common.Models.Vocabulary.Messages.RawMessage import RawMessage

from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Domain.Parser.FieldParser import FieldParser



@NetzobLogger
class FlowParser(object):
    """    In some cases, a message can also represent multiple consecutive messages. For instance, TCP flows embeds
    consecutive payloads with no delimiter. To deal with such case, the `class:MessageParser` can be parametrized to
    enable multiple consecutive symbols to abstract a single message.

    >>> from netzob.all import *
    >>> payload1 = "aabb"
    >>> payload2 = "ccdd"
    >>> message = RawMessage(payload1 + payload2)
    >>> s1 = Symbol(fields=[Field(ASCII("aabb"))], name="s1")
    >>> s2 = Symbol(fields=[Field(ASCII("ccdd"))], name="s2")
    >>> mp = FlowParser()
    >>> result = mp.parseFlow(message, [s1, s2])
    >>> print [(s.name, values) for (s, values) in result]
    [('s1', [bitarray('01100001011000010110001001100010')]), ('s2', [bitarray('01100011011000110110010001100100')])]


    >>> from netzob.all import *
    >>> payload1 = "hello netzob"
    >>> payload2 = "hello zoby"
    >>> message = RawMessage(payload1 + payload2)
    >>> f1 = Field(ASCII("hello "), name="f0")
    >>> f2 = Field(ASCII(nbChars=(1, 10)), name="f1")
    >>> s1 = Symbol(fields=[f1, f2], name="s1")
    >>> fp = FlowParser()
    >>> result = fp.parseFlow(message, [s1])
    >>> print [(s.name, values) for (s, values) in result]
    [('s1', [bitarray('011010000110010101101100011011000110111100100000'), bitarray('011011100110010101110100011110100110111101100010')]), ('s1', [bitarray('011010000110010101101100011011000110111100100000'), bitarray('01111010011011110110001001111001')])]

    
    >>> from netzob.all import *
    >>> content = "hello netzob" * 100
    >>> message = RawMessage(content)
    >>> f1 = Field(ASCII("hello"), name="f1")
    >>> f2 = Field(ASCII(" "), name="f2")
    >>> f3 = Field(ASCII("netzob"), name="f3")
    >>> s1 = Symbol(fields = [f1, f2, f3], name="s1")
    >>> s2 = Symbol(fields = [Field("nawak")], name="s2")
    >>> fp = FlowParser()
    >>> result = fp.parseFlow(message, [s2, s1])
    >>> print [s.name for (s, values) in result]
    ['s1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 's1']




    
    """

    def __init__(self, memory = None):
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory

    @typeCheck(AbstractMessage, list)
    def parseFlow(self, message, symbols):
        """This method parses the specified message against the specification of one or multiple consecutive
        symbol. It returns a list of tuples, one tuple for each consecutive symbol that participate in the flo.
        A tupple is made of the symbol's and its alignment of the message part it applies on.
        If an error occurs, an Exception is raised."""

        if message is None:
            raise Exception("Specified cannot be None")
        if symbols is None or len(symbols) == 0:
            raise Exception("Symbols cannot be None and must be a list of at least one symbol")

        data_to_parse_raw = message.data
        data_to_parse_bitarray = TypeConverter.convert(data_to_parse_raw, Raw, BitArray)
    
        for result in self._parseFlow_internal(data_to_parse_bitarray, symbols, self.memory):
            return result

        raise InvalidParsingPathException("No parsing path returned while parsing '{}'".format(data_to_parse_raw))
    
    def _parseFlow_internal(self, data_to_parse_bitarray, symbols, memory):
        """Parses the specified data"""

        if data_to_parse_bitarray is None or len(data_to_parse_bitarray) == 0:
            raise Exception("Nothing to parse")

        for symbol in symbols:
            self._logger.debug("Parsing '{}' with Symbol '{}'".format(data_to_parse_bitarray, symbol.name))
            flow_parsing_results = []
            try:
                mp = MessageParser(memory = memory)
                results = mp.parseBitarray(data_to_parse_bitarray.copy(),
                                           symbol._getLeafFields(),
                                           must_consume_everything = False)

                for parse_result in results:
                    parse_result_len = sum([len(value) for value in parse_result])                    
            
                    remainings_bitarray = data_to_parse_bitarray[parse_result_len:]

                    if len(remainings_bitarray) > 0:
                        self._logger.debug("Try to parse the remaining data '{}' with another symbol".format(remainings_bitarray))
                        try:    
                            child_flow_parsings = self._parseFlow_internal(remainings_bitarray, symbols, memory.duplicate())
                            for child_flow_parsing in child_flow_parsings:
                                flow_parsing_results = [(symbol, parse_result)] + child_flow_parsing
                            
                                yield flow_parsing_results
                        except InvalidParsingPathException:
                            pass
                    else:
                        flow_parsing_results = [(symbol, parse_result)]
                            
                        yield flow_parsing_results

            except InvalidParsingPathException:
                pass




            
            
