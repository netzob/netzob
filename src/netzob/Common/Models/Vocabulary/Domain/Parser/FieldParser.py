#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Field import Field
from netzob.Common.Models.Vocabulary.Domain.Parser.VariableParser import VariableParser
from netzob.Common.Models.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Common.Models.Vocabulary.Domain.Parser.FieldParserResult import FieldParserResult
from netzob.Common.Models.Vocabulary.Domain.Variables.Memory import Memory


@NetzobLogger
class FieldParser():
    """Main entry point for the vocabulary parser.
    This class can be use to parse some data against the specification of a field

    >>> from netzob.all import *
    >>> f1 = Field(name="f1", domain=ASCII(nbChars=(1,10)))
    >>> print f1.domain.svas
    Ephemeral SVAS
    
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print '\\n'.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('00101110111101100010111011110110'), remaining=bitarray())
    FieldParserResult (consumed=bitarray('001011101111011000101110'), remaining=bitarray('11110110'))
    FieldParserResult (consumed=bitarray('0010111011110110'), remaining=bitarray('0010111011110110'))
    FieldParserResult (consumed=bitarray('00101110'), remaining=bitarray('111101100010111011110110'))

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,4)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("toto.txt", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print '\\n'.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('0010111011110110001011101111011001110100001011100001111000101110'), remaining=bitarray())
    
    >>> f1 = Field(name="f1", domain=Agg([ASCII("toto"), ASCII(" "), ASCII("tata")]))
    >>> content = TypeConverter.convert("toto tata", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print ''.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('001011101111011000101110111101100000010000101110100001100010111010000110'), remaining=bitarray())

    >>> f1 = Field(name="f1", domain=Alt([ASCII("toto"), ("tata")]))
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print ''.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('00101110111101100010111011110110'), remaining=bitarray())

    # Let's illustrate that our parser support multiple results

    >>> f1 = Field(name="f1", domain=Alt([ASCII("toto"), ("to")]))
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print '\\n'.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('00101110111101100010111011110110'), remaining=bitarray())
    FieldParserResult (consumed=bitarray('0010111011110110'), remaining=bitarray('0010111011110110'))

    Yes, the following example is (mostly) the reason for this last year's development :)

    >>> f1 = Field(name="f1", domain=Agg([Alt(["to", "toto"]), Alt(["to", "toto"])]))
    >>> content = TypeConverter.convert("tototo", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print '\\n'.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('00101110111101100010111011110110'), remaining=bitarray('0010111011110110'))
    FieldParserResult (consumed=bitarray('001011101111011000101110111101100010111011110110'), remaining=bitarray())
    FieldParserResult (consumed=bitarray('001011101111011000101110111101100010111011110110'), remaining=bitarray())

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,10)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("helloword.txt", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    True
    >>> print '\\n'.join([str(result) for result in parser.fieldParserResults])
    FieldParserResult (consumed=bitarray('00010110101001100011011000110110111101101110111011110110010011100010011001110100001011100001111000101110'), remaining=bitarray())

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,10)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("helloword.tot", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> print parser.parse(content)
    False

    """

    def __init__(self, field, memory=None):
        self.field = field
        if memory is not None:
            self.memory = memory
        else:
            self.memory = Memory()
            
        self.__clearResults()

    def parse(self, content):
        """Parses the specified content against the field definition domain

        It returns True if the content is valid according to the field definition domain.
        """
        self._logger.debug("Parse '{0}' with field '{1}' specifications".format(content, self.field.name))

        self.__clearResults()
    
        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception("No definition domain specified for field '{0}', cannnot parse the content against it.".format(self.field.name))
        
        # we create a first VariableParser and uses it to parse the domain
        variableParser = self.__createVariableParser(domain)
        variableParser.parse(content)

        # we create as many FieldParserResult as we found valid paths
        for path in variableParser.variableParserPaths:
            # check path
            if content[:len(path.consumedData)] == path.consumedData:
                self.__createFieldParserResult(path)
            else:
                self._logger.debug("{0} didn't consume {1}".format(path, content))
        
        return self.isOk()


    def isOk(self):
        """Returns True if at least one valid FieldParserResult is available"""

        return len(self.fieldParserResults) > 0

    @typeCheck(AbstractVariable)
    def __createVariableParser(self, domain):
        """Create a new variable parser based on current FieldParser"""
        variableParser = VariableParser(domain, self.memory)        
        self.__variableParsers.append(variableParser)
        
        return variableParser

    def __createFieldParserResult(self, path):
        """Create a field parser result based on specified path"""
        if path is None:
            raise Exception("Path cannot be None")

        self.fieldParserResults.append(FieldParserResult(self.field, path.consumedData, path.remainingData))
        
    def __clearResults(self):
        """Prepare for a new parsing by cleaning any previously results"""
        self.fieldParserResults = []
        self.__variableParsers = []

    @property
    def field(self):
        """The field that will be use to parse some content

        :type: :class:`netzob.Common.Models.Vocabulary.Field.Field`
        """
        return self.__field

    @field.setter
    @typeCheck(Field)
    def field(self, field):
        if field is None:
            raise ValueError("Field cannot be None")

        self.__field = field


    @property
    def fieldParserResults(self):
        """The list of parsing results obtained after last call to parse() method

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Domain.Parser.FieldParserResult.FieldParserResult`
        """
        return self.__fieldParserResults

    @fieldParserResults.setter
    def fieldParserResults(self, results):
        if results is None:
            raise ValueError("FieldParserResults cannot be None, it should be an empty list if really you want to clear the results")

        self.__fieldParserResults = results        


    

