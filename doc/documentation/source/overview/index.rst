.. currentmodule:: netzob

.. _overview:


Overview of Netzob
==================

Netzob has been initiated by security auditors of
`AMOSSYS <http://www.amossys.fr>`_ and the `CIDre research team of
Supélec <http://www.rennes.supelec.fr/ren/rd/cidre/>`_ to address the
reverse engineering of communication protocols.

Originaly, the development of Netzob has been initiated to support
security auditors and evaluators in their activities of modeling and
simulating undocumented protocols. The tool has then been extended to
allow smart fuzzing of unknown protocol.

The following picture depicts the main modules of Netzob:

.. figure:: http://www.netzob.org/img/overview_archi.png
   :align: center
   :alt: Architecture of Netzob

   Architecture of Netzob

-  **Import module:** Data import is available in two ways: either by
   leveraging the channel-specific captors (currently network and IPC --
   Inter-Process Communication), or by using specific importers (such as
   PCAP files, structured files and OSpy files).
-  **Protocol inference modules:** The vocabulary and grammar inference
   methods constitute the core of Netzob. It provides both passive and
   active reverse engineering of communication flows through automated
   and manuals mechanisms.
-  **Simulation module:** Given vocabulary and grammar models previously
   inferred, Netzob can understand and generate communication traffic
   between multiple actors. It can act as either a client, a server or
   both.
-  **Export module:** This module permits to export an inferred model of
   a protocol in formats that are understandable by third party software
   or by a human. Current work focuses on export format compatible with
   main traffic dissectors (Wireshark and Scapy) and fuzzers (Peach and
   Sulley).

And here is a screenshot of the main graphical interface:

.. figure:: https://dev.netzob.org/attachments/96/netzob_UI.png
   :align: center
   :alt: 

The following sections will describe in more details the available
mechanisms.


Import and capture data
~~~~~~~~~~~~~~~~~~~~~~~

The first step in the inferring process of a protocol in Netzob is to
capture and to import messages as samples. There are different methods
to retrieve messages depending of the communication channel used (files,
network, IPC, USB, etc.) and the format (PCAP, hex, raw binary flows,
etc.).

The figure below describes the multiple communication channels and
therefore possible sniffing point's Netzob aims at addressing.

.. figure:: http://www.netzob.org/img/overview_multipleFlows.png
   :align: center
   :alt: Multiple communication flows arround an application

   Multiple communication flows arround an application

The current version (version 0.4) of Netzob deals with the following
data sources :

-  **Live network communications**
-  **Captured network communications** (PCAPs)
-  **Inter-Process Communications** (IPCs)
-  **Text and binary files**
-  **API flows** through `oSpy <http://code.google.com/p/ospy/>`_ file
   format support

Otherwise, if you plan to reverse a protocol implemented over an
supported communication channel, Netzob's can manipulates any
communications flow through an XML representation. Therefore, this
situation only requires a specific development to capture the targeted
flow and to save it using a compatible XML.

.. figure:: http://www.netzob.org/img/overview_extraImport.png
   :align: center
   :width: 800 px
   :alt: Importing data from an unknown communication channel using the XML definition

   Importing data from an unknown communication channel using the XML
   definition


