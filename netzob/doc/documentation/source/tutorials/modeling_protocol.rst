.. currentmodule:: netzob

.. _tutorial_modeling_protocol:

Modeling your Protocol with Netzob
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial details the main features of Netzob's protocol modeling
aspects. It shows how your protocol fields can be described with Netzob's
language.     

The first thing to know is that a Netzob protocol model is entirely made of python code. Naturally, this code relies on Netzob's classes and methods. Thus, following this tutorial requires an installed version of ``Netzob (>=1.0)`` and your favorite python editor.

Initial Settings
^^^^^^^^^^^^^^^^

First step will be to create a directory that will hold our python source file.
For example, create the temporary ``/tmp/netzob`` directory and initiate the executable python file ``/tmp/netzob/tutorial.py``::
  
  /$ mkdir /tmp/netzob
  /$ cd /tmp/netzob
  /tmp/netzob$ touch tutorial.py
  /tmp/netzob$ chmod +x tutorial.py

Along with the traditional python shebang, imports the netzob library::
    
  #!/usr/bin/env python
  from netzob.all import *

Executing this file should return the following::
    
  /tmp/netzob$ ./tutorial.py 
  Warning: FastBinaryTree not available, using Python version BinaryTree.
  Warning: FastAVLTree not available, using Python version AVLTree.
  Warning: FastRBTree not available, using Python version RBTree.    
  
If an error related to the netzob import is returned, check the installation process you followed to install netzob.

Modeling the Protocol Vocabulary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Netzob, the vocabulary of a protocol consists in a list of symbols.

A symbol represents all the messages that share a similar objectif from a protocol perspective. For example, the HTTP_GET symbol describes any HTTP request with the method GET being set.

A symbol is made of a succession of fields and an optional name::

  >>> s = Symbol(name="MySymbol", fields = [field1, field2])

A symbol can be **specialized** into a context-valid message and a message can be **abstracted** into a symbol. 

A field describes a chunk of the symbol and is defined by a definition domain::

  >>> field1 = Field(name="MyField1", domain=domainOfField1)
  >>> field2 = Field(name="MyField2", domain=domainOfField2)

A definition domain describes the set of values its field accepts. To support complex domains, a definition domain is represented by a tree where each vertices is a variable. Thus it exists two kind of variables, *Leaf variables* that accept no children and *Node variables* that accept one or more children variables.

**Leaf variables** are the simplest variables. It exists four kinds of leaf variables.

A *Data Variables* describes a data which value is of a given type. Various types are provided with Netzob:

* *ASCII* : an ASCII string (see class :class:`ASCII <netzob.Common.Models.Types.ASCII>`)
  
  Example of a field that only accepts the "netzob" ASCII string::

    >>> field = Field(ASCII("netzob"))
    >>> field.specialize()
    "netzob"

  Example of a field that only accepts ASCII strings of five characters::
  
    >>> field = Field(ASCII(nbChars=5))
    >>> field.specialize()
    zorjf

  Exemple of a field that only accepts ASCII strings made of 5 to 10 characters::
  
    >>> field = Field(ASCII(nbChars=(5, 10)))
    >>> field.specialize()
    jfozkp
    >>> field.specialize()
    nckrphjj

  
* *Decimal* : a decimal number (see class :class:`Decimal <netzob.Common.Models.Types.Decimal>`)

  Similarly to the ASCII type, a Decimal data can be constrained by a specific value::

    >>> field = Field(Decimal(20))
    >>> field.specialize()
    '\x14'

  A decimal variable also accepts a range of valid values::

    >>> field = Field(Decimal(interval=(10, 100)))
    >>> field.specialize()
    '\xda\x82'
    >>> field.specialize()
    '\xd6\xca'

* *Raw* : a sequence of bytes (see class :class:`Raw <netzob.Common.Models.Types.Raw>`)

  Example of a field that accepts a specific sequence of bytes::
  
    >>> field = Field(Raw('\x00\x01\x02\x03'))
    >>> repr(field.specialize())
    "'\\x00\\x01\\x02\\x03'"

  Example of a field that accepts any sequence of ten bytes::
    
    >>> field = Field(Raw(nbBytes=10))
    >>> field.specialize()
    't)\x99\x8a\x02>\xd1\x91y\x9b'
    
