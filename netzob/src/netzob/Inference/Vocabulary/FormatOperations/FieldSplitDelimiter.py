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
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Model.Vocabulary.Field import Field
#from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Opt import Opt
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString


@NetzobLogger
class FieldSplitDelimiter(object):

    # Static method
    @staticmethod
    @typeCheck(AbstractField, AbstractType)
    def split(field, delimiter):
        r"""Split a field (or symbol) with a specific delimiter. The
        delimiter can be passed either as a String, a Raw, an
        HexaString, or any objects that inherit from AbstractType.


        >>> from netzob.all import *
        >>> from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        >>> samples = [b"aaaaff000000ff10", b"bbff110010ff00000011", b"ccccccccfffe1f000000ff12"]
        >>> messages = [RawMessage(data=sample) for sample in samples]
        >>> symbol = Symbol(messages=messages[:3])
        >>> Format.splitDelimiter(symbol, String("ff"))
        >>> print(symbol.str_data())
        Field-0    | Field-sep-6666 | Field-2      | Field-sep-6666 | Field-4   
        ---------- | -------------- | ------------ | -------------- | ----------
        'aaaa'     | 'ff'           | '000000'     | 'ff'           | '10'      
        'bb'       | 'ff'           | '110010'     | 'ff'           | '00000011'
        'cccccccc' | 'ff'           | 'fe1f000000' | 'ff'           | '12'      
        ---------- | -------------- | ------------ | -------------- | ----------

        >>> samples = [b"434d446964656e74696679230400000066726564", b"5245536964656e74696679230000000000000000", b"434d44696e666f2300000000", b"524553696e666f230000000004000000696e666f", b"434d4473746174732300000000", b"52455373746174732300000000050000007374617473", b"434d4461757468656e7469667923090000006d7950617373776421", b"52455361757468656e74696679230000000000000000", b"434d44656e6372797074230a00000031323334353674657374", b"524553656e637279707423000000000a00000073707176777436273136", b"434d4464656372797074230a00000073707176777436273136", b"5245536465637279707423000000000a00000031323334353674657374", b"434d446279652300000000", b"524553627965230000000000000000", b"434d446964656e746966792307000000526f626572746f", b"5245536964656e74696679230000000000000000", b"434d44696e666f2300000000", b"524553696e666f230000000004000000696e666f", b"434d4473746174732300000000", b"52455373746174732300000000050000007374617473", b"434d4461757468656e74696679230a000000615374726f6e67507764", b"52455361757468656e74696679230000000000000000", b"434d44656e63727970742306000000616263646566", b"524553656e6372797074230000000006000000232021262724", b"434d44646563727970742306000000232021262724", b"52455364656372797074230000000006000000616263646566", b"434d446279652300000000", b"524553627965230000000000000000"]
        >>> messages = [RawMessage(data=TypeConverter.convert(sample, HexaString, Raw)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> symbol.encodingFunctions.add(TypeEncodingFunction(String))  # Change visualization to hexastring
        >>> Format.splitDelimiter(symbol, String("#"))
        >>> print(symbol.str_data())
        Field-0         | Field-sep-23 | Field-2              | Field-sep-23 | Field-4
        --------------- | ------------ | -------------------- | ------------ | -------
        'CMDidentify'   | '#'          | '....fred'           | ''           | ''     
        'RESidentify'   | '#'          | '........'           | ''           | ''     
        'CMDinfo'       | '#'          | '....'               | ''           | ''     
        'RESinfo'       | '#'          | '........info'       | ''           | ''     
        'CMDstats'      | '#'          | '....'               | ''           | ''     
        'RESstats'      | '#'          | '........stats'      | ''           | ''     
        'CMDauthentify' | '#'          | '....myPasswd!'      | ''           | ''     
        'RESauthentify' | '#'          | '........'           | ''           | ''     
        'CMDencrypt'    | '#'          | '....123456test'     | ''           | ''     
        'RESencrypt'    | '#'          | "........spqvwt6'16" | ''           | ''     
        'CMDdecrypt'    | '#'          | "....spqvwt6'16"     | ''           | ''     
        'RESdecrypt'    | '#'          | '........123456test' | ''           | ''     
        'CMDbye'        | '#'          | '....'               | ''           | ''     
        'RESbye'        | '#'          | '........'           | ''           | ''     
        'CMDidentify'   | '#'          | '....Roberto'        | ''           | ''     
        'RESidentify'   | '#'          | '........'           | ''           | ''     
        'CMDinfo'       | '#'          | '....'               | ''           | ''     
        'RESinfo'       | '#'          | '........info'       | ''           | ''     
        'CMDstats'      | '#'          | '....'               | ''           | ''     
        'RESstats'      | '#'          | '........stats'      | ''           | ''     
        'CMDauthentify' | '#'          | '....aStrongPwd'     | ''           | ''     
        'RESauthentify' | '#'          | '........'           | ''           | ''     
        'CMDencrypt'    | '#'          | '....abcdef'         | ''           | ''     
        'RESencrypt'    | '#'          | '........'           | '#'          | " !&'$"
        'CMDdecrypt'    | '#'          | '....'               | '#'          | " !&'$"
        'RESdecrypt'    | '#'          | '........abcdef'     | ''           | ''     
        'CMDbye'        | '#'          | '....'               | ''           | ''     
        'RESbye'        | '#'          | '........'           | ''           | ''     
        --------------- | ------------ | -------------------- | ------------ | -------
        >>> print(symbol.fields[0].str_structure())
        Field-0
        |--   Alt
              |--   Data (Raw(b'CMDidentify'))
              |--   Data (Raw(b'RESidentify'))
              |--   Data (Raw(b'CMDinfo'))
              |--   Data (Raw(b'RESinfo'))
              |--   Data (Raw(b'CMDstats'))
              |--   Data (Raw(b'RESstats'))
              |--   Data (Raw(b'CMDauthentify'))
              |--   Data (Raw(b'RESauthentify'))
              |--   Data (Raw(b'CMDencrypt'))
              |--   Data (Raw(b'RESencrypt'))
              |--   Data (Raw(b'CMDdecrypt'))
              |--   Data (Raw(b'RESdecrypt'))
              |--   Data (Raw(b'CMDbye'))
              |--   Data (Raw(b'RESbye'))

        Below is another example of the FieldSplitDelimiter usage: it splits fields based on a Raw string.


        >>> from netzob.all import *
        >>> samples = [b"\x01\x02\x03\xff\x04\x05\xff\x06\x07", b"\x01\x02\xff\x03\x04\x05\x06\xff\x07", b"\x01\xff\x02\x03\x04\x05\x06"]
        >>> messages = [RawMessage(data=sample) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> Format.splitDelimiter(symbol, Raw(b"\xff"))
        >>> print(symbol.str_data())
        Field-0        | Field-sep-ff | Field-2                | Field-sep-ff | Field-4   
        -------------- | ------------ | ---------------------- | ------------ | ----------
        '\x01\x02\x03' | b'\xff'      | '\x04\x05'             | b'\xff'      | '\x06\x07'
        '\x01\x02'     | b'\xff'      | '\x03\x04\x05\x06'     | b'\xff'      | '\x07'    
        '\x01'         | b'\xff'      | '\x02\x03\x04\x05\x06' | ''           | ''        
        -------------- | ------------ | ---------------------- | ------------ | ----------


        :param field : the field to consider when spliting
        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :param delimiter : the delimiter used to split messages of the field
        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        if delimiter is None:
            raise TypeError("Delimiter cannot be None.")

        if field is None:
            raise TypeError("Field cannot be None.")

        if len(field.messages) < 1:
            raise ValueError(
                "The associated symbol does not contain any message.")

        # Find message substrings after applying delimiter
        splittedMessages = []

        for cell in field.getValues(encoded=False, styled=False):
            splittedMessage = cell.split(delimiter.value.tobytes())
            splittedMessages.append(splittedMessage)

        import itertools
        # Inverse the array, so that columns contains observed values for each field
        splittedMessages = list(itertools.zip_longest(*splittedMessages))

        # If the delimiter does not create splitted fields
        if len(splittedMessages) <= 1:
            return

        # Else, we add (2*len(splittedMessages)-1) fields
        newFields = []
        iField = -1
        for i in range(len(splittedMessages)):
            iField += 1

            fieldDomain = list()

            # temporary set that hosts all the observed values to prevent useless duplicate ones
            observedValues = set()
            has_inserted_empty_value = False

            isEmptyField = True  # To avoid adding an empty field
            for v in splittedMessages[i]:
                if v != "" and v is not None:
                    isEmptyField = False

                    if v not in observedValues:
                        fieldDomain.append(Raw(v))
                        observedValues.add(v)
                else:
                    has_inserted_empty_value = True

            if not isEmptyField:
                if has_inserted_empty_value:
                    newField = Field(
                        domain=DomainFactory.normalizeDomain(Opt(fieldDomain)),
                        name="Field-" + str(iField))
                else:
                    newField = Field(
                        domain=DomainFactory.normalizeDomain(fieldDomain),
                        name="Field-" + str(iField))
                newField.encodingFunctions = list(
                    field.encodingFunctions.values())
                newFields.append(newField)
                iField += 1

            str_delimiter = TypeConverter.convert(delimiter.value, BitArray,
                                                  HexaString).decode('utf-8')
            fieldName = "Field-sep-{}".format(str_delimiter)

            newFields.append(
                Field(domain=Opt(delimiter), name=fieldName))

        newFields.pop()

        # Reset the field
        from netzob.Inference.Vocabulary.Format import Format
        Format.resetFormat(field)

        # Create a field for each entry
        field.fields = newFields
