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
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize


@NetzobLogger
class FieldOperations(object):
    """This class offers various operations to support manual merge and split of fields."""

    @typeCheck(Field, Field)
    def mergeFields(self, field1, field2):
        """Merge specified fields.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000", "000010000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1), name="f1")
        >>> f2 = Field(Raw(nbBytes=2), name="f2")
        >>> f3 = Field(Raw(nbBytes=2), name="f3")
        >>> f4 = Field(Data(Integer(unitSize=UnitSize.SIZE_8)), name="f4")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))

        >>> print(symbol.str_data())
        f1   | f2     | f3     | f4  
        ---- | ------ | ------ | ----
        '00' | 'ff2f' | '0000' | '00'
        '00' | '0010' | '0000' | '00'
        '00' | 'fe1f' | '0000' | '00'
        ---- | ------ | ------ | ----
        
        >>> fo = FieldOperations()
        >>> fo.mergeFields(f2, f3)
        >>> print(symbol.str_data())
        f1   | Merge      | f4  
        ---- | ---------- | ----
        '00' | 'ff2f0000' | '00'
        '00' | '00100000' | '00'
        '00' | 'fe1f0000' | '00'
        ---- | ---------- | ----

        >>> fo.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol.str_data())
        Merge        | f4  
        ------------ | ----
        '00ff2f0000' | '00'
        '0000100000' | '00'
        '00fe1f0000' | '00'
        ------------ | ----
        
        >>> fo.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol.str_data())
        Merge         
        --------------
        '00ff2f000000'
        '000010000000'
        '00fe1f000000'
        --------------
        
        :param field1: the left field to merge
        :type field1: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :param field2: the right field to merge
        :type field2: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`

        :raise Exception if something bad happens
        """

        if field1 is None or field2 is None:
            raise TypeError("Fields cannot be None")

        if field1 == field2:
            raise ValueError("Cannot merge a unique field (field1 == field2)")

        self._logger.debug("Merging field {0} with field {1}".format(
            field1.name, field2.name))

        if field1.parent is not field2.parent:
            raise ValueError(
                "Specified fields don't have the same parent, only fields with same parents can be merged."
            )

        # retrieve indexes of specified fields
        iField1 = None
        iField2 = None
        for iField, field in enumerate(field1.parent.fields):
            if field == field1:
                iField1 = iField
            elif field == field2:
                iField2 = iField

        if iField1 is None:
            raise ValueError(
                "Cannot retrieve position of field1 in its parent fields")
        if iField2 is None:
            raise ValueError(
                "Cannot retrieve position of field2 in its parent fields")
        if iField2 != iField1 + 1:
            raise ValueError(
                "Field1 must be directly on the left of field2 (iField1={0}, iField2={1})".
                format(iField1, iField2))

        try:
            # first try to completely blend the fields if this is supported
            newField = FieldOperations._blendFields(field1, field2)
        except (TypeError, NotImplementedError):
            # build a new field domain
            newDomain = Agg([field1.domain, field2.domain])
            newField = Field(domain=newDomain, name="Merge")
            newField.encodingFunctions = list(field1.encodingFunctions.values())
        parent = field1.parent
        before = parent.fields[:iField1]
        after = parent.fields[iField2 + 1:]
        parent.fields = before + [newField] + after

    @typeCheck(Field, Field)
    @staticmethod
    def _blendFields(field1, field2):
        """
        Completely blend two fields without using Agg.
        This requires that the two fields are of the same domain and its parameters.
        The returned new field still needs to be placed into the symbol.

        >>> from netzob.all import *
        >>> samples = [ b'\\x00\\xff/BPz12', b'\\x00\\x00 CQ~34', b'\\x00\\xff/Gf/56' ]
        >>> messages = [RawMessage(data=sample) for sample in samples]
        >>> f1 = Field(Data(Integer(unitSize=UnitSize.SIZE_8)))
        >>> f2 = Field(Raw(nbBytes=3))
        >>> f3 = Field(Raw(nbBytes=4))
        >>> symbol = Symbol([f1, f2, f3], messages=messages)
        >>> print(f2.domain.dataType.size)
        (24, 24)
        >>> print(f3.domain.dataType.size)
        (32, 32)
        >>> nf = FieldOperations._blendFields(f2,f3)
        >>> print(nf.domain.dataType.value)
        None
        >>> print(nf.domain.dataType.endianness)
        Endianness.BIG
        >>> print(nf.domain.dataType.size)
        (56, 56)
        >>> nf2 = FieldOperations._blendFields(f1,f2)
        Traceback (most recent call last):
        ...
        NotImplementedError: The datatype Integer is not yet supported.

        :param field1: the left field
        :param field2: the right field
        :return: a combination of field1 and field2
        :raises TypeError: if domains are not compatible
        :raises NotImplementedError: for datatypes which still need to be implemented
        """

        for d in [field1.domain, field2.domain]:
            if not isinstance(d.dataType, Raw):
                raise NotImplementedError("The datatype {} is not yet supported.".format(d.dataType.typeName))

        if not field1.domain.scope == field2.domain.scope:
            raise TypeError("The scope-values of both fields to merge are not the same.")
        if not field1.domain.dataType.endianness == field2.domain.dataType.endianness:
            raise TypeError("The endianness of both fields to merge are not the same.")
        if not field1.domain.dataType.sign == field2.domain.dataType.sign:
            raise TypeError("The signedness of both fields to merge are not the same.")
        if not field1.domain.dataType.unitSize == field2.domain.dataType.unitSize:
            raise TypeError("The unitSize of both fields to merge are not the same.")

        # '_ASCII__nbChars': (None, None)

        newDomain = field1.domain.__class__(field1.domain.dataType.__class__())
        newDomain.scope = field1.domain.scope
        newDomain.dataType.endianness = field1.domain.dataType.endianness
        newDomain.dataType.sign = field1.domain.dataType.sign
        newDomain.dataType.unitSize = field1.domain.dataType.unitSize
        newDomain.dataType.size = field1.domain.dataType.size

        minsizes = []
        maxsizes = []
        for f in [field1, field2]:
            if not f.domain.dataType.size is None:
                sizes = []
                for s in f.domain.dataType.size:
                    if s is not None:
                        sizes.append(s)
                minsizes.append(min(sizes))
                maxsizes.append(max(sizes))
        newDomain.dataType.size = (sum(minsizes) , sum(maxsizes))

        newField = Field(domain=newDomain, name="Merge")
        newField.encodingFunctions = list(field1.encodingFunctions.values())

        # Position the new field in correct positions with correct dataType size
        if field1.domain.dataType.value is None or field2.domain.dataType.value is None:
            newField.domain.dataType.value = None
        else:
            newField.domain.dataType.Value = (field1.domain.dataType.value + field2.domain.dataType.value)

        return newField
