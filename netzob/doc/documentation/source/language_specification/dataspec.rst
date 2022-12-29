
.. _dataspec:

.. _format_message_modeling:

Format Message Modeling
=======================

The Netzob Description Language (ZDL) is the API exposed by the Netzob library
to model data structures employed in communication protocols.
This textual language has been designed in order to be easily understandable
by a human. It enables the user to describe a protocol through dedicated
*\*.zdl* files, which are independent of the API and core of the library.
The ZDL language has been designed with attention to its expressiveness.
In this chapter, firstly, the main concepts of the ZDL language are presented,
then its expressiveness in terms of data types,
constraints and relationships are explained.

Format Message Modeling Concepts
--------------------------------

Definitions: Symbol, Field, Variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the Netzob library, the set of valid messages and their formats are
represented through **symbols**. A symbol represents all the messages
that share a similar objective from a protocol perspective.  For
example, the HTTP_GET symbol would describe any HTTP request with the
GET method being set. A symbol can be specialized into a context-valid
message and a message can be abstracted into a symbol.

A **field** describes a chunk of the symbol and is defined by a
**definition domain**, representing the set of values the field handles.
To support complex domains, a definition domain is represented by a tree where
each vertex is a **Variable**. There are three kinds of variables:

* **Data variables**, which describes data whose value is of a given **type**. Various types are provided with the library, such as String, Integer, Raw and BitArray.
* **Relationship variables**, which make it possible to model a relationship between a variable and a list of variables or fields. Besides, relationships can be done between fields of different symbols, thus making it possible to model both **intra-symbol relationships** and **inter-symbol relationships**.
* **Node variables**, which accept one or more children variables.

Node variables can be used to construct complex definition domains,
such as:

* **Aggregate node variable**, which can be used to model a concatenation of
  variables.
* **Alternate node variable**, which can be used to model an alternative of
  multiple variables.
* **Repeat node variable**, which can be used to model a repetition of a
  variable.
* **Optional node variable**, which can be used to model a variable
  that may or may not be present.

As an illustration of these concepts, the following figure presents the
definition of a Symbol structured with three Fields.
The first field contains an alternative between String Data with a constant
string and Integer Data with a constant value. The second field is String
Data with a variable length string.
The third field depicts an Integer whose value is the size of the second string.

.. figure:: img/netzob_vocabulary_model.*
   :align: center

   Example of Symbol definition and relationships with Field and Variable objects.


Abstraction and Specialization of Symbols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The use of a symbolic model is required to represent the message formats of a protocol in a compact way. However, as the objective of this platform is to analyze the robustness of a target implementation, this implies that the testing tool should be able to exchange messages with this target. We therefore need to abstract received messages into symbols that can be used by the protocol model. Conversely, we also need to specialize symbols produced by the protocol model into valid messages. To achieve this, we use an **abstraction** method (*ABS*) and a **specialization** (*SPE*) method. As illustrated in the following figure, these methods play the role of an interface between the symbolic protocol model and a communication channel on which concrete messages transit.

.. figure:: img/abstractionAndSpecialization.*
   :align: center

   Abstraction (ABS) and Specialization (SPE) methods are interfaces between the protocol symbols and the wire messages.

To compute or verify the constraints and relationships that
participate in the definition of the fields, the library relies on a
:class:`~netzob.Model.Vocabulary.Domain.Variables.Memory.Memory`. This memory stores the value of previously captured or emitted
fields. More precisely, the memory contains all the variables that are
needed according to the field definition during the abstraction and
specialization processes.

.. raw:: latex

   \newpage

Modeling Data Types
-------------------

The library enables the modeling of the following data types:

* **Integer**: The Integer type is a wrapper for the Python integer object with the capability to express more constraints regarding the sign, endianness and unit size.
* **HexaString**: The HexaString type makes it possible to describe a sequence of bytes of arbitrary size, with a hexastring notation (e.g. ``aabbcc``).
* **BLOB / Raw**: The Raw type makes it possible to describe a sequence of bytes of arbitrary size, with a raw notation (e.g. ``\xaa\xbb\xcc``).
* **String**: The String type makes it possible to describe a field that contains sequence of String characters.
* **BitArray**: The BitArray type makes it possible to describe a field that contains a sequence of bits of arbitrary size.
* **IPv4**: The IPv4 type makes it possible to encode a raw Python in an IPv4 representation, and conversely to decode an IPv4 representation into a raw object.
* **Timestamp**: The Timestamp type makes it possible to define dates in a specific format (such as Windows, Unix or MacOS X formats).


