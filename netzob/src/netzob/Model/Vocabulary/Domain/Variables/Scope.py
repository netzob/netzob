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
    """This class represents the Assignment Strategy of a variable.

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

    * Scope.CONSTANT
    * Scope.SESSION
    * Scope.MESSAGE (the default strategy for variables)
    * Scope.NONE

    Those strategies are explained below. In addition, some following
    examples are shown in order to understand how the strategies can
    be applied during abstraction and specialization of Field with
    Data variables.

    * **Scope.CONSTANT**: A constant value denotes a static content
      defined once and for all in the protocol. When abstracting, the
      concrete value is compared with the symbolic value, which is a
      constant and succeeds only if it matches. On the other hand, the
      specialization of a constant value does not imply any additional
      operations than just using the value as it is. A typical example of
      a constant value is a magic number in a protocol or a delimiter
      field.


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
      does not correspond to the expected model returns an exception:

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

      The following example shows that the specialization of
      constant data raises an exception when no specific value is
      attached to the definition domain of the variable:

      >>> from netzob.all import *
      >>> f = Field(name='f1')
      >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.CONSTANT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> next(s.specialize(memory=m))
      Traceback (most recent call last):
      ...
      StopIteration


    * **Scope.SESSION**: A persistent value carries a value, such as
      a session identifier, generated and memorized during its first
      specialization and reused as such in the remainder of the
      session. Conversely, the first time a persistent field such as this is
      abstracted, the value of its variable is not defined and the received
      value is saved. Later in the session, if this field is
      abstracted again, the corresponding variable is then defined and
      we compare the received field value against the memorized one.


      The following example shows the **abstraction of a persistent
      data**:

      >>> from netzob.all import *
      >>> f = Field(name='f1')
      >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.SESSION)
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> s.abstract("dylan", memory=m)
      OrderedDict([('f1', b'dylan')])
      >>> s.abstract("dylan", memory=m)
      OrderedDict([('f1', b'dylan')])

      The following example shows that the abstraction of persistent
      data that does not correspond to the expected model returns a
      unknown symbol:

      >>> from netzob.all import *
      >>> f = Field(name='f1')
      >>> f.domain = Data(String(nbChars=(5, 10)), scope=Scope.SESSION)
      >>> s = Symbol(name="S0", fields=[f])
      >>> m = Memory()
      >>> s.abstract("kurt", memory=m)
      Traceback (most recent call last):
      ...
      netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'S0', cannot abstract the data: 'kurt'. Error: 'No parsing path returned while parsing 'b'kurt'''


      The following examples show the **specialization of persistent
      data**:

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
  

    * **Scope.MESSAGE**: The value of an ephemeral variable is
      regenerated each time it is specialized. The generated value is
      memorized, and can then be used afterwards to abstract or
      specialize other fields. During abstraction, the value of this
      field is always learned for the same reason. For example, the
      IRC `nick` command includes such an ephemeral field that denotes
      the new nick name of the user. This nick name can afterwards be
      used in other fields, but whenever a NICK command is emitted, its
      value is regenerated.


      The following example shows the **abstraction of ephemeral
      data**:
  
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


      The following examples show the **specialization of ephemeral
      data**:

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


    * **Scope.NONE**: A volatile variable denotes a value which
      changes whenever it is specialized and is never
      memorized. It can be seen as an optimization of an ephemeral
      variable to reduce memory usage. Thus, the abstraction
      process of such a field only verifies that the received value
      complies with the field definition domain without memorizing
      it. For example, a size field or a CRC field is a volatile
      field.

      The following example shows the **abstraction of volatile
      data**:
  
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


      The following example shows the **specialization of volatile
      data**:

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

    CONSTANT = "Constant Scope"
    SESSION = "Persistent Scope"
    MESSAGE = "Ephemeral Scope"
    NONE = "Volatile Scope"
