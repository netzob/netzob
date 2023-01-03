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
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, UnitSize
from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString


@NetzobLogger
class FieldSplitStatic(object):
    """This class updates a field structure following
    the static and dynamic portions of data.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = [b"00ff2f00000010", b"00001000000011", b"00fe1f00000012", b"00002000000013", b"00ff1f00000014", b"00ff1f00000015", b"00ff2f00000016", b"00fe1f00000017"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(symbol.str_data())
    Field           
    ----------------
    '00ff2f00000010'
    '00001000000011'
    '00fe1f00000012'
    '00002000000013'
    '00ff1f00000014'
    '00ff1f00000015'
    '00ff2f00000016'
    '00fe1f00000017'
    ----------------
    
    >>> fs = FieldSplitStatic()
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2  | Field-3
    ------- | ------- | -------- | -------
    '00'    | 'ff2f'  | '000000' | '10'   
    '00'    | '0010'  | '000000' | '11'   
    '00'    | 'fe1f'  | '000000' | '12'   
    '00'    | '0020'  | '000000' | '13'   
    '00'    | 'ff1f'  | '000000' | '14'   
    '00'    | 'ff1f'  | '000000' | '15'   
    '00'    | 'ff2f'  | '000000' | '16'   
    '00'    | 'fe1f'  | '000000' | '17'   
    ------- | ------- | -------- | -------

    >>> fs = FieldSplitStatic(mergeAdjacentStaticFields=False, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2 | Field-3 | Field-4 | Field-5 | Field-6
    ------- | ------- | ------- | ------- | ------- | ------- | -------
    '00'    | 'ff'    | '2f'    | '00'    | '00'    | '00'    | '10'   
    '00'    | '00'    | '10'    | '00'    | '00'    | '00'    | '11'   
    '00'    | 'fe'    | '1f'    | '00'    | '00'    | '00'    | '12'   
    '00'    | '00'    | '20'    | '00'    | '00'    | '00'    | '13'   
    '00'    | 'ff'    | '1f'    | '00'    | '00'    | '00'    | '14'   
    '00'    | 'ff'    | '1f'    | '00'    | '00'    | '00'    | '15'   
    '00'    | 'ff'    | '2f'    | '00'    | '00'    | '00'    | '16'   
    '00'    | 'fe'    | '1f'    | '00'    | '00'    | '00'    | '17'   
    ------- | ------- | ------- | ------- | ------- | ------- | -------

    >>> fs = FieldSplitStatic(mergeAdjacentStaticFields=True, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2 | Field-3  | Field-4
    ------- | ------- | ------- | -------- | -------
    '00'    | 'ff'    | '2f'    | '000000' | '10'   
    '00'    | '00'    | '10'    | '000000' | '11'   
    '00'    | 'fe'    | '1f'    | '000000' | '12'   
    '00'    | '00'    | '20'    | '000000' | '13'   
    '00'    | 'ff'    | '1f'    | '000000' | '14'   
    '00'    | 'ff'    | '1f'    | '000000' | '15'   
    '00'    | 'ff'    | '2f'    | '000000' | '16'   
    '00'    | 'fe'    | '1f'    | '000000' | '17'   
    ------- | ------- | ------- | -------- | -------

    >>> fs = FieldSplitStatic(mergeAdjacentStaticFields=False, mergeAdjacentDynamicFields=True)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2 | Field-3 | Field-4 | Field-5
    ------- | ------- | ------- | ------- | ------- | -------
    '00'    | 'ff2f'  | '00'    | '00'    | '00'    | '10'   
    '00'    | '0010'  | '00'    | '00'    | '00'    | '11'   
    '00'    | 'fe1f'  | '00'    | '00'    | '00'    | '12'   
    '00'    | '0020'  | '00'    | '00'    | '00'    | '13'   
    '00'    | 'ff1f'  | '00'    | '00'    | '00'    | '14'   
    '00'    | 'ff1f'  | '00'    | '00'    | '00'    | '15'   
    '00'    | 'ff2f'  | '00'    | '00'    | '00'    | '16'   
    '00'    | 'fe1f'  | '00'    | '00'    | '00'    | '17'   
    ------- | ------- | ------- | ------- | ------- | -------


    We can also plays with the unitsize:
    >>> fs = FieldSplitStatic(UnitSize.SIZE_8, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2 | Field-3  | Field-4
    ------- | ------- | ------- | -------- | -------
    '00'    | 'ff'    | '2f'    | '000000' | '10'   
    '00'    | '00'    | '10'    | '000000' | '11'   
    '00'    | 'fe'    | '1f'    | '000000' | '12'   
    '00'    | '00'    | '20'    | '000000' | '13'   
    '00'    | 'ff'    | '1f'    | '000000' | '14'   
    '00'    | 'ff'    | '1f'    | '000000' | '15'   
    '00'    | 'ff'    | '2f'    | '000000' | '16'   
    '00'    | 'fe'    | '1f'    | '000000' | '17'   
    ------- | ------- | ------- | -------- | -------

    >>> fs = FieldSplitStatic(UnitSize.SIZE_16, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0 | Field-1 | Field-2 | Field-3
    ------- | ------- | ------- | -------
    '00ff'  | '2f00'  | '0000'  | '10'   
    '0000'  | '1000'  | '0000'  | '11'   
    '00fe'  | '1f00'  | '0000'  | '12'   
    '0000'  | '2000'  | '0000'  | '13'   
    '00ff'  | '1f00'  | '0000'  | '14'   
    '00ff'  | '1f00'  | '0000'  | '15'   
    '00ff'  | '2f00'  | '0000'  | '16'   
    '00fe'  | '1f00'  | '0000'  | '17'   
    ------- | ------- | ------- | -------

    >>> fs = FieldSplitStatic(UnitSize.SIZE_32, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0    | Field-1 
    ---------- | --------
    '00ff2f00' | '000010'
    '00001000' | '000011'
    '00fe1f00' | '000012'
    '00002000' | '000013'
    '00ff1f00' | '000014'
    '00ff1f00' | '000015'
    '00ff2f00' | '000016'
    '00fe1f00' | '000017'
    ---------- | --------

    >>> fs = FieldSplitStatic(UnitSize.SIZE_64, mergeAdjacentDynamicFields=False)
    >>> fs.execute(symbol)
    >>> print(symbol.str_data())
    Field-0         
    ----------------
    '00ff2f00000010'
    '00001000000011'
    '00fe1f00000012'
    '00002000000013'
    '00ff1f00000014'
    '00ff1f00000015'
    '00ff2f00000016'
    '00fe1f00000017'
    ----------------

    """

    SUPPORTED_UNITSIZE = [
        UnitSize.SIZE_8, UnitSize.SIZE_16,
        UnitSize.SIZE_32, UnitSize.SIZE_64
    ]

    def __init__(self,
                 unitSize=UnitSize.SIZE_8,
                 mergeAdjacentStaticFields=True,
                 mergeAdjacentDynamicFields=True):
        """Constructor.


        :keyword unitSize: the unitsize considered to split
        :type unitSize: :class:`int`
        :keyword mergeAdjacentStaticFields: if set to true, adjacent static fields are merged in a single field
        :type mergeAdjacentStaticFields: :class:`bool`
        :keyword mergeAdjacentDynamicFields: if set to true, adjacent dynamic fields are merged in a single field
        :type mergeAdjacentDynamicFields: :class:`bool`
        """
        self.unitSize = unitSize
        self.mergeAdjacentStaticFields = mergeAdjacentStaticFields
        self.mergeAdjacentDynamicFields = mergeAdjacentDynamicFields

    @typeCheck(AbstractField)
    def execute(self, field):
        """Executes the field edition following the specified messages.
        Children of the specified field will be replaced with new fields.

        :param field: the format definition that will be user
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raise Exception: if something bad happens
        """

        if field is None:
            raise TypeError("The field cannot be None")
        fieldValues = [
            TypeConverter.convert(data, Raw, HexaString)
            for data in field.getValues(encoded=False)
        ]

        if len(fieldValues) == 0:
            raise Exception("No value found in the field.")

        # Retrieve longuest field value
        maxLengthFieldValue = len(max(fieldValues, key=len))

        # definies the step following specified unitsize
        stepUnitsize = self.__computeStepForUnitsize()

        # Vertical identification of variation
        indexedValues = []
        for i in range(0, maxLengthFieldValue, stepUnitsize):
            currentIndexValue = []
            for fieldValue in fieldValues:
                if i < len(fieldValue):
                    currentIndexValue.append(
                        fieldValue[i:min(len(fieldValue), i + stepUnitsize)])
                else:
                    currentIndexValue.append(b'')
            indexedValues.append(currentIndexValue)

        # If requested, merges the adjacent static fields
        if self.mergeAdjacentStaticFields:
            result = []
            staticSequences = []
            for values in indexedValues:
                if len(set(values)) == 1:
                    # static
                    staticSequences.append(values[0])
                else:
                    # dynamic
                    if len(staticSequences) > 0:
                        result.append([b''.join(staticSequences)])
                        staticSequences = []
                    result.append(values)
            if len(staticSequences) > 0:
                result.append([b''.join(staticSequences)])
            indexedValues = result

        # If requested, merges the adjacent dynamic fields
        if self.mergeAdjacentDynamicFields:
            result = []
            dynamicSequences = []
            for values in indexedValues:
                if len(set(values)) > 1:
                    # dynamic
                    dynamicSequences.append(values)
                else:
                    # static
                    if len(dynamicSequences) > 0:
                        dynValues = zip(*dynamicSequences)
                        tmp_result = []
                        for d in dynValues:
                            tmp_result.append(b''.join(
                                [x if x is not None else b'' for x in d]))
                        result.append(tmp_result)
                        dynamicSequences = []
                    result.append(values)
            if len(dynamicSequences) > 0:
                dynValues = zip(*dynamicSequences)
                tmp_result = []
                for d in dynValues:
                    tmp_result.append(
                        b''.join([x if x is not None else b'' for x in d]))
                result.append(tmp_result)

            indexedValues = result

        # Create a field for each entry
        newFields = []
        for (i, val) in enumerate(indexedValues):
            fName = "Field-{0}".format(i)
            fDomain = DomainFactory.normalizeDomain([
                Raw(TypeConverter.convert(v, HexaString, BitArray))
                for v in set(val)
            ])
            newFields.append(Field(domain=fDomain, name=fName))

        # attach encoding functions
        for newField in newFields:
            newField.encodingFunctions = list(field.encodingFunctions.values())

        field.fields = newFields

    def __computeStepForUnitsize(self):
        """Computes the step following the specified unitsize.

        :return: the step
        :rtype: :class:`int`
        :raise: Exception if unitsize not supported
        """
        if self.unitSize == UnitSize.SIZE_4:
            return 1
        elif self.unitSize == UnitSize.SIZE_8:
            return 2
        elif self.unitSize == UnitSize.SIZE_16:
            return 4
        elif self.unitSize == UnitSize.SIZE_32:
            return 8
        elif self.unitSize == UnitSize.SIZE_64:
            return 16

        else:
            raise Exception("Unitsize not supported, can't compute the step")

    # Static method
    @staticmethod
    def split(field,
              unitSize=UnitSize.SIZE_8,
              mergeAdjacentStaticFields=True,
              mergeAdjacentDynamicFields=True):
        """Split the portion of message in the current field
        following the value variation every unitSize

        :param field : the field to consider when spliting
        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :keyword mergeAdjacentStaticFields: if set to true, adjacent static fields are merged in a single field
        :type mergeAdjacentStaticFields: :class:`bool`
        :keyword mergeAdjacentDynamicFields: if set to true, adjacent dynamic fields are merged in a single field
        :type mergeAdjacentDynamicFields: :class:`bool`
        :keyword unitSize: the required size of static element to create a static field
        :type unitSize: :class:`int`.
        """

        if field is None:
            raise TypeError("Field cannot be None.")

        if unitSize is None:
            raise TypeError("Unitsize cannot be None.")

        if len(field.messages) < 1:
            raise ValueError(
                "The associated symbol does not contain any message.")

        pSplit = FieldSplitStatic(unitSize, mergeAdjacentStaticFields,
                                  mergeAdjacentDynamicFields)
        pSplit.execute(field)

    # Properties

    @property
    def unitSize(self):
        return self.__unitSize

    @unitSize.setter  # type: ignore
    @typeCheck(UnitSize)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("Unitsize cannot be None")

        if unitSize not in FieldSplitStatic.SUPPORTED_UNITSIZE:
            raise ValueError(
                "The specified unitsize is not supported, only {0} are available".
                format(FieldSplitStatic.SUPPORTED_UNITSIZE))

        self.__unitSize = unitSize

    @property
    def mergeAdjacentStaticFields(self):
        return self.__mergeAdjacentStaticFields

    @mergeAdjacentStaticFields.setter  # type: ignore
    @typeCheck(bool)
    def mergeAdjacentStaticFields(self, mergeAdjacentStaticFields):
        if mergeAdjacentStaticFields is None:
            raise TypeError("mergeAdjacentStaticFields cannot be None")

        self.__mergeAdjacentStaticFields = mergeAdjacentStaticFields

    @property
    def mergeAdjacentDynamicFields(self):
        return self.__mergeAdjacentDynamicFields

    @mergeAdjacentDynamicFields.setter  # type: ignore
    @typeCheck(bool)
    def mergeAdjacentDynamicFields(self, mergeAdjacentDynamicFields):
        if mergeAdjacentDynamicFields is None:
            raise TypeError("mergeAdjacentDynamicFields cannot be None")

        self.__mergeAdjacentDynamicFields = mergeAdjacentDynamicFields
