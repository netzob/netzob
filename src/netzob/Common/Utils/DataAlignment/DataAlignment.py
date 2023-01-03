# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
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

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.MatrixList import MatrixList
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw


@NetzobLogger
class DataAlignment(object):
    """This class enables data alignment, given a field
    specification. This class inherits from :class:`threading.Thread` which enables
    the processing to be synchronous or asynchronous.

    The constructor expects some parameters:

    :param data: the list of data that will be aligned, data must be encoded in HexaString
    :param field: the format definition that will be user
    :param depth: the limit in depth in the format (use None for not limit)
    :param encoded: indicates if the result should be encoded following field definition
    :param styled: indicated if the result visualization filter should be applied
    :param memory: A memory used to store variable values during
                   specialization and abstraction of sequence of symbols.
    :type data: a :class:`list` of data to align
    :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
    :type depth: :class:`int`
    :type encoded: :class:`bool`
    :type styled: :class:`bool`
    :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory>`

    For instance, below is a very simple example of data alignment executed
    traditionnaly

    >>> from netzob.all import *
    >>> from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
    >>> import random
    >>> import string

    >>> contents = ['hello {0} hello'.format(''.join([random.choice(string.ascii_letters) for y in range(random.randint(5,10))])) for x in range(10)]
    >>> fields = [Field("hello ", name="f0"), Field(String(nbChars=(5,10)), name="f1"), Field(" hello", name="f2")]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(contents, symbol, encoded=True)
    >>> print(len(alignedData))
    10

    >>> # one more fun test case
    >>> data = ['hello tototo, welcome' for  x in range(5)]
    >>> # Now we create a symbol with its field structure to represent this type of message
    >>> fields = [Field(String('hello '), name="f1"), Field(Agg([Alt([String("toto"), String("to")]), Alt([String("to"), String("toto")])]), name="f2"), Field(String(', welcome'), name="f3")]
    >>> symbol = Symbol(fields=fields)
    >>> alignedData = DataAlignment.align(data, symbol)
    >>> print(len(alignedData))
    5
    >>> print(alignedData)
    f1       | f2       | f3         
    -------- | -------- | -----------
    'hello ' | 'tototo' | ', welcome'
    'hello ' | 'tototo' | ', welcome'
    'hello ' | 'tototo' | ', welcome'
    'hello ' | 'tototo' | ', welcome'
    'hello ' | 'tototo' | ', welcome'
    -------- | -------- | -----------

    >>> # Lets try to align a more complex message
    >>> msg1 = "helloPUTtotoPA343"
    >>> msg2 = "helloGETtototoPA"
    >>> msg3 = "helloPUTtotototoPAdqs4qsd33"
    >>> messages = [msg1, msg2, msg3]
    >>> fh1 = Field("hello", name="f1")
    >>> fh2 = Field(String(nbChars=(3)), name="f2")
    >>> fh3 = Field(Agg([Alt(["toto", "to"]), Alt(["to", "toto"])]), name="f3")
    >>> fb1 = Field(String("PA"), name="f4")
    >>> fb2 = Field(Raw(nbBytes=(0,10)), name="f5")
    >>> headerFields = [fh1, fh2, fh3]
    >>> bodyFields = [fb1, fb2]

    >>> symbol = Symbol(fields=headerFields+bodyFields)
    >>> alignedData2 = DataAlignment.align(messages, symbol)
    >>> print(alignedData2)
    f1      | f2    | f3         | f4   | f5         
    ------- | ----- | ---------- | ---- | -----------
    'hello' | 'PUT' | 'toto'     | 'PA' | '343'      
    'hello' | 'GET' | 'tototo'   | 'PA' | ''         
    'hello' | 'PUT' | 'totototo' | 'PA' | 'dqs4qsd33'
    ------- | ----- | ---------- | ---- | -----------

    """

    def __init__(self, data, field, depth=None, encoded=True, styled=False, memory=None, messageParser=None):
        self.data = data
        self.field = field
        self.depth = depth
        self.encoded = encoded
        self.styled = styled
        self.memory = memory
        self.messageParser = messageParser

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
        rootLeafFields = self.__root.getLeafFields(depth=self.depth)

        # if self.__root != self.field:
        #     targetedFieldLeafFields = self.field.getLeafFields(depth=self.depth)
        # else:
        targetedFieldLeafFields = rootLeafFields

        result.headers = [str(field.name) for field in targetedFieldLeafFields]

        for d in self.data:
            alignedMsg = next(self.messageParser.parseRaw(d, targetedFieldLeafFields))

            alignedEncodedMsg = []
            for ifield, currentField in enumerate(targetedFieldLeafFields):

                # now we apply encoding and mathematic functions
                fieldValue = alignedMsg[ifield]

                if self.encoded and len(
                        list(currentField.encodingFunctions.values())) > 0:
                    for encodingFunction in list(
                            currentField.encodingFunctions.values()):
                        fieldValue = encodingFunction.encode(fieldValue)
                else:
                    fieldValue = fieldValue.tobytes()

                if currentField in self.field.getLeafFields(depth=self.depth):
                    alignedEncodedMsg.append(fieldValue)

            result.append(alignedEncodedMsg)

        return result

    # Static method
    @staticmethod
    @typeCheck(str, AbstractField, int)
    def align(data, field, depth=None, encoded=True, memory=None, messageParser=None):
        """Execute an alignment of specified data with provided field.
        Data must be provided as a list of hexastring.

        :param data: the data to align as a list of hexastring
        :param field : the field to consider when aligning
        :param depth: maximum field depth to consider (similar to layer depth)
        :param encoded: set to True if you want the returned result to follow the encoding functions
        :param memory: A memory used to store variable values during
                       specialization and abstraction of sequence of symbols.
        :param messageParser: The underlying message parser class instance to use.
        :type data: :class:`list`
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :type depth: :class:`int`.
        :type encoded: :class:`boolean`
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory>`
        :type messageParser: :class:`MessageParser <netzob.Model.Vocabulary.Domain.Parser.MessageParser.MessageParser>`
        :return: the aligned data
        :rtype: :class:`MatrixList <netzob.Common.Utils.MatrixList.MatrixList>`
        """

        dAlignment = DataAlignment(data, field, depth, encoded=encoded, memory=memory, messageParser=messageParser)
        return dAlignment.execute()

    # Properties
    @property
    def data(self):
        """The list of data to align.
        """
        return self.__data

    @data.setter  # type: ignore
    def data(self, data):
        if data is None:
            raise Exception("Data cannot be None")
        val = []
        for d in data:
            if isinstance(d, str):
                val.append(bytes(d, "utf-8"))
            elif isinstance(d, bytes):
                val.append(d)
            else:
                raise Exception(
                    "Invalid type, data can only be a str or a bytes not {}: {}".
                    format(type(data), d))
        self.__data = val

    @property
    def field(self):
        """The field that contains the definition domain used
        to align data

        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        """
        return self.__field

    @field.setter  # type: ignore
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
        """The depth represents the maximum deepness in the field definition
        that will be considered when aligning messages.

        If set to None, its no limit.

        :type: :class:`int`
        """
        return self.__depth

    @depth.setter  # type: ignore
    @typeCheck(int)
    def depth(self, depth):
        if depth is not None and depth < 0:
            raise ValueError(
                "Depth cannot be <0, use None to specify unlimited depth")

        self.__depth = depth

    @property
    def encoded(self):
        """The encoded defines if it applies the encoding filters on aligned data

        :type: :class:`bool`
        """
        return self.__encoded

    @encoded.setter  # type: ignore
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

    @styled.setter  # type: ignore
    @typeCheck(bool)
    def styled(self, styled):
        if styled is None:
            raise ValueError("Styled cannot be None")

        self.__styled = styled

    @property
    def memory(self):
        """The memory used for data persistence.

        :type: :class:`netzob.Model.Vocabulary.Domain.Variables.Memory`
        """
        return self.__memory

    @memory.setter  # type: ignore
    def memory(self, memory):
        self.__memory = memory

    @property
    def messageParser(self):
        """The messageParser used to parse the data.

        :type: :class:`netzob.Model.Vocabulary.Domain.Parser.MessageParser.MessageParser`
        """
        return self.__messageParser

    @messageParser.setter  # type: ignore
    def messageParser(self, messageParser):
        if messageParser is not None:
            self.__messageParser = messageParser
        else:
            from netzob.Model.Vocabulary.Domain.Parser.MessageParser import MessageParser
            self.__messageParser = MessageParser(memory=self.memory)
