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


@NetzobLogger
class FieldReseter(object):
    """This class defines the required operation to reset
    the definition of a field. It reinitializes the definition domain
    as a raw field and delete its children.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = ["00ff2f000000",	"000010000000",	"00fe1f000000"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> f1 = Field(Raw(nbBytes=1), name="f1")
    >>> f21 = Field(Raw(nbBytes=1), name="f21")
    >>> f22 = Field(Raw(nbBytes=1), name="f22")
    >>> f2 = Field(name="f2")
    >>> f2.fields = [f21, f22]
    >>> f3 = Field(Raw(), name="f3")
    >>> symbol = Symbol([f1, f2, f3], messages=messages)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(symbol)
    f1   | f21  | f22  | f3      
    ---- | ---- | ---- | --------
    '00' | 'ff' | '2f' | '000000'
    '00' | '00' | '10' | '000000'
    '00' | 'fe' | '1f' | '000000'
    ---- | ---- | ---- | --------
    >>> reseter = FieldReseter()
    >>> reseter.reset(symbol)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print(symbol)
    Field         
    --------------
    '00ff2f000000'
    '000010000000'
    '00fe1f000000'
    --------------
    """

    @typeCheck(AbstractField)
    def reset(self, field):
        """Resets the format (field hierarchy and definition domain) of
        the specified field.


        :param field: the field we want to reset
        :type field: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :raise Exception if something bad happens
        """

        if field is None:
            raise TypeError("The field to reset must be specified and cannot be None")

        self._logger.debug("Reset the definition of field {0} ({1})".format(field.name, field.id))
        field.clearFields()

        if isinstance(field, Symbol):
            field.fields = [Field()]

        if isinstance(field, Field):
            field.domain = Raw(None)
