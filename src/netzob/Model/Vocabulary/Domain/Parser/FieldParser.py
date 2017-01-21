#-*- coding: utf-8 -*-

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
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Parser.VariableParser import VariableParser
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath


@NetzobLogger
class FieldParser():
    """Main entry point for the vocabulary parser.
    This class can be use to parse some data against the specification of a field

    >>> from netzob.all import *
    >>> f1 = Field(name="f1", domain=ASCII(nbChars=(1,10)))
    >>> print(f1.domain.svas)
    Ephemeral SVAS
    
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto
    tot
    to
    t

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,4)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("toto.txt", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto.txt
    
    >>> f1 = Field(name="f1", domain=Agg([ASCII("toto"), ASCII(" "), ASCII("tata")]))
    >>> content = TypeConverter.convert("toto tata", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto tata

    >>> f1 = Field(name="f1", domain=Alt([ASCII("toto"), ("tata")]))
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto

    # # Let's illustrate that our parser support multiple results

    >>> f1 = Field(name="f1", domain=Alt([ASCII("toto"), ("to")]))
    >>> content = TypeConverter.convert("toto", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto
    to

    # Yes, the following example is (mostly) the reason for this last year's development :)

    >>> f1 = Field(name="f1", domain=Agg([Alt(["to", "toto"]), Alt(["to", "toto"])]))
    >>> content = TypeConverter.convert("tototo", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    toto
    tototo
    tototo

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,10)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("helloword.txt", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> print(b'\\n'.join([TypeConverter.convert(result.getDataAssignedToField(f1), BitArray, Raw) for result in parsingPaths]).decode("utf-8"))
    helloword.txt

    >>> f1 = Field(name="f1", domain=Agg([ASCII(nbChars=(1,10)), ASCII(".txt")]))
    >>> content = TypeConverter.convert("helloword.tot", ASCII, BitArray)
    >>> parser = FieldParser(f1)
    >>> parser = FieldParser(f1)
    >>> parsingPath = ParsingPath(dataToParse=content, memory=Memory())
    >>> parsingPath.assignDataToField(content, f1)
    >>> parsingPaths = parser.parse(parsingPath)
    >>> next(parsingPaths)
    Traceback (most recent call last):
     ...
    StopIteration


    Below are few tests 

    >>> from netzob.all import *
    >>> message = RawMessage(b"\\xaa\\x00\\xbb")
    >>> f1 = Field(Raw(nbBytes=(0,1)), name="f1")
    >>> f2 = Field(b"\\x00", name="f2")
    >>> f3 = Field(Raw(nbBytes=(0, 2)), name="f3")
    >>> s = Symbol([f1, f2, f3], messages=[message])
    >>> print(s)
    f1      | f2     | f3     
    ------- | ------ | -------
    b'\\xaa' | '\\x00' | b'\\xbb'
    ------- | ------ | -------


    >>> msg1 = b'\\n\\x00aStrongPwd'
    >>> msg2 = b'\\t\\x00myPasswd!'
    >>> messages = [RawMessage(data=sample) for sample in [msg1, msg2]]
    >>> f1 = Field(Raw(nbBytes=(0,1)), name="f1")
    >>> f2 = Field(b"\\x00", name="f2")
    >>> f3 = Field(Raw(nbBytes=(0,11)), name="f3")
    >>> f4 = Field(b"wd", name="f4")
    >>> f5 = Field(Raw(nbBytes=(0,1)), name="f5")
    >>> s = Symbol([f1, f2, f3, f4, f5], messages = messages)
    >>> print(s)
    f1   | f2     | f3         | f4   | f5 
    ---- | ------ | ---------- | ---- | ---
    '\\n' | '\\x00' | 'aStrongP' | 'wd' | '' 
    '\\t' | '\\x00' | 'myPass'   | 'wd' | '!'
    ---- | ------ | ---------- | ---- | ---

    

    """

    def __init__(self, field, lastField=False):
        self.field = field
        self.lastField = lastField

    @typeCheck(ParsingPath)
    def parse(self, parsingPath):
        """Parses the specified content (the remaining data in the parsingPath) against the field definition domain

        It returns the parsing paths
        """
    
        # we retrieve the field definition domain
        domain = self.field.domain

        # and check it exists
        if domain is None:
            raise Exception("No definition domain specified for field '{0}', cannnot parse the content against it.".format(self.field.name))

        # check we have something to parse
        data = parsingPath.getDataAssignedToField(self.field)

        self._logger.debug("Parses '{0}' with field '{1}' specifications".format(data, self.field.name))

        # we assign this data to the field's variable
        parsingPath.assignDataToVariable(data.copy(), self.field.domain)                

        # we create a first VariableParser and uses it to parse the domain
        variableParser = VariableParser(domain)

        for resultParsingPath in variableParser.parse(parsingPath, carnivorous=self.lastField):
            if resultParsingPath.isDataAvailableForVariable(self.field.domain):
                try:
                    resultParsingPath.addResultToField(self.field, resultParsingPath.getDataAssignedToVariable(self.field.domain))
                    yield resultParsingPath
                except Exception as e:
                    self._logger.debug("An error occurred while parsing variable : {}".format(e))
    
    @property
    def field(self):
        """The field that will be use to parse some content

        :type: :class:`netzob.Model.Vocabulary.Field.Field`
        """
        return self.__field

    @field.setter
    @typeCheck(Field)
    def field(self, field):
        if field is None:
            raise ValueError("Field cannot be None")

        self.__field = field



    


