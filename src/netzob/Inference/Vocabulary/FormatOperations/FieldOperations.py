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
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Types.Raw import Raw
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg


@NetzobLogger
class FieldOperations(object):
    """This class offers various operations to support manual merge and split of fields."""

    @typeCheck(AbstractField, AbstractField)
    def mergeFields(self, field1, field2):
        """Merge specified fields.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000", "000010000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1), name="f1")
        >>> f2 = Field(Raw(nbBytes=2), name="f2")
        >>> f3 = Field(Raw(nbBytes=2), name="f3")
        >>> f4 = Field(Raw(nbBytes=1), name="f4")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))

        >>> print(symbol)
        f1   | f2     | f3     | f4  
        ---- | ------ | ------ | ----
        '00' | 'ff2f' | '0000' | '00'
        '00' | '0010' | '0000' | '00'
        '00' | 'fe1f' | '0000' | '00'
        ---- | ------ | ------ | ----
        
        >>> fo = FieldOperations()
        >>> fo.mergeFields(f2, f3)
        >>> print(symbol)
        f1   | Merge      | f4  
        ---- | ---------- | ----
        '00' | 'ff2f0000' | '00'
        '00' | '00100000' | '00'
        '00' | 'fe1f0000' | '00'
        ---- | ---------- | ----

        >>> fo.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol)
        Merge        | f4  
        ------------ | ----
        '00ff2f0000' | '00'
        '0000100000' | '00'
        '00fe1f0000' | '00'
        ------------ | ----
        
        >>> fo.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol)
        Merge         
        --------------
        '00ff2f000000'
        '000010000000'
        '00fe1f000000'
        --------------
        
        :param field1: the left field to merge
        :type field1: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :param field2: the right field to merge
        :type field2: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`

        :raise Exception if something bad happens
        """

        if field1 is None or field2 is None:
            raise TypeError("Fields cannot be None")

        if field1 == field2:
            raise ValueError("Cannot merge a unique field (field1 == field2)")

        self._logger.debug("Merging field {0} with field {1}".format(field1.name, field2.name))

        if field1.parent is not field2.parent:
            raise ValueError("Specified fields don't have the same parent, only fields with same parents can be merged.")

        # retrieve indexes of specified fields
        iField1 = None
        iField2 = None
        for iField, field in enumerate(field1.parent.fields):
            if field == field1:
                iField1 = iField
            elif field == field2:
                iField2 = iField

        if iField1 is None:
            raise ValueError("Cannot retrieve position of field1 in its parent fields")
        if iField2 is None:
            raise ValueError("Cannot retrieve position of field2 in its parent fields")
        if iField2 != iField1 + 1:
            raise ValueError("Field1 must be directly on the left of field2 (iField1={0}, iField2={1})".format(iField1, iField2))

        # build a new field domain
        newDomain = Agg([field1.domain, field2.domain])
        newField = Field(domain=newDomain, name="Merge")
        newField.encodingFunctions = list(field1.encodingFunctions.values())
        parent = field1.parent
        before = parent.fields[:iField1]
        after = parent.fields[iField2 + 1:]
        parent.fields = before + [newField] + after

