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
from enum import Enum

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, public_api


@public_api
@NetzobLogger
class Scope(Enum):
    r"""This class represents the Assignment Strategy of a variable.

    The scope of a variable defines how its value is used while
    abstracting and specializing, and therefore impacts the
    memorization strategy.

    A scope strategy can be attached to a variable and is used both
    when abstracting and specializing. A scope strategy describes the
    set of memory operations that must be performed each time a
    variable is abstracted or specialized. These operations can be
    separated into two groups: those used during the abstraction and
    those used during the specialization.

    The available scope strategies for a variable are:

    * Scope.SESSION
    * Scope.MESSAGE
    * Scope.NONE (the default strategy for variables)

    Those strategies are explained below. In addition, some following
    examples are shown in order to understand how the strategies can
    be applied during abstraction and specialization of Field with
    Data variables.

    * **Scope.SESSION**: This kind of variable carries a value, such as
      a session identifier, generated and memorized during its first
      specialization and reused as such in the remainder of the
      session. Conversely, the first time a Session Scope field is
      abstracted, the value of its variable is not defined and the received
      value is saved. Later in the session, if this field is
      abstracted again, the corresponding variable is then defined and
      we compare the received field value against the memorized one.

      The following example shows the **abstraction and specialization of data with Session Scope**:

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.SESSION), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> next(s.specialize(memory=m))
      b'SZ,1'
      >>> s.abstract(b'SZ,1', memory=m)
      OrderedDict([('f1', b'SZ,1')])
      >>> next(s.specialize(memory=m))
      b'SZ,1'
      >>> s.abstract(b'test', memory=m)
      Traceback (most recent call last):
      ...
      netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'S0', cannot abstract the data: 'b'test''. Error: 'No parsing path returned while parsing 'b'test'''

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.SESSION), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> next(s.specialize(memory=m))
      b'john'
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> s.abstract(b'test', memory=m)
      Traceback (most recent call last):
      ...
      netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'S0', cannot abstract the data: 'b'test''. Error: 'No parsing path returned while parsing 'b'test'''


    * **Scope.MESSAGE**: With this kind of variable, the value is
      generated and then memorized during the first specialization and
      is always memorized during abstraction. For further specialization, the value is taken from memory. However, in contrary to
      the Session Scope, no comparison is made during abstraction with
      the current memorized value (i.e. the received value is always memorized). For example, the IRC `nick` command
      corresponds to a Message Scope, that denotes the new nick name
      of the user. This nick name can afterwards be used in other
      fields, but whenever a NICK command is emitted, its value is
      regenerated.

      The following example shows the **abstraction and specialization of data with Message Scope**:

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.MESSAGE), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> next(s.specialize(memory=m))
      b'X!z@'
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> next(s.specialize(memory=m))
      b'john'
      >>> next(s.specialize(memory=m))
      b'john'

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.MESSAGE), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> next(s.specialize(memory=m))
      b'john'
      >>> s.abstract("kurt", memory=m)
      OrderedDict([('f1', b'kurt')])
      >>> next(s.specialize(memory=m))
      b'kurt'


    * **Scope.NONE**: This kind of variable denotes a value which
      changes whenever it is specialized and is never
      memorized. The abstraction
      process of such a field only verifies that the received value
      complies with the field definition domain without memorizing
      it. For example, a size field or a CRC field should have such a scope.


      The following example shows the **abstraction and specializaion of data without persistence**:

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.NONE), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> next(s.specialize(memory=m))
      b'4%!F'
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> next(s.specialize(memory=m))
      b'v\tK5'

      >>> from netzob.all import *
      >>> f = Field(domain=Data(String(nbChars=4), scope=Scope.NONE), name='f1')
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> s.abstract("john", memory=m)
      OrderedDict([('f1', b'john')])
      >>> next(s.specialize(memory=m))
      b'h:JM'
      >>> s.abstract("kurt", memory=m)
      OrderedDict([('f1', b'kurt')])

    """

    CONSTANT = "Constant Scope"
    SESSION = "Session Scope"
    MESSAGE = "Message Scope"
    NONE = "None Scope"


