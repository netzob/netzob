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
import threading
import regex as re
from bitarray import bitarray


#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.MatrixList import MatrixList
from netzob.Common.Utils.NetzobRegex import NetzobAggregateRegex
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken
from netzob.Common.Models.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Common.Models.Vocabulary.Domain.Parser.FieldParser import FieldParser


@NetzobLogger
class DataAlignment(threading.Thread):
    """This class allows to align data given a field
    specification. This class inherits from :class:`threading.Thread` which allows
    to execute it asynchronously but also to execute it in a traditionnal way.

    For instance, below is a very simple example of data alignment executed
    traditionnaly

    >>> from netzob.all import *
    >>> from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
    >>> import random
    >>> import string

    >>> contents = ['hello {0} hello'.format(''.join([random.choice(string.letters) for y in range(random.randint(5,10))])) for x in range(10)]
    >>> fields = [Field("hello ", name="f0"), Field(ASCII(nbChars=(5,10)), name="f1"), Field(" hello", name="f2")]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(contents, symbol, encoded=True)
    >>> print len(alignedData)
    10
    

    >>> # one more fun test case
    >>> data = ['hello {0}, welcome'.format(random.choice(["tototo"])) for x in range(5)]
    >>> # Now we create a symbol with its field structure to represent this type of message
    >>> fields = [Field(ASCII('hello ')), Field(Agg([Alt([ASCII("toto"), ASCII("to")]), Alt([ASCII("to"), ASCII("toto")])])), Field(ASCII(', welcome'))]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(data, symbol)
    >>> print len(alignedData)
    5
    >>> print alignedData
    hello  | tototo | , welcome
    hello  | tototo | , welcome
    hello  | tototo | , welcome
    hello  | tototo | , welcome
    hello  | tototo | , welcome

    >>> # Lets try to align a more complex message
    >>> msg1 = "helloPUTtotoPA343"
    >>> msg2 = "helloGETtototoPA"
    >>> msg3 = "helloPUTtotototoPAdqs4qsd33"
    >>> messages = [msg1, msg2, msg3]
    >>> fh1 = Field("hello", name="f1")
    >>> fh2 = Field(ASCII(nbChars=(3)), name="f4")
    >>> fh3 = Field(Agg([Alt(["toto", "to"]), Alt(["to", "toto"])]), name="f3")
    >>> fb1 = Field(ASCII("PA"), name="f5")
    >>> fb2 = Field(Raw(nbBytes=(0,10)))
    >>> headerFields = [fh1, fh2, fh3]
    >>> bodyFields = [fb1, fb2]

    >>> symbol = Symbol(fields=headerFields+bodyFields)
    >>> alignedData2 = DataAlignment.align(messages, symbol)
    >>> print alignedData2
    hello | PUT | toto     | PA | 343      
    hello | GET | tototo   | PA |          
    hello | PUT | totototo | PA | dqs4qsd33


    """

    def __init__(self, data, field, depth=None, encoded=True, styled=False):
        """Constructor.

        :param data: the list of data that will be aligned, data must be encoded in HexaString
        :type data: a :class:`list` of data to align
        :param field: the format definition that will be user
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :keyword depth: the limit in depth in the format (use None for not limit)
        :type depth: :class:`int`
        :keyword encoded: indicates if the result should be encoded following field definition
        :type encoded: :class:`bool`
        :keyword styled: indicated if the result visualization filter should be applied
        :type styled: :class:`bool`

        """
        self.data = data
        self.field = field
        self.depth = depth
        self.encoded = encoded
        self.styled = styled

    def execute(self):
        """Execute the alignment of data following specified field
        """
        if self.data is None:
            raise TypeError("Data cannot be None")
        if self.field is None:
            raise TypeError("Field cannot be None")

        # Aligned messages are stored in a MatrixList for better display
        result = MatrixList()

        # We retrieve all the leaf fields of the root of the provided field
        rootLeafFields = self.__root._getLeafFields(depth=self.depth)
            
        # if self.__root != self.field:
        #     targetedFieldLeafFields = self.field._getLeafFields(depth=self.depth)
        # else:
        targetedFieldLeafFields = rootLeafFields

        for f in targetedFieldLeafFields:
            self._logger.debug(f.name)

        for d in self.data:
            from netzob.Common.Models.Vocabulary.Domain.Parser.MessageParser import MessageParser
            
            mp = MessageParser()
            #alignedMsg = mp.parseRaw(TypeConverter.convert(d, HexaString, Raw), targetedFieldLeafFields)
            alignedMsg = mp.parseRaw(d, targetedFieldLeafFields)

            alignedEncodedMsg = []
            for ifield, currentField in enumerate(targetedFieldLeafFields):

                # now we apply encoding and mathematic functions
                fieldValue = alignedMsg[ifield]
            
                if self.encoded and len(currentField.encodingFunctions.values()) > 0:
                    for encodingFunction in currentField.encodingFunctions.values():
                        fieldValue = encodingFunction.encode(fieldValue)
                else:
                    fieldValue = TypeConverter.convert(fieldValue, BitArray, Raw)

                if currentField in self.field._getLeafFields(depth=self.depth):
                    alignedEncodedMsg.append(fieldValue)

            result.append(alignedEncodedMsg)

        return result

        
        

    #     We retrieve all the leaf fields of the root of the provided field
    #     rootLeafFields = self.__root._getLeafFields(depth=self.depth)
            
    #     if self.__root != self.field:
    #         targetedFieldLeafFields = self.field._getLeafFields(depth=self.depth)
    #     else:
    #         targetedFieldLeafFields = rootLeafFields

    #     -- debug display
    #     self._logger.debug("Targeted leaf fields: ")
    #     for f in targetedFieldLeafFields:
    #         self._logger.debug("- {0}".format(f.name))
    #     -- debug display
        
    #     we successively parse/align each data
    #     for d in self.data:            
    #         self._logger.debug("[START] Parsing Data : '{0}'".format(d))
    #         (rawParsingResult, encodedParsingResult) = self._parseData(d, rootLeafFields, targetedFieldLeafFields)
    #         self._logger.debug("[END] Parsing Data '{0}' produced '{1}'".format(d, encodedParsingResult))

    #         additionnal check (just to be certain dataParsing equals the data)
    #         if not ''.join(rawParsingResult) in TypeConverter.convert(d, HexaString, Raw):
    #             raise Exception("<!> You found a case which broke our parsing engine: concat alignedData not in original message not '{0}' in '{1}'".format(''.join(rawParsingResult), TypeConverter.convert(d, HexaString, Raw)))
    #         result.append(encodedParsingResult)
            
    #     return result

            
    # def _parseData(self, d, rootLeafFields, targetedFieldLeafFields):
    #     """Internal method that aligns one data according to the provided fields"""
    
    #     self._logger.debug("Data to align: {0}".format(d))
    #     split the message following the regex definition
    #     splittedDatas = self.__splitDataWithRegex(d, rootLeafFields)

    #     first we check if the regex parsing was a success:
    #     we verify the regex has identified a segment for each field
    #     for field in targetedFieldLeafFields:
    #         for splittedData in splittedDatas:
    #             if field.regex.id not in splittedData.keys() or len(splittedData[field.regex.id]) == 0:
    #                 raise Exception("Content of field {0} ({1}) has not been found on message, alignment failed.")

    #             if len(splittedData[field.regex.id]) > 1:
    #                 raise Exception("Multiple values are available for the same field, this is not yet supported.")
        
    #     store all the parsing results
    #     parsingResults = []

    #     we analyze each result of the regex parsing
    #     for splittedData in splittedDatas:
    #         Yes, we create an empty array that contains an empty array
    #         fieldParserPaths[0] => one path in the token-tree. a path = [FieldParserResult0, ....]
    #         fieldParserPaths = [[]] = [[FieldParserResult0, FieldParserResult1, ...], [], []]

    #         we parse the current regex result according to each field token-tree
    #         for ifield, currentField in enumerate(targetedFieldLeafFields):
    #             regex applies on the hexastring level, token-tree applies on the bitarray level, we execute a convertion
    #             fieldContent = TypeConverter.convert(splittedData[currentField.regex.id][0], HexaString, BitArray)

    #             newFieldParserPaths = []

    #             for i_fieldParserPath, fieldParserPath in enumerate(fieldParserPaths):
    #                 we retrieve the remaining data
    #                 remainingData = None
    #                 if len(fieldParserPath) > 0:
    #                     remainingData = fieldParserPath[ifield-1].remainingData

    #                 if remainingData is not None:
    #                     content = remainingData.copy()
    #                     content.extend(fieldContent.copy())
    #                 else:
    #                     content = fieldContent.copy()

    #                 start the field parser
    #                 fieldParser = FieldParser(currentField)
    #                 if fieldParser.parse(content):
    #                     for fieldParserResult in fieldParser.fieldParserResults:
    #                         path = []
    #                         path.extend(fieldParserPath)
    #                         path.append(fieldParserResult)
    #                         newFieldParserPaths.append(path)
    #                 else:
    #                     self._logger.debug("Field parsing failed.")
                            
    #             fieldParserPaths = newFieldParserPaths

    #             if len(fieldParserPaths) == 0:
    #                 raise Exception("Invalid, content: {0}, field: {1}".format(fieldContent, currentField._str_debug()))
            
    #         parsingResults.extend(fieldParserPaths)

    #     remove all the paths where the last field parser result has none empty remaining data
    #     removeItems = []
    #     for parsingResult in parsingResults:
    #         if len(parsingResult[-1].remainingData) != 0:
    #             removeItems.append(parsingResult)

    #     for removeItem in removeItems:
    #         parsingResults.remove(removeItem)
            
    #     parsingResult = None
    #     if len(parsingResults) == 0:
    #         raise Exception("Message cannot be parsed according to fields specification")
    #     if len(parsingResults) > 1:
    #         TODO: new version should support the selection of which parsing result must be retained
    #         self._logger.debug("TODO: multiple parsing results found !")
    #     parsingResult = parsingResults[0]

    #     resultEncoded = []
    #     resultRaw = []
    #     for ifield, currentField in enumerate(targetedFieldLeafFields):
    #         now we apply encoding and mathematic functions
    #         fieldValue = parsingResult[ifield].consumedData  here we have bitarrays
            
    #         if self.encoded and len(currentField.encodingFunctions.values()) > 0:
    #             for encodingFunction in currentField.encodingFunctions.values():
    #                 fieldValue = encodingFunction.encode(fieldValue)
    #         else:
    #             fieldValue = TypeConverter.convert(fieldValue, BitArray, Raw)
        
    #         resultEncoded.append(fieldValue)
    #         resultRaw.append(TypeConverter.convert(parsingResult[ifield].consumedData, BitArray, Raw))
            
    #     return (resultRaw, resultEncoded)

    # @typeCheck(str)
    # def __splitDataWithRegex(self, data, fields):
    #     """Split the specified data in possible field following
    #     the application of the regex

    #     :param data: the data to split must be encoded in hexastring
    #     :type data: :class:`str`
    #     :param fields: the list of fields to use to parse the specified data
    #     :type fields: a list of :class:`netzob.Common.Models.Vocabulary.Field.Field`
    #     """

    #     if data is None:
    #         raise TypeError("data cannot be None")

    #     if fields is None:
    #         raise TypeError("fields cannot be None")

    #     if len(fields) == 0:
    #         raise TypeError("At least one field must be specified")

    #     build the regex
    #     regexes = [field.regex for field in fields]
        
    #     regex = NetzobAggregateRegex(regexes)
                    
    #     self._logger.debug("Regex: {0}".format(regex.finalRegex()))

    #     dynamicDatas = None
    #     try:
    #         Now we apply the regex over the message
    #         compiledRegex = re.compile(regex.finalRegex())
    #         validDynamicDatas = compiledRegex.finditer(data)
    #     except Exception, e:
    #         self._logger.warning("An error occured in the alignment process")
    #         self._logger.warning("The regex of the group doesn't match one of its message")
    #         self._logger.warning("Regex: {0}".format(regex.finalRegex()))
    #         if len(data) > 255:
    #             self._logger.warning("Message: {0}...".format(data[:255]))
    #         else:
    #             self._logger.warning("Message: {0}".format(data))
    #         raise e

    #     results = []
    #     for dynamicDatas in validDynamicDatas:
    #         results.append(dynamicDatas.capturesdict())
    #         Memory optimization offered by regex module
    #         dynamicDatas.detach_string()

    #     self._logger.debug("{0} ways of parsing the message with a regex was found.".format(len(results)))
    #     self._logger.debug(results)
            
    #     return results                

    # Static method
    @staticmethod
    @typeCheck(str, AbstractField, int)
    def align(data, field, depth=None, encoded=True):
        """Execute an alignment of specified data with provided field.
        Data must be provided as a list of hexastring.

        :param data: the data to align as a list of hexastring
        :type data: :class:`list`
        :param field : the field to consider when aligning
        :type: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :keyword depth: maximum field depth to consider (similar to layer depth)
        :type depth: :class:`int`.
        :keyword encoded: set to True if you want the returned result to follow the encoding functions
        :type encoded: :class:`boolean`
        :return: the aligned data
        :rtype: :class:`netzob.Common.Utils.MatrixList.MatrixList`
        """

        dAlignment = DataAlignment(data, field, depth, encoded=encoded)
        return dAlignment.execute()

    # Properties

    @property
    def field(self):
        """The field that contains the definition domain used
        to align data

        :type: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        """
        return self.__field

    @field.setter
    @typeCheck(AbstractField)
    def field(self, field):
        if field is None:
            raise TypeError("Field cannot be None")
        self.__field = field
        # update the root
        root = self.__field
        while root.hasParent():
            root = root.parent
        self.__root = root

    @property
    def depth(self):
        """The depth represents the maximum deepness in the fields definition
        that will be considered when aligning messages.

        If set to None, its no limit.

        :type: :class:`int`
        """
        return self.__depth

    @depth.setter
    @typeCheck(int)
    def depth(self, depth):
        if depth is not None and depth < 0:
            raise ValueError("Depth cannot be <0, use None to specify unlimited depth")

        self.__depth = depth

    @property
    def encoded(self):
        """The encoded defines if it applies the encoding filters on aligned data

        :type: :class:`bool`
        """
        return self.__encoded

    @encoded.setter
    @typeCheck(bool)
    def encoded(self, encoded):
        if encoded is None:
            raise ValueError("Encoded cannot be None")

        self.__encoded = encoded

    @property
    def styled(self):
        """The styled defines if it applies the visu filters on aligned data

        :type: :class:`bool`
        """
        return self.__styled

    @styled.setter
    @typeCheck(bool)
    def styled(self, styled):
        if styled is None:
            raise ValueError("Styled cannot be None")

        self.__styled = styled