Data Types API
^^^^^^^^^^^^^^

Each data type provides the following API:

.. autoclass:: netzob.Model.Vocabulary.Types.AbstractType.AbstractType()

.. automethod:: netzob.Model.Vocabulary.Types.AbstractType.AbstractType.convert(typeClass)

.. automethod:: netzob.Model.Vocabulary.Types.AbstractType.AbstractType.generate


Some data types can have specific attributes regarding their endianness, sign and unit size. Values supported for those attributes are available through Python enumerations:

.. autoclass:: netzob.Model.Vocabulary.Types.AbstractType.Endianness
   :members:
.. autoclass:: netzob.Model.Vocabulary.Types.AbstractType.Sign
   :members:
.. autoclass:: netzob.Model.Vocabulary.Types.AbstractType.UnitSize
   :members:

Data Types
^^^^^^^^^^

Supported data types are described in detail in this chapter.

.. _integer_type:

Integer Type
++++++++++++

In the API, the definition of an integer is done through the Integer class.

.. autoclass:: netzob.Model.Vocabulary.Types.Integer.Integer

BLOB / Raw Type
+++++++++++++++

In the API, the definition of a BLOB type is made through the Raw class.

.. autoclass:: netzob.Model.Vocabulary.Types.Raw.Raw(value=None, nbBytes=None, alphabet=None, default=None)

HexaString Type
+++++++++++++++

In the API, the definition of a hexastring type is made through the HexaString class.

.. autoclass:: netzob.Model.Vocabulary.Types.HexaString.HexaString(value=None, nbBytes=None, default=None)

String Type
+++++++++++

In the API, the definition of an ASCII or Unicode type is made through the String class.

.. autoclass:: netzob.Model.Vocabulary.Types.String.String(value=None, nbChars=None, encoding='utf-8', eos=[], default=None)

BitArray Type
+++++++++++++

In the API, the definition of a bitfield type is made through the BitArray class.

.. autoclass:: netzob.Model.Vocabulary.Types.BitArray.BitArray(value=None, nbBits=None, default=None)

IPv4 Type
+++++++++

In the API, the definition of an IPv4 type is made through the IPv4 class.

.. autoclass:: netzob.Model.Vocabulary.Types.IPv4.IPv4(value=None, network=None, endianness=Endianness.BIG, default=None)

Timestamp Type
++++++++++++++

In the API, the definition of a timestamp type is done through the Timestamp class.

.. autoclass:: netzob.Model.Vocabulary.Types.Timestamp.Timestamp(value=None, epoch=Epoch.UNIX, unity=Unity.SECOND, unitSize=UnitSize.SIZE_32, endianness=Endianness.BIG, sign=Sign.UNSIGNED, default=None)

.. raw:: latex

   \newpage

Modeling Fields
---------------

In the API, field modeling is done through the Field class.

.. autoclass:: netzob.Model.Vocabulary.Field.Field
   :members: specialize, abstract, getField, getSymbol, count

   .. automethod:: netzob.Model.Vocabulary.Field.Field.copy()

   .. automethod:: netzob.Model.Vocabulary.Field.Field.str_structure(preset=None)

.. raw:: latex

   \newpage

Modeling Variables
------------------

The definition domain of a field is represented by a tree of variables, containing leaf and node variables. Each variable follows a common API, which is described in the abstract class AbstractVariable:

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable()
   :members: count, isnode

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable.copy()

.. raw:: latex

   \newpage

Modeling Data Variables
-----------------------

In the API, data variable modeling is made through the class Data.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data.copy()

.. raw:: latex

   \newpage

Modeling Node Variables
-----------------------

Multiple variables can be combined to form a complex and precise
specification of the values that are accepted by a field. Four complex
variable types are provided:

* **Aggregate node variables**, which can be used to model a concatenation of variables.
* **Alternate node variables**, which can be used to model an alternative of multiple variables.
* **Repeat node variables**, which can be used to model a repetition of a variable.
* **Optional node variables**, which can be used to model a variable
  that may or may not be present.

Those node variables are described in detail in this chapter.