Inferring message format and state machine with Netzob
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The vocabulary of a communication protocol defines all the words which
are integrated in it. For example, the vocabulary of a malware's
communication protocol looks like a set of possible commands : {"attack
`www.google.fr <http://www.google.fr>`_", "dnspoison
this.dns.server.com", "execute 'uname -a'", ...}. Another example of a
vocabulary is the set of valids words in the HTTP protocol : { "GET
/images/logo.png HTTP/1.1 ...", "HTTP/1.1 200 OK ...", ...}.

Netzob's vocabulary inferring process has been designed in order to
retrieve the set of all possible words used in a targeted protocol and
to identify their structures. Indeed words are made of different fields
which are defined by their value and types. Hence a word can be
described using the structure of its fields.

We describe the learning process implemented in Netzob to
semi-automatically infer the vocabulary and the grammar of a protocol.
This process, illustrated in the following picture, is performed in
three main steps:

#. **Clustering messages and partitioning these messages in fields.**
#. **Characterizing message fields and abstracting similar messages in
   symbols.**
#. **Inferring the transition graph of the protocol.**

.. figure:: http://www.netzob.org/img/overview_inferenceSteps.png
   :align: center
   :width: 800 px
   :alt: The main functionalities

   The main functionalities


Step 1: clustering Messages and Partitioning in Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To discover the format of a symbol, Netzob supports different
partitioning approaches. In this article we describe the most accurate
one, that leverages sequence alignment processes. This technique permits
to align invariants in a set of messages. The `Needleman-Wunsh
algorithm <http://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm>`_
performs this task optimally. Needleman-Wunsh is particularly effective
on protocols where dynamic fields have variable lengths (as shown on the
following picture).

.. figure:: http://www.netzob.org/img/overview_needleman.png
   :align: center
   :alt: Sequence alignment with Needleman-Wunsh algorithm

   Sequence alignment with Needleman-Wunsh algorithm

When partitioning and clustering processes are done, we obtain a
relevant first approximation of the overall message formats. The next
step consists in determining the characteristics of the fields.

If the size of those fields is fixed, as in TCP and IP headers, it is
preferable to apply a basic partitioning, also provided by Netzob. Such
partitioning works by aligning each message by the left, then
separating successive fixed columns from successive dynamic columns.

To regroup aligned messages by similarity, the Needleman-Wunsh algorithm
is used in conjunction with a clustering algorithm. The applied
algorithm is `UPGMA <http://en.wikipedia.org/wiki/UPGMA>`_.


Step 2 : characterization of Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The field type identification partially derives from the partitioning
inference step. For fields containing only invariants, the type merely
corresponds to the invariant value. For other fields, the type is
automatically materialized, in first approximation, with a regular
expression, as shown on next figure. This form enables easy validation of
the data compliance with a specific type. Moreover, Netzob offers the
possibility to visualize the definition domain of a field. This helps to
manually refine the type associated with a field.

.. figure:: http://www.netzob.org/img/overview_fieldType.png
   :align: center
   :alt: Characterization of field type

   Characterization of field type

Some intra-symbol dependencies are automatically identified. The size
field, present in many protocol formats, is an example of intra-symbol
dependency. A search algorithm has been designed to look for potential
size fields and their associated payloads. By extension, this technique
permits to discover encapsulated protocol payloads.

Environmental dependencies are also identified by looking for specific
values retrieved during message capture. Such specific values consist of
characteristics of the underlying hardware, operating system and network
configuration. During the dependency analysis, these characteristics are
searched in various encoding.


Step 3: inferring the Transition Graph of the Protocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The third step of the learning process discovers and extracts the
transition graph from a targeted protocol (also called the grammar).
More formally, the grammar of a communication protocol defines the set
of valid sentences which can be produced by a communication. A sentence
is a sorted set of words which may be received or emmited by a protocol
handler. An exemple of a simple sentence is :

::

    ["attack www.google.fr", "attack has failed", "attack www.kernel.org", "root access granted."]

which can be described using the following simple automata with S0 the
initial state :

.. figure:: http://www.netzob.org/img/overview_exampleSimpleGrammar.png
   :align: center
   :alt: Schema of a simple grammar

   Schema of a simple grammar

The learning process step is achieved by a set of active experiments
that stimulate a real client or server implementation using successive
sequences of input symbols and analyze its responses.

In Netzob, the automata used to represent or model a communication
protocol is an extended version of a Mealy automata which includes
semi-stochastic transitions, contextualized and parametrized inputs and
outputs. The first academic presention of this model is included in a
dedicated scientific paper provided in the documentation section.

The model is inferred through a dedicated **active** process which
consists in stimulating an implementation and to analyze its responses.
In this process, we use the previously infered vocabulary to discover
and to learn the grammar of the communication protocol. Each stimulation
is computed following an extension of the **Angluin L** algorithm\*.

Protocol simulation
~~~~~~~~~~~~~~~~~~~

One of our main goal is to generate realistic network traffic from
undocummented protocols. Therefore, we have implemented a dedicated
module that, given vocabulary and grammar models previously infered, can
simulate a communication protocol between multiple bots and masters.
Besides their use of the same model, each actors is independent from the
others and is organized around three main stages.

The first stage is a dedicated library that reads and writes from the
network channel. It also parses the flow in messages according to
previous protocols layers. The second stage uses the vocabulary to
abstract received messages into symbols and vice-versa to specialize
emitted symbols into messages. A memory buffer is also available to
manage dependency relations. The last stage implements the grammar model
and computes which symbols must be emitted or received according to the
current state and time.

Smart fuzzing with Netzob
~~~~~~~~~~~~~~~~~~~~~~~~~

A typical example of dynamic vulnerability analysis is the robustness
tests. It can be used to reveal software programming errors which can
leads to software security vulnerabilities. These tests provide an
efficient and almost automated solution to easily identify and study
exposed surfaces of systems. Nevertheless, to be fully efficient, the
fuzzing approaches must cover the complete definition domain and
combination of all the variables which exist in a protocol (IP adresses,
serial numbers, size fields, payloads, message identifer, etc.). But
fuzzing typical communication interface requires too many test cases due
to the complex variation domains introduced by the semantic layer of a
protocol. In addition to this, an efficient fuzzing should also cover
the state machine of a protocol which also brings another huge set of
variations. The necessary time is nearly always too high and therefore
limits the efficiency of this approach.

With all these contraints, achieving robustness tests on a target is
feasible only if the expert has access to a specially designed tool for
the targeted protocol. Hence the emergence of a large number of tools to
verify the behavior of an application on one or more communication
protocols. However in the context of proprietary communications
protocols for which no specifications are published, fuzzers do not
provide optimal results.

Netzob helps the security evaluator by simplifying the creation of a
dedicated fuzzer for a proprietary or undocumented protocol. It provides
to the expert means to execute a semi-automated inferring process to create a
model of the targeted protocol. This model can afterward be refined by
the evaluator. Finally, the created model is included in the fuzzing
module of Netzob which considers the vocabulary and the grammar of the
protocol to generate optimized and specific test cases. Both mutation
and generation are available for fuzzing.

Export protocol model
~~~~~~~~~~~~~~~~~~~~~

The following export formats are currently provided by Netzob:

-  XML format
-  human readable (Wireshark like)
-  Peach fuzzer export: this enables efficiency combination of Peach
   Fuzzer on previously undocumented protocols.

Besides, you can write your own exporter to manipulate the inferred
protocol model in your favorite tool.
