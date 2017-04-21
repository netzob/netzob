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
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Common.Utils.Decorators import typeCheck


@NetzobLogger
class SVAS(object):
    """This class represents the Assignment Strategy of a variable.

    The State Variable Assignment Strategy (SVAS) of a variable
    defines how its value is used while abstracting and specializing,
    and therefore impacts the memorization strategy.

    A`SVAS` strategy can be attached to a variable and is used both
    when abstracting and specializing. A SVAS strategy describes the
    set of memory operations that must be performed each time a
    variable is abstracted or specialized. These operations can be
    separated into two groups, those used during the abstraction and
    those used during the specialization.

    The available SVAS strategies for a variable are:

    * SVAS.CONSTANT
    * SVAS.EPHEMERAL (the default strategy for variables)
    * SVAS.VOLATILE
    * SVAS.PERSISTENT

    Those strategies are explained below. Besides some following
    examples are shown in order to understand how the strategies can
    be applied during abstraction and specialization of Field with
    Data variables.

    * **SVAS.CONSTANT**: A constant value denotes a static content
      defined once and for all in the protocol. When abstracting, the
      concrete value is compared against the symbolic value which is a
      constant and succeeds only if it matches. On the other hand, the
      specialization of a constant value does not imply any additional
      operations than just using the value as is. A typical example of
      a constant value is a magic number in a protocol or a delimiter
      field.


      The following example shows the **abstraction of a constant
      data**, through the parsing of a message that corresponds to the
      expected model:

      >>> from netzob.all import *
      >>> f = Field()
      >>> value = TypeConverter.convert("netzob", ASCII, BitArray)
      >>> f.domain = Data(dataType=ASCII(), originalValue=value, svas=SVAS.CONSTANT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> msg1 = RawMessage("netzob")
      >>> mp = MessageParser()
      >>> print(mp.parseMessage(msg1, s))
      [bitarray('011011100110010101110100011110100110111101100010')]

      The following example shows that the abstraction of a constant
      data raises an exception when Netzob tries to parse a message
      that does not correspond to the expected model:

      >>> msg2 = RawMessage("netzab")
      >>> mp = MessageParser()
      >>> print(mp.parseMessage(msg2, s))
      Traceback (most recent call last):
        ...
      netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzab''


      The following example shows the **specialization of a constant
      data**:
  
      >>> from netzob.all import *
      >>> f = Field()
      >>> value = TypeConverter.convert("netzob", ASCII, BitArray)
      >>> f.domain = Data(dataType=ASCII(), originalValue=value, svas=SVAS.CONSTANT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.specializeSymbol(s).generatedContent)
      bitarray('011011100110010101110100011110100110111101100010')
      >>> print(ms.specializeSymbol(s).generatedContent)
      bitarray('011011100110010101110100011110100110111101100010')
      >>> print(len(str(ms.memory)))
      0

      The following example shows that the specialization of a
      constant data raises an exception when no value is attached to
      the definition domain of the variable:
      
      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5, 10)), svas=SVAS.CONSTANT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.specializeSymbol(s).generatedContent)
      Traceback (most recent call last):
        ...
      Exception: Cannot specialize this symbol.


    * **SVAS.PERSISTENT**: A persistent value carries a value, such as
      a session identifier, generated and memorized during its first
      specialization and reused as such in the remainder of the
      session. Conversely, the first time such persistent field is
      abstracted, its variable's value is not defined and the received
      value is saved. Later in the session, if this field is
      abstracted again, the corresponding variable is then defined and
      we compare the received field value against the memorized one.


      The following example shows the **abstraction of a persitent
      data**:

      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5, 10)), svas=SVAS.PERSISTENT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> msg1 = RawMessage("netzob")
      >>> msg2 = RawMessage("netzob")
      >>> mp = MessageParser()
      >>> print(mp.parseMessage(msg1, s))
      [bitarray('011011100110010101110100011110100110111101100010')]
      >>> print(mp.parseMessage(msg2, s))
      [bitarray('011011100110010101110100011110100110111101100010')]

      The following example shows that the abstraction of a persistent
      data raises an exception when Netzob tries to parse a message
      that does not correspond to the expected model:

      >>> msg3 = RawMessage("netzab")
      >>> print(mp.parseMessage(msg3, s))
      Traceback (most recent call last):
        ...
      netzob.Model.Vocabulary.Domain.Parser.MessageParser.InvalidParsingPathException: No parsing path returned while parsing 'b'netzab''


      The following examples show the **specialization of a persistent
      data**:

      >>> from netzob.all import *
      >>> f = Field()
      >>> value = TypeConverter.convert("netzob", ASCII, BitArray)
      >>> f.domain = Data(dataType=ASCII(), originalValue=value, svas=SVAS.PERSISTENT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.specializeSymbol(s).generatedContent)
      bitarray('011011100110010101110100011110100110111101100010')
      >>> print(len(str(ms.memory)))
      0

      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=5), svas=SVAS.PERSISTENT)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> generated1 = ms.specializeSymbol(s).generatedContent
      >>> print(len(generated1))
      40
      >>> print(ms.memory.hasValue(f.domain))
      True
      >>> generated2 = ms.specializeSymbol(s).generatedContent
      >>> print(len(generated2))
      40
      >>> generated1 == generated2
      True
  

    * **SVAS.EPHEMERAL**: The value of an ephemeral variable is
      regenerated each time it is specialized. The generated value is
      memorized, and can then be used afterwards to abstract or
      specialize other fields. During abstraction, the value of this
      field is always learned for the same reason. For example, the
      IRC `nick` command includes such an ephemeral field that denotes
      the new nick name of the user. This nick name can afterward be
      used in other fields but whenever a NICK command is emitted, its
      value is regenerated.


      The following example shows the **abstraction of an ephemeral
      data**:
  
      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5, 10)), svas=SVAS.EPHEMERAL)
      >>> s = Symbol(name="S0", fields=[f])
      >>> msg1 = RawMessage("netzob")
      >>> msg2 = RawMessage("netzob")
      >>> msg3 = RawMessage("netzab")
      >>> mp = MessageParser()
      >>> print(mp.parseMessage(msg1, s))
      [bitarray('011011100110010101110100011110100110111101100010')]
      >>> print(mp.memory)
      Data (ASCII=None ((40, 80))): b'netzob'
      >>> print(mp.parseMessage(msg2, s))
      [bitarray('011011100110010101110100011110100110111101100010')]
      >>> print(mp.memory)
      Data (ASCII=None ((40, 80))): b'netzob'
      >>> print(mp.parseMessage(msg3, s))
      [bitarray('011011100110010101110100011110100110000101100010')]
      >>> print(mp.memory)
      Data (ASCII=None ((40, 80))): b'netzab'


      The following examples show the **specialization of an ephemeral
      data**:

      >>> from netzob.all import *
      >>> f = Field()
      >>> value = TypeConverter.convert("netzob", ASCII, BitArray)
      >>> f.domain = Data(dataType=ASCII(), originalValue=value, svas=SVAS.EPHEMERAL)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.memory.hasValue(f.domain))
      False
      >>> generated1 = ms.specializeSymbol(s).generatedContent
      >>> print(ms.memory.hasValue(f.domain))
      True
      >>> generated2 = ms.specializeSymbol(s).generatedContent
      >>> generated2 == ms.memory.getValue(f.domain)
      True
      >>> generated1 == generated2
      False
  
      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5, 10)), svas=SVAS.EPHEMERAL)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.memory.hasValue(f.domain))
      False
      >>> generated1 = ms.specializeSymbol(s).generatedContent
      >>> print(ms.memory.hasValue(f.domain))
      True
      >>> generated2 = ms.specializeSymbol(s).generatedContent
      >>> generated2 == ms.memory.getValue(f.domain)
      True
      >>> generated1 == generated2
      False


    * **SVAS.VOLATILE**: A volatile variable denotes a value which
      changes whenever it is specialized and that is never
      memorized. It can be seen as an optimization of an ephemeral
      variable to reduce the memory usages. Thus, the abstraction
      process of such field only verifies that the received value
      complies with the field definition domain without memorizing
      it. For example, a size field or a CRC field is a volatile
      field.

      The following example shows the **abstraction of a volatile
      data**:
  
      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5, 10)), svas=SVAS.VOLATILE)
      >>> s = Symbol(name="S0", fields=[f])
      >>> msg1 = RawMessage("netzob")
      >>> msg2 = RawMessage("netzob")
      >>> msg3 = RawMessage("netzab")
      >>> mp = MessageParser()
      >>> print(mp.parseMessage(msg1, s))
      [bitarray('011011100110010101110100011110100110111101100010')]
      >>> print(len(str(mp.memory)))
      0
      >>> print(mp.parseMessage(msg2, s))
      [bitarray('011011100110010101110100011110100110111101100010')]
      >>> print(len(str(mp.memory)))
      0
      >>> print(mp.parseMessage(msg3, s))
      [bitarray('011011100110010101110100011110100110000101100010')]
      >>> print(len(str(mp.memory)))
      0


      The following example shows the **specialization of a volatile
      data**:

      >>> from netzob.all import *
      >>> f = Field()
      >>> f.domain = Data(dataType=ASCII(nbChars=(5,10)), svas=SVAS.VOLATILE)
      >>> s = Symbol(name="S0", fields=[f])
      >>> ms = MessageSpecializer()
      >>> print(ms.memory.hasValue(f.domain))
      False
      >>> generated1 = ms.specializeSymbol(s).generatedContent
      >>> print(ms.memory.hasValue(f.domain))
      False
      >>> generated2 = ms.specializeSymbol(s).generatedContent
      >>> generated2 == ms.memory.hasValue(f.domain)
      False
      >>> generated1 == generated2
      False

    """

    CONSTANT = "Constant SVAS"
    EPHEMERAL = "Ephemeral SVAS"
    VOLATILE = "Volatile SVAS"
    PERSISTENT = "Persistent SVAS"

    def __init__(self):
        pass