Aggregate Domain
^^^^^^^^^^^^^^^^

In the API, the definition of a concatenation of variables is made through the Agg class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg.Agg

      .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg.Agg.copy()

Alternate Domain
^^^^^^^^^^^^^^^^

In the API, the definition of an alternate of variables is made through the Alt class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt.Alt.copy()

Repeat Domain
^^^^^^^^^^^^^

In the API, the definition of a repetition of variables, or sequence, is made through the Repeat class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat.Repeat

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat.Repeat.copy()

Optional Domain
^^^^^^^^^^^^^^^

In the API, the definition of a conditional variable is made through the Opt class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Opt.Opt

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Nodes.Opt.Opt.copy()

.. raw:: latex

   \newpage

Modeling Fields with Relationship Variables
-------------------------------------------

The ZDL language defines constraints on variables, in order to handle relationships. Those constraints are leveraged during abstraction and specialization of messages. The API supports the following relationships.

Value Relationships
^^^^^^^^^^^^^^^^^^^

In the API, the definition of a relationship with the value of another field is made through the Value class. This class enables the computation of the relationship result by a basic copy of the targeted field or by calling a callback function.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Value.Value

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Value.Value.copy()

Size Relationships
^^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Size.Size

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Size.Size.copy()

Padding Relationships
^^^^^^^^^^^^^^^^^^^^^

In the API, it is possible to model a structure with a padding through the Padding class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Padding.Padding

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Padding.Padding.copy()

Checksum Relationships
^^^^^^^^^^^^^^^^^^^^^^

The ZDL language enables the definition of checksum relationships between fields.

**Checksum API**

As an example, the API for the CRC16 checksum is as follows:

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16.CRC16(targets)

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16.CRC16.copy()

**Available checksums**

The following list shows the available checksums. The API for those checksums are similar to the CRC16 API.

* :class:`CRC16(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16.CRC16>`
* :class:`CRC16DNP(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16DNP.CRC16DNP>`
* :class:`CRC16Kermit(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16Kermit.CRC16Kermit>`
* :class:`CRC16SICK(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC16SICK.CRC16SICK>`
* :class:`CRC32(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRC32.CRC32>`
* :class:`CRCCCITT(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.CRCCCITT.CRCCCITT>`
* :class:`InternetChecksum(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Checksums.InternetChecksum.InternetChecksum>` (used in ICMP, UDP, IP, TCP protocols, as specified in :rfc:`1071`).

Hash Relationships
^^^^^^^^^^^^^^^^^^

The ZDL language enables the definition of hash relationships between fields.

**Hash API**

As an example, the API for the MD5 hash is as follows:

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.MD5.MD5(targets)

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.MD5.MD5.copy()

**Available hashes**

The following list shows the available hashes. The API for those hashes are similar to the MD5 API.

* :class:`MD5(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.MD5.MD5>`
* :class:`SHA1(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA1.SHA1>`
* :class:`SHA1_96(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA1_96.SHA1_96>`
* :class:`SHA2_224(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA2_224.SHA2_224>`
* :class:`SHA2_256(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA2_256.SHA2_256>`
* :class:`SHA2_384(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA2_384.SHA2_384>`
* :class:`SHA2_512(targets) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hashes.SHA2_512.SHA2_512>`

HMAC Relationships
^^^^^^^^^^^^^^^^^^

The ZDL language enables the definition of HMAC relationships between fields.

**HMAC API**

As an example, the API for the HMAC_MD5 is as follows:

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_MD5.HMAC_MD5(targets, key)

   .. automethod:: netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_MD5.HMAC_MD5.copy()

**Available HMACs**

The following list shows the available HMACs. The API for those HMACs are similar to the HMAC_MD5 API.

* :class:`HMAC_MD5(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_MD5.HMAC_MD5>`
* :class:`HMAC_SHA1(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA1.HMAC_SHA1>`
* :class:`HMAC_SHA1_96(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA1_96.HMAC_SHA1_96>`
* :class:`HMAC_SHA2_224(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_224.HMAC_SHA2_224>`
* :class:`HMAC_SHA2_256(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_256.HMAC_SHA2_256>`
* :class:`HMAC_SHA2_384(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_384.HMAC_SHA2_384>`
* :class:`HMAC_SHA2_512(targets, key) <netzob.Model.Vocabulary.Domain.Variables.Leafs.Hmacs.HMAC_SHA2_512.HMAC_SHA2_512>`

