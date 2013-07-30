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
import threading
import regex as re

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
from netzob.Common.Models.Vocabulary.Domain.Variables.VariableProcessingTokens.VariableReadingToken import VariableReadingToken


@NetzobLogger
class DataAlignment(threading.Thread):
    """This class allows to align data given a field
    specification. This class inherits from :class:`threading.Thread` which allows
    to execute it asynchronously but also to execute it in a traditionnal way.

    For instance, below is a very simple example of data alignment executed
    traditionnaly

    >>> from netzob import *
    >>> import random
    >>> # Create 10 data which follows format : 'hello '+random number of [5-10] digits+' welcome'.
    >>> data = [TypeConverter.convert('hello {0}, welcome'.format(''.join([str(random.randint(0,9)) for y in range(0, random.randint(5,10))])), Raw, HexaString) for x in range(0, 10)]
    >>> # Now we create a symbol with its field structure to represent this type of message
    >>> fields = [Field('hello '), Field(Decimal(size=(5,10))), Field(', welcome')]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(data, symbol)
    >>> print len(alignedData)
    10

    """

    def __init__(self, data, field, depth=None, encoded=False, styled=False):
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

        rootLeafFields = self.__extractSubFields(self.__root)
        if self.__root != self.field:
            targetedFieldLeafFields = self.__extractSubFields(self.field)
        else:
            targetedFieldLeafFields = rootLeafFields

        for d in self.data:
            try:
                # split the message following the regex definition
                splittedData = self.__splitDataWithRegex(d, rootLeafFields)
                self._logger.debug("Splitted data = {0}".format(splittedData))

                # apply the field definition on each slice
                remainingData = ''
                fieldsValue = []
                for field in targetedFieldLeafFields:

                    if field.regex.id not in splittedData.keys() or len(splittedData[field.regex.id]) == 0:
                        raise Exception("Content of field {0} ({1}) has not been found on message, alignment failed.")

                    if len(splittedData[field.regex.id]) > 1:
                        raise Exception("Multiple values are available for the same field, this is not yet supported.")

                    data = splittedData[field.regex.id][0]
                    (value, remainingData) = self.__applyFieldDefinition(remainingData + data, field)
                    fieldsValue.append(value)

                if len(remainingData) > 0:
                    raise Exception("The data has not be fully consummed by the field definition.")
                result.append(fieldsValue)
            except Exception, e:
                self._logger.warning("An exception occurred while aligning a data : {0}".format(e))
                raise e

        return result

    @typeCheck(str, AbstractField)
    def __applyFieldDefinition(self, data, field):
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
        self._logger.debug("Apply field {0} on {1}".format(field.name, data))
        binValue = TypeConverter.convert(data, HexaString, BitArray)
        rToken = VariableReadingToken(value=binValue)
        field.domain.read(rToken)

        if not rToken.Ok:
            raise Exception("Impossible to parse the specified data with the field specifications")

        consummedData = TypeConverter.convert(binValue[:rToken.index], BitArray, HexaString)
        remainingData = TypeConverter.convert(binValue[rToken.index:], BitArray, HexaString)
        self._logger.debug("Consummed : {0}, remainingData: {1}".format(consummedData, remainingData))

        return (consummedData, remainingData)

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
            compiledRegex = re.compile(str(regex))
            dynamicDatas = compiledRegex.match(data)
        except Exception, e:
            self._logger.warning("An error occured in the alignment process")
            raise e

        if dynamicDatas is None:
            self._logger.warning("The regex of the group doesn't match one of its message")
            self._logger.warning("Regex: {0}".format(regex))
            self._logger.warning("Message: {0}...".format(data[:255]))
            raise Exception("The regex of the group doesn't match one of its message")

        result = dynamicDatas.capturesdict()

        # Memory optimization offered by regex module
        dynamicDatas.detach_string()

        return result

    def __extractSubFields(self, field, currentDepth=0):

        """Extract the leaf fields to consider regarding the specified depth

        >>> from netzob import *
        >>> field = Field("hello", name="F0")
        >>> da = DataAlignment(None, field, depth=None)
        >>> print [f.name for f in da._DataAlignment__extractSubFields(field)]
        ['F0']

        >>> field = Field(name="L0")
        >>> headerField = Field(name="L0_header")
        >>> payloadField = Field(name="L0_footer")
        >>> footerField = Field(name="L0_footer")

        >>> fieldL1 = Field(name="L1")
        >>> fieldL1_header = Field(name="L1_header")
        >>> fieldL1_payload = Field(name="L1_payload")
        >>> fieldL1.children = [fieldL1_header, fieldL1_payload]

        >>> payloadField.children = [fieldL1]
        >>> field.children = [headerField, payloadField, footerField]

        >>> da = DataAlignment(None, field, depth=None)
        >>> print [f.name for f in da._DataAlignment__extractSubFields(field)]
        ['L0_header', 'L1_header', 'L1_payload', 'L0_footer']

        >>> da = DataAlignment(None, field, depth=0)
        >>> print [f.name for f in da._DataAlignment__extractSubFields(field)]
        ['L0']

        >>> da = DataAlignment(None, field, depth=1)
        >>> print [f.name for f in da._DataAlignment__extractSubFields(field)]
        ['L0_header', 'L0_footer', 'L0_footer']

        >>> da = DataAlignment(None, field, depth=2)
        >>> print [f.name for f in da._DataAlignment__extractSubFields(field)]
        ['L0_header', 'L1', 'L0_footer']

        :return: the list of leaf fields
        :rtype: :class:`list` of :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`.
        """

        if field is None:
            raise Exception("No field seems available")

        if len(field.children) == 0 or currentDepth == self.depth:
            return [field]

        fields = []
        for children in field.children:
            if children is not None:
                fields.extend(self.__extractSubFields(children, currentDepth + 1))
        return fields

    # Static method
    @staticmethod
    @typeCheck(str, AbstractField, int)
    def align(data, field, depth=None):
        """Execute an alignment of specified data with provided field.
        Data must be provided as a list of hexastring.

        :param data: the data to align as a list of hexastring
        :type data: :class:`list`
        :param field : the field to consider when aligning
        :type: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :keyword depth: maximum field depth to consider (similar to layer depth)
        :type depth: :class:`int`.
        :return: the aligned data
        :rtype: :class:`netzob.Common.Utils.MatrixList.MatrixList`
        """

        dAlignment = DataAlignment(data, field, depth)
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
