.. currentmodule:: netzob

.. _inference:

Protocol inference
==================

Definition of a communication protocol
--------------------------------------

A communication protocol is as language. A language is defined
through~:

* its vocabulary (the set of valid words or, in our context, the set
  of valid messages) ;
* its grammar (the set of valid sentences which, in our context, can
  be represented as a protocol state machine, like the TCP state
  machine).

A word of the vocabular is called a symbol. A symbol represents an
abstract view of a set of similar messages. Similar messages refer to
messages having the same semantic (for example, a TCP SYN message, a
SMTP HELLO message, an ICMP ECHO REQUEST message, etc.).

A symbol is structured following a format, which specifies a sequence
of fields (like the IP format). A field can be splitted into
sub-fields. For example, a payload is a field of a TCP
message. Therefore, by defining a layer as a kind of payload (which is
a specific field), we can retrieve the so-called Ethernet, IP, TCP and
HTTP layers from a raw packet ; each layer having its own vocabular
and grammar.

Field's size can be fixed or variable.
Field's content can be static of dynamic.
Field's content can be basic (a 32 bits integer) or complex (an array).
A field has four attributes~:

* the type defines its definition domain or set of valid values (16 bits integer, string, etc.) ;
* the data description defines the structuration of the field (ASN.1, TSN.1, EBML, etc.) ;
* the data encoding defines ... (ASCII, little endian, big endian, XML, EBML, DER, XER, PER, etc.) ;
* the semantic defines ... (IP address, port number, URL, email, checksum, etc.).

Field's content can be~:

* static ;
* dependant of another field (or a set of fields) of the same message (intra-message dependency) ;
* dependant of a field (or a set of fields) of a previous message in the grammar (inter-message dependency) ;
* dependant of the environment ;
* dependant of the application behaviour (which could depend on the user behaviour) ;
* random (the initial value of the TCP sequence number for example).

Modelization in Netzob
----------------------

Netzob provides a framework for the semi-automated modelization (inference) of communication protocols, i.e. inferring its vocabular and grammar.

* Vocabular inference
   * Message structure inference (based on sequence alignment)
   * Regoupment of similar message structures
   * Field type inference
   * Field dependencies from the same message and from the environment
   * Field semantic inference
* Grammar inference
   * Identification of the automata of the protocol
   * Fields dependencies with messages of previous states

All the functionalities of the framework are detailled in this chapter.

.. toctree::
   :maxdepth: 2

   vocabular
   grammar