.. _modeling_symbols:
  
Modeling Symbols
----------------

In the API, symbol modeling is done through the Symbol class.

.. autoclass:: netzob.Model.Vocabulary.Symbol.Symbol
   :members: specialize, abstract, getField, count

   .. automethod:: netzob.Model.Vocabulary.Symbol.Symbol.copy()

   .. automethod:: netzob.Model.Vocabulary.Symbol.Symbol.str_structure(preset=None)

.. raw:: latex

   \newpage

Configuring Symbol Content
--------------------------

Setting Field Values
^^^^^^^^^^^^^^^^^^^^

In the API, it is possible to control values that will be used in
fields during symbol specialization. Such configuration can be done
through the Preset class.

.. autoclass:: netzob.Model.Vocabulary.Preset.Preset
   :members: copy, update, bulk_set, clear

Symbol with no Content
^^^^^^^^^^^^^^^^^^^^^^

A specific symbol may be used in the state machine to represent the
absence of received symbol (EmptySymbol), when listening for incoming
message, or the fact that nothing is going to be sent, when attempting
to send something to the remote peer.

.. autoclass:: netzob.Model.Vocabulary.EmptySymbol.EmptySymbol

Relationships between Symbols and the Environment
-------------------------------------------------

In the API, a memory capability is provided in order to support
relationships between variables, as well as variable persistence
during the specialization and abstraction processes. This capability
is described in the Memory class.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Memory.Memory
   :members: memorize, hasValue, getValue, forget, copy

In the API, the ability to specify relationships between successive
messages or between messages and the environment is provided by the
:class:`~netzob.Model.Vocabulary.Domain.Variables.Memory.Memory` class.


**Relationships between fields of successive messages**

The following example shows how to define a relationship between a
received message and the next message to send. A memory is used to store the value of each variable. During the first call to :meth:`specialize` on the ``s1`` symbol, the value associated to the field ``f3`` is notably stored in memory, so that it can be retrieved when calling :meth:`specialize` on the ``s2`` symbol::

  >>> from netzob.all import *
  >>> f1 = Field(domain=String("hello"), name="F1")
  >>> f2 = Field(domain=String(";"), name="F2")
  >>> f3 = Field(domain=String(nbChars=(5,10)), name="F3")
  >>> s1 = Symbol(fields=[f1, f2, f3], name="S1")
  >>>
  >>> f4 = Field(domain=String("master"), name="F4")
  >>> f5 = Field(domain=String(">"), name="F5")
  >>> f6 = Field(domain=Value(f3), name="F6")
  >>> s2 = Symbol(fields=[f4, f5, f6])
  >>>
  >>> memory = Memory()
  >>> m1 = next(s1.specialize(memory=memory))
  >>> m2 = next(s2.specialize(memory=memory))
  >>>
  >>> m1[len("hello;"):] == m2[len("master>"):]
  True


**Relationships between a message field and the environment**

The following example shows how to define a relationship between a
message to send and an environment variable. The symbol is first
defined, and then an environment variable is created. The first step
consists in overloading the definition domain of the ``f9`` field to
link the environment variable::

  >>> from netzob.all import *
  >>>
  >>> # Symbol definition
  >>> f7 = Field(domain=String("master"), name="F7")
  >>> f8 = Field(domain=String(">"), name="F8")
  >>> f9 = Field(domain=String(), name="F9")
  >>> s3 = Symbol(fields=[f7, f8, f9])
  >>>
  >>> # Environment variables definition
  >>> memory = Memory()
  >>> env1 = Data(String(), name="env1")
  >>> memory.memorize(env1, String("John").value)
  >>>
  >>> # Overloading f9 field definition to link the environment variable
  >>> f9.domain = Value(env1)
  >>>
  >>> # Symbol specialization
  >>> next(s3.specialize(memory=memory))
  b'master>John'


Persistence during Specialization and Abstraction of Symbols
------------------------------------------------------------

The values of variables defined in fields can have different assignment strategies, depending on their persistence and lifecycle.

The Scope class provides a description of those strategies, along with some examples.

.. autoclass:: netzob.Model.Vocabulary.Domain.Variables.Scope.Scope

.. raw:: latex

   \newpage
