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
import traceback

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


@NetzobLogger
class DataAlignment(threading.Thread):
    """This class allows to align data given a field
    specification. This class inherits from :class:`threading.Thread` which allows
    to execute it asynchronously but also to execute it in a traditionnal way.

    For instance, below is a very simple example of data alignment executed
    traditionnaly

    >>> from netzob.all import *
    >>> from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
    >>> # Create 10 data which follows format : 'hello '+random number of [5-10] digits+' welcome'.
    >>> data = [TypeConverter.convert('hello {0}, welcome'.format(''.join([str(y) for y in range(0, 10)])), Raw, HexaString) for x in range(0, 10)]
    >>> # Now we create a symbol with its field structure to represent this type of message
    >>> fields = [Field('hello '), Field(ASCII(nbChars=(5,10))), Field(', welcome')]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(data, symbol, encoded=True)
    >>> print len(alignedData)
    10
    >>> print alignedData
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome
    hello  | 0123456789 | , welcome

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

        result = MatrixList()

        rootLeafFields = self.__root._getLeafFields(depth=self.depth)
        if self.__root != self.field:
            targetedFieldLeafFields = self.field._getLeafFields(depth=self.depth)
        else:
            targetedFieldLeafFields = rootLeafFields

        for d in self.data:
            self._logger.debug("Data to align: {0}".format(d))
            try:
                # split the message following the regex definition
                splittedData = self.__splitDataWithRegex(d, rootLeafFields)
                self._logger.debug("Splitted data = {0}".format(splittedData))

                # apply the field definition on each slice
                remainingData = ''
                fieldsValue = []
                rToken = VariableReadingToken()

                for field in targetedFieldLeafFields:
                    self._logger.debug("Target leaf field : {0}({1})".format(field.name, field.__class__))
                    if field.regex.id not in splittedData.keys() or len(splittedData[field.regex.id]) == 0:
                        raise Exception("Content of field {0} ({1}) has not been found on message, alignment failed.")

                    if len(splittedData[field.regex.id]) > 1:
                        raise Exception("Multiple values are available for the same field, this is not yet supported.")

                    data = splittedData[field.regex.id][0]
                    fieldData = remainingData + data
                    rToken.setValueForVariable(field.domain, TypeConverter.convert(fieldData, HexaString, BitArray))

                    (value, remainingData) = self.__applyFieldDefinition(field, rToken)
                    rToken.setValueForVariable(field.domain, TypeConverter.convert(fieldData, HexaString, BitArray))

                    fieldsValue.append(value)

                if len(remainingData) > 0:
                    raise Exception("The data has not be fully consummed by the field definition.")
                result.append(fieldsValue)
            except Exception, e:
                tb = traceback.format_exc()
                self._logger.warning("An exception occurred while aligning a data : {0}".format(e))
                self._logger.warning(tb)
                raise e

        return result

    @typeCheck(AbstractField)
    def __applyFieldDefinition(self, field, rToken):
        """This method applies the domain parser associated with the specified field on the
        provided data. It returns a tupple which indicates the consummed data and the remainning data
        after the application of the field domain on the data.

        :param data: the data to parse with the field definition
        :type data: :class:`str` of hexastring
        :param field: the field from which we consider the domain to parse the data
        :type field: :class:`netzob.Common.Models.Vocabulary.Field.Field`
        :return: a tuple indicating the consummed data and the remaining data.
        :rtype: a tuple of :class:`str`, :class:`str`
        :raise Exception if something failed while parsing the data with the field domain.

        """
        originalValue = rToken.getValueForVariable(field.domain)

        self._logger.debug("Apply Field {0} ({1})".format(field.name, field.domain))
        field.domain.read(rToken)

        if not rToken.Ok:
            raise Exception("The field specification does not allow to parse data.")

        readValue = rToken.getValueForVariable(field.domain)

        if self.encoded:
            consummedData = self.__applyEncodingFunctionsOnField(readValue, field, rToken)
        else:
            consummedData = TypeConverter.convert(readValue, BitArray, Raw)

        remainingData = TypeConverter.convert(originalValue[len(readValue):], BitArray, HexaString)
        self._logger.debug("Sucessfuly parsed data, Consummed : {0}, remainingData: {1}".format(consummedData, remainingData))

        return (consummedData, remainingData)

    @typeCheck(bitarray, AbstractField, VariableReadingToken)
    def __applyEncodingFunctionsOnField(self, data, field, readingToken):
        """Encodes the aligned data using the definition of the field
        and of its variables.
        The expected behavior is to encode the data with the default
        encoding filter which is the DomainEncodingFunction that encode
        data following the domain of the used variables to parse.

        :parameter data: the data to encode
        :type data: :class:`bitarray`
        :parameter field: the field from which the data belongs
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :parameter readingToken: the reading token used to parse provided data
        :type readingToken: :class:`netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken.VariableReadingToken`
        :return: the encoded data
        :rtype: :class:`str`
        """

        if field is None:
            raise TypeError("The field cannot be None.")
        if data is None:
            raise TypeError("The data cannot be None.")

        if not readingToken.isValueForVariableAvailable(field.domain):
            raise Exception("There are no value associated with the field, impossible to encode it.")

        currentField = field
        encodingFunctions = None
        while encodingFunctions is None or len(encodingFunctions) == 0:
            encodingFunctions = currentField.encodingFunctions
            if currentField.parent is None:
                break
            currentField = currentField.parent

        if encodingFunctions is None or len(encodingFunctions) == 0:
            encodingFunction = EncodingFunction.getDefaultEncodingFunction()
            encodedValue = encodingFunction.encode(field, readingToken)
        else:
            for encodingFunction in encodingFunctions.values():
                encodedValue = encodingFunction.encode(field, readingToken)

        return str(encodedValue)

    @typeCheck(str)
    def __splitDataWithRegex(self, data, fields):
        """Split the specified data in possible field following
        the application of the regex

        :param data: the data to split must be encoded in hexastring
        :type data: :class:`str`
        :param fields: the list of fields to use to parse the specified data
        :type fields: a list of :class:`netzob.Common.Models.Vocabulary.Field.Field`
        """

        if data is None:
            raise TypeError("data cannot be None")

        if fields is None:
            raise TypeError("fields cannot be None")

        if len(fields) == 0:
            raise TypeError("At least one field must be specified")

        # build the regex
        regexes = [field.regex for field in fields]
        regex = NetzobAggregateRegex(regexes)

        dynamicDatas = None
        try:
            # Now we apply the regex over the message
            compiledRegex = re.compile(regex.finalRegex())
            dynamicDatas = compiledRegex.match(data)
        except Exception, e:
            self._logger.warning("An error occured in the alignment process")
            raise e

        if dynamicDatas is None:
            self._logger.warning("The regex of the group doesn't match one of its message")
            self._logger.warning("Regex: {0}".format(regex.finalRegex()))
            if len(data) > 255:
                self._logger.warning("Message: {0}...".format(data[:255]))
            else:
                self._logger.warning("Message: {0}".format(data))
            raise Exception("The regex of the group doesn't match one of its message")

        result = dynamicDatas.capturesdict()

        # Memory optimization offered by regex module
        dynamicDatas.detach_string()

        return result

    # Static method
    @staticmethod
    @typeCheck(str, AbstractField, int)
    def align(data, field, depth=None, encoded=False):
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
