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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory


class InvalidDomainException(Exception):
    pass


class Field(AbstractField):
    r"""The Field class is used in the definition of a Symbol structure.

    A Field describes a chunk of a Symbol and is specified by a
    definition domain, representing the set of values the field
    accepts.

    The Field constructor expects some parameters:

    :param domain: The definition domain of the field (i.e. the
                   set of values the field accepts). If not
                   specified, the default definition domain will
                   be Raw(), meaning it accepts any values.
    :param name: The name of the field. If not specified, the
                 default name will be "Field".
    :param layer: A flag indicating if the field is a layer.
    :param isPseudoField: A flag indicating if the field is a
                          pseudo field, meaning it is used
                          internally to help for the computation
                          of the value of another field, but does
                          not directly produce data.
    :type domain: a :class:`list` of :class:`object`
    :type name: :class:`str`
    :type layer: :class:`bool`
    :type isPseudoField: :class:`bool`


    **Fields hierarchy**

    A field can be composed of sub-fields. This is useful for example
    to separate a header, composed of multiple fields, from its
    payload:

    >>> from netzob.all import *
    >>> fh0 = Field()
    >>> fh1 = Field()
    >>> fheader = Field()
    >>> fheader.fields = [fh0, fh1]
    >>> fpayload = Field()
    >>> symbol = Symbol(fields=[fheader, fpayload])
    >>> print(symbol._str_debug())
    Symbol
    |--  Field
    |--  |--  Field
              |--   Data (Raw=None ((0, None)))
    |--  |--  Field
              |--   Data (Raw=None ((0, None)))
    |--  Field
         |--   Data (Raw=None ((0, None)))

    More generally, a field is part of a tree whose root is a symbol
    and whose all other nodes of the tree are fields. Hence, a field
    always has a parent which can be another field or a symbol if it
    is the root.

    **Field definition domain**

    The value that can take a field is defined by its definition
    domain. The definition domain of a field can take multiple forms,
    in order to easily express basic types (such as Integer or ASCII
    strings) or to model complex data structures (such has
    alternatives, repetitions or sequences).

    The following examples present the different forms that are
    authorized by Netzob to express the same field content (i.e. an
    Integer with a constant value of 10):

    >>> f = Field(10)
    >>> f = Field(Integer(10))
    >>> f = Field(Data(Integer(10)))
    >>> f = Field(domain=Data(Integer(10)))

    If these fields are equivalent, this is because the first
    parameter of the Field constructor is *domain=*, thus its name can
    be omitted. Besides, the domain parameter will be parsed by a
    factory, which accepts either the canonical form of a definition
    domain (such as `domain=Data(Integer(10))`) or a shortened form
    (such as `domain=Integer(10)`, or even `domain=10`).

    A domain may be composed of basic types, or complex data
    structures. The following examples show how to express data
    structures composed of 1) an alternative between the integers `10`
    and `20`, 2) a repetition of the string `a`, and 3) an aggregate
    (or concatenation) of the strings `aa` and `bb`:

    >>> f = Field(Alt([10, 20]))
    >>> f = Field(Repeat("a", nbRepeat=(4,8)))
    >>> f = Field(Agg(["aa", "bb"]))

    **Relationships between fields**

    A field can have its value related to the content of another
    field. Such relationships may be specified in Netzob through
    specific domain objects, such as Size or Value classes.

    The following example describes a size relationship with an ASCII
    field:
    
    >>> from netzob.all import *
    >>> f0 = Field(ASCII("test"))
    >>> f1 = Field(Size(f0))
    >>> symbol = Symbol(fields=[f0, f1])
    >>> print(symbol.specialize())
    b'test\x04'

    **Pseudo fields**

    Sometimes, a specific field can be needed to express a complex
    data structure that depends on external data. This is the purpose
    of the `isPseudoField` flag. This flag indicates that the current
    field is only used for the computation of the value of another
    field, but does not produce real content during
    specialization. The following example shows a pseudo field that
    contains an external data, and a real field whose content is the
    size of the external data:

    >>> from netzob.all import *
    >>> f_pseudo = Field(domain="An external data", isPseudoField=True)
    >>> f_real = Field(domain=Size(f_pseudo))
    >>> symbol = Symbol(fields=[f_pseudo, f_real])
    >>> print(symbol.specialize())
    b'\x10'

    A real example of a pseudo field is found in the UDP checksum,
    which relies on a pseudo IP header for its computation.

    **Encoding functions applied on fields**

    Encoding functions represents functions which apply to modify the
    encoding of a data. The following example shows the use of the
    Base64EncodingFunction function to automatically decode base64
    strings in the `f1` field:

    >>> m1 = "hello YWxs"
    >>> m2 = "hello bXkgbG9yZA=="
    >>> m3 = "hello d29ybGQ="
    >>> messages = [RawMessage(m1), RawMessage(m2), RawMessage(m3)]
    >>> f0 = Field(name="f0", domain=ASCII("hello "))
    >>> f1 = Field(name="f1", domain=ASCII(nbChars=(0, 20)))
    >>> s = Symbol(fields=[f0, f1], messages=messages)
    >>> print(s)
    f0       | f1            
    -------- | --------------
    'hello ' | 'YWxs'        
    'hello ' | 'bXkgbG9yZA=='
    'hello ' | 'd29ybGQ='    
    -------- | --------------
    >>> f1.addEncodingFunction(Base64EncodingFunction(encode_data = False))
    >>> print(s)
    f0       | f1       
    -------- | ---------
    'hello ' | 'all'    
    'hello ' | 'my lord'
    'hello ' | 'world'  
    -------- | ---------

    **Fields examples**

    Here are examples of fields:

    * a field containing the integer value 100

      >>> f = Field(100)

    * a field containing a specific binary: '1000' = 8 in decimal

      >>> f = Field(0b1000)

    * a field containing a raw value of 8 bits (1 byte)

      >>> f = Field(Raw(nbBytes=8))

    * a field with a specific raw value

      >>> f = Field(Raw('\x00\x01\x02\x03'))
    
    * a field representing a random IPv4:

      >>> f = Field(IPv4())

    * a field representing a random ASCII of 6 characters length:

      >>> f = Field(ASCII(nbChars=6))

    * a field representing a random ASCII with between 5 and 20 characters:

      >>> payloadField = Field(ASCII(nbChars=(5, 20)))

    * a field whose value is the size of the payloadField:

      >>> f = Field([Size(payloadField)])

    * a field representing an alternative between two differents ASCII strings, either "netzob" or "zoby":

      >>> f = Field(["netzob", "zoby"])

    * a field representing a decimal (10) or an ASCII of 16 chars:

      >>> f = Field([10, ASCII(nbChars=(16))])

    """

    def __init__(self, domain=None, name="Field", isPseudoField=False):
        super(Field, self).__init__(name)
        if domain is None:
            domain = Raw(None)
        self.domain = domain
        self.isPseudoField = isPseudoField

    def specialize(self):
        """Specialize the current field to build a raw data that
        follows the fields definitions attached to current element.

        This method allows to generate some content following the field definition:

        >>> from netzob.all import *
        >>> f = Field("hello")
        >>> print('\\n'.join([str(f.specialize()) for x in range(3)]))
        b'hello'
        b'hello'
        b'hello'

        This method also applies on multiple fields using a Symbol

        >>> fHello = Field("hello ")
        >>> fName = Field("zoby")
        >>> s = Symbol([fHello, fName])
        >>> print('\\n'.join([str(s.specialize()) for x in range(3)]))
        b'hello zoby'
        b'hello zoby'
        b'hello zoby'

        :return: a generated content represented with an hexastring
        :rtype: :class:`str``
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while generating a message
        """
        self._logger.debug("Specializes field {0}".format(self.name))
        if self.__domain is None:
            raise InvalidDomainException("The domain is not defined.")

        from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
        fs = FieldSpecializer(self)
        specializingPaths = fs.specialize()

        if len(specializingPaths) < 1:
            raise Exception("Cannot specialize this field")

        specializingPath = specializingPaths[0]

        self._logger.debug(
            "field specializing done: {0}".format(specializingPath))
        if specializingPath is None:
            raise Exception(
                "The specialization of the field {0} returned no result.".
                format(self.name))

        return TypeConverter.convert(
            specializingPath.getDataAssignedToVariable(self.domain), BitArray,
            Raw)

    @property
    def domain(self):
        """This defines the definition domain of a field.

        This definition domain is made of a list of typed values which can optionally have a static value.
        More information on the available types and their specificities are available on their documentations.

        :type: a :class:`list` of :class:`object <object>` -- By object we refer to a primitive object (:class:`int`, :class:`str`, :class:`hex <hex>`, :class:`binary <binary>`) and netzob types objects inherited from :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        :raises: :class:`InvalidDomainException <netzob.Model.Vocabulary.Field.InvalidDomainException>` if domain invalid.
        """

        return self.__domain

    @domain.setter
    def domain(self, domain):
        normalizedDomain = DomainFactory.normalizeDomain(domain)
        self.__domain = normalizedDomain

    @property
    def messages(self):
        """A list containing all the messages that the parents of this field have.
        In reality, a field doesn't have messages, it just returns the messages of its symbol

        :type: a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        """
        messages = []
        try:
            messages.extend(self.getSymbol().messages)
        except Exception as e:
            self._logger.warning(
                "The field is attached to no symbol and so it has no messages: {0}".
                format(e))

        return messages

    @property
    def isPseudoField(self):
        """Flag describing if current field is a isPseudoField.

        :type: :class:`bool`
        :raises: :class:`TypeError`
        """

        return self.__isPseudoField

    @isPseudoField.setter
    @typeCheck(bool)
    def isPseudoField(self, isPseudoField):
        if isPseudoField is None:
            isPseudoField = False
        self.__isPseudoField = isPseudoField