def _test():
    r"""

    **Scope.CONSTANT**: A constant value denotes a static content
    defined once and for all in the protocol. When abstracting, the
    concrete value is compared with the symbolic value, which is a
    constant and succeeds only if it matches. On the other hand, the
    specialization of a constant value does not imply any additional
    operations than just using the value as it is. A typical example of
    a constant value is a magic number in a protocol or a delimiter
    field.

    .. note::
       When creating a data type with a defined value, a normalization step will automatically set the data Scope to :attr:`Scope.CONSTANT`.

    The following example shows the **abstraction of constant
    data**, through the parsing of a message that corresponds to the
    expected model:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> st = String("john")
    >>> f.domain = Data(st, scope=Scope.CONSTANT)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("john", memory=m)
    OrderedDict([('f1', b'john')])

    The following example shows that the abstraction of a data that
    do not correspond to the expected model returns an exception:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> st = String("john")
    >>> f.domain = Data(st, scope=Scope.CONSTANT)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("kurt", memory=m)
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'S0', cannot abstract the data: 'kurt'. Error: 'No parsing path returned while parsing 'b'kurt'''

    The following example shows the **specialization of constant
    data**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> st = String("john")
    >>> f.domain = Data(st, scope=Scope.CONSTANT)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> next(s.specialize(memory=m))
    b'john'
    >>> next(s.specialize(memory=m))
    b'john'
    >>> len(str(m))
    0

    The following example shows that the specialization of constant
    data raises an exception when no specific value is attached to the
    definition domain of the variable:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.CONSTANT)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> next(s.specialize(memory=m))
    Traceback (most recent call last):
    ...
    StopIteration

    The following example shows the **abstraction of data with Session Scope**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.SESSION)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("dylan", memory=m)
    OrderedDict([('f1', b'dylan')])
    >>> s.abstract("dylan", memory=m)
    OrderedDict([('f1', b'dylan')])

    The following example shows that the abstraction of Session Scope
    data that does not correspond to the expected model triggers an exception:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.SESSION)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("kurt", memory=m)
    Traceback (most recent call last):
    ...
    netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'S0', cannot abstract the data: 'kurt'. Error: 'No parsing path returned while parsing 'b'kurt'''


    The following examples show the **specialization of data with Session Scope**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> st = String("john")
    >>> f.domain = Data(st, scope=Scope.SESSION)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> next(s.specialize(memory=m))
    b'john'
    >>> len(str(m))
    0

    >>> from netzob.all import *
    >>> f = Field()
    >>> f.domain = Data(String(nbChars=5), scope=Scope.SESSION)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> generated1 = next(s.specialize(memory=m))
    >>> len(generated1)
    5
    >>> m.hasValue(f.domain)
    True
    >>> generated2 = next(s.specialize(memory=m))
    >>> len(generated2)
    5
    >>> generated1 == generated2
    True


    The following example shows the **abstraction of data with Message Scope**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(4, 10)), scope=Scope.MESSAGE)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("john", memory=m)
    OrderedDict([('f1', b'john')])
    >>> print(m)
    Data (String(nbChars=(4,10))) from field 'f1': b'john'
    >>> s.abstract("john", memory=m)
    OrderedDict([('f1', b'john')])
    >>> print(m)
    Data (String(nbChars=(4,10))) from field 'f1': b'john'
    >>> s.abstract("kurt", memory=m)
    OrderedDict([('f1', b'kurt')])
    >>> print(m)
    Data (String(nbChars=(4,10))) from field 'f1': b'kurt'


    The following examples show the **specialization of data with Message Scope**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> st = String("john")
    >>> f.domain = Data(st, scope=Scope.MESSAGE)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> m.hasValue(f.domain)
    False
    >>> generated1 = next(s.specialize(memory=m))
    >>> m.hasValue(f.domain)
    True
    >>> generated2 = next(s.specialize(memory=m))
    >>> generated1 == generated2
    True


    The following example shows the **abstraction data without persistence**:
  
    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(4, 10)), scope=Scope.NONE)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> s.abstract("john", memory=m)
    OrderedDict([('f1', b'john')])
    >>> len(m)
    0
    >>> s.abstract("john", memory=m)
    OrderedDict([('f1', b'john')])
    >>> len(m)
    0
    >>> s.abstract("kurt", memory=m)
    OrderedDict([('f1', b'kurt')])
    >>> len(m)
    0


    The following example shows the **specialization data without persistence**:

    >>> from netzob.all import *
    >>> f = Field(name='f1')
    >>> f.domain = Data(String(nbChars=(5,10)), scope=Scope.NONE)
    >>> s = Symbol(name="S0", fields=[f])
    >>> m = Memory()
    >>> m.hasValue(f.domain)
    False
    >>> generated = next(s.specialize(memory=m))
    >>> m.hasValue(f.domain)
    False

    """

def _test_scope_none():
    r"""

    >>> from netzob.all import *

    >>> t = IPv4(value="127.0.0.1", endianness=Endianness.LITTLE)
    >>> f = Field(domain=t, name="field")
    >>> symbol = Symbol(fields=[f])
    >>> data = next(symbol.specialize())
    >>> data
    b'\x7f\x00\x00\x01'
    >>> symbol.abstract(data)
    OrderedDict([('field', b'\x7f\x00\x00\x01')])

    >>> t = IPv4(value="127.0.0.1", endianness=Endianness.LITTLE)
    >>> domain = Data(dataType=t, name="IPv4", scope=Scope.NONE)
    >>> f = Field(domain=domain, name="field")
    >>> symbol = Symbol(fields=[f])
    >>> data = next(symbol.specialize())
    >>> data
    b'\x7f\x00\x00\x01'
    >>> symbol.abstract(data)
    OrderedDict([('field', b'\x7f\x00\x00\x01')])

    """