* *BitArray* : a sequence of bits (see class :class:`BitArray <netzob.Common.Models.Types.BitArray>`)

  Example of a field that accepts 3 to 10 bits::
  
    >>> field = Field(BitArray(nbBits=(3, 10))
    >>> field.specialize()
    '\xbe@'
  
* *IPv4* : an IPv4 raw address (see class :class:`IPv4 <netzob.Common.Models.Types.IPv4>`)

  Example of a field that only accepts an IPv4 address::

    >>> field = Field(IPv4())
    >>> field.specialize()
    '\x86\x89\\\xac'

  Example of a field that only accepts an IPv4 address that belongs to the network 192.168.0.0/24::

    >>> field = Field(IPv4(network='192.168.0.0/24'))
    >>> field.specialize()
    '\xc0\xa8\x00\x0b'
    
Along with Data variables, the definition domain of a field can embed the definition of relationships. Two kinds of relationships are supported in Netzob; intra-symbol relationships and inter-symbol relationships. The former denotes a relationship between the size or the value of a variable, and another field in the same symbol. The latter one denotes a relationship with a field of another symbol. Currently, three kinds of relationships are supported.
  
* A *Size Relationship* that describes a data whose value is the size of another field.

  The size field can be declared before the targeted field in the same symbol::

    >>> payloadField = Field(Raw(nbBytes=(5, 10)))
    >>> sizeField = Field(Size(payloadField))
    >>> s = Symbol([sizeField, payloadField])
    >>> s.specialize()
    '\x08\xac\xa4\xb8\x93\x8d\x83\x95%' # size = 8
    >>> s.specialize()
    '\x05\xff\xef\x93\x07\xd7' # size = 5

  The size field can also be declared after the targeted field in the same symbol::
  
    >>> payloadField = Field(Raw(nbBytes=(5, 10)))
    >>> sizeField = Field(Size(payloadField))
    >>> s = Symbol([payloadField, sizeField])
    >>> s.specialize()
    'n\\\x82\x84`\x00\x13\x9f\x08' # size = 8
    >>> s.specialize()
    '\xe7\xc4\xde\xbd\x18\x05' " size = 5

  An optional "factor" and "offset" can be applied to the value of the computed size::

    >>> payloadField = Field(Raw(nbBytes=(5, 10)))
    >>> sizeField = Field(Size(payloadField, offset=1))
    >>> s = Symbol([sizeField, payloadField])
    >>> s.specialize()
    '\x07\xfb+K\xf4N\x99' # size = 6 + 1 (offset)

  More details and examples of Size relationships can be found in its API doc :class:`Size <netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Size>`.
    
* A *Value Relationship* is very similar to the size relationship except that the relationship applies on the value of the targeted field.

  For example, a symbol can be made of three fields, the former being a random sequence of 5 bytes, the second a simple ASCII delimitor (':') while the latest shares the same value than the first field::

    >>> f1 = Field(Raw(nbBytes=5))
    >>> f2 = Field(ASCII(':'))
    >>> f3 = Field(Value(f1))
    >>> s = Symbol(fields=[f1, f2, f3])
    >>> s.specialize()
    '\x0f\x01ShS:\x0f\x01ShS'
    >>> s.specialize()
    '6H\xf9\x84\xc4:6H\xf9\x84\xc4'

  More details and examples of Value relationships can be found in its API doc :class:`Size <netzob.Common.Models.Vocabulary.Domain.Variables.Leafs.Size>`.
    
* A *Checksum Variable* describes a data whose value is the IP checksum of one or more other fields.

  The following example, illustrates the creation of an ICMP Echo request packet with a valid checksum represented on two bytes computed on-the-fly::
    
    >>> typeField = Field(name="Type", domain=Raw('\\x08'))
    >>> codeField = Field(name="Code", domain=Raw('\\x00'))
    >>> chksumField = Field(name="Checksum")
    >>> identField = Field(name="Identifier", domain=Raw('\\x1d\\x22'))
    >>> seqField = Field(name="Sequence Number", domain=Raw('\\x00\\x07'))
    >>> timeField = Field(name="Timestamp", domain=Raw('\\xa8\\xf3\\xf6\\x53\\x00\\x00\\x00\\x00'))
    >>> headerField = Field(name="header")
    >>> headerField.fields = [typeField, codeField, chksumField, identField, seqField, timeField]
    >>> dataField = Field(name="Payload", domain=Raw(nbBytes=(5, 10)))

    >>> chksumField.domain = Checksum([headerField, dataField], "InternetChecksum", dataType=Raw(nbBytes=2))
    >>> s = Symbol(fields = [headerField, dataField])
    >>> s.specialize()
    '\\x08\\x00\x9d\xda\\x1d\\x22\\x00\\x07\\xa8\\xf3\\xf6\\x53\\x00\\x00\\x00\\x00\xec6\xf4\x98\xee' # checksum = \\xda\\x1d

**Leaf Variables** can be combined into a tree model to produce much more complex definition domains. To achieve this, **Node Variables** can be used to construct complex definition domains made of a succession of variables, an alternative of variables or a repetition of variables.

* The *Aggregation Node Variable* can be used to model a succession of variables.

  For example, a field that accepts an ASCII string of 10 characters followed by 2 bytes (see :class:`Agg <netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Agg>`)::
  
    >>> domainOfField = Agg([ ASCII(nbChars=10), Raw(nbBytes=2) ])
    >>> field = Field(domainOfField)
    >>> repr(field.specialize())
    "'VLAuxPd0A0\\x86M'"

* The *Alternate Node Variable* can be used to model an alternative of multiple variables (OR).

  For example, in the following models a field either accepts the ASCII value "hello" or any ASCII string of 10 to 15 characters (see :class:`Alt <netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Alt>`) ::

    >>> field = Field(Alt([ ASCII("hello"), ASCII(nbChars=(10, 15)) ]))
    >>> repr(field.specialize())
    "'hello'"
    >>> repr(field.specialize())
    "'Zm7D3Ade9K'"

* The *Repeat Node Variable* can be used to model a repetition of a variable.
  
  For example, in the following models a field accepts between 1 and 4 repetitions of the ASCII string "netzob" (see :class:`Repeat <netzob.Common.Models.Vocabulary.Domain.Variables.Nodes.Repeat>`) ::::

    >>> field = Field(Repeat(ASCII("netzob"), nbRepeat=(1, 4)))
    >>> repr(field.specialize())
    "'netzob'"
    >>> repr(field.specialize())
    "'netzobnetzobnetzob'"

Node variables can be combined to produce complex definition domains. For example, the following models a field that either accept an ASCII string that starts by the letter "n" or a random IPv4 address::

  >>> field = Field( Alt([ Agg([ASCII('n'), ASCII()]), Agg([ IPv4() ])]) )
  >>> repr(field.specialize())
  "'nlPj66'"
  >>> repr(field.specialize())
  "'aI\\xe4\\xc5'"


  


  






