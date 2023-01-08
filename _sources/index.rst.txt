.. currentmodule:: netzob

====================
Netzob documentation
====================

**Netzob** is an open source tool for reverse engineering,
modelization, traffic generation and fuzzing of communication
protocols.

Netzob is suitable for reversing network protocols, structured files
and system and process flows (IPC and communication with drivers and
devices). Netzob handles different types of protocols: text protocols
(like HTTP and IRC), delimiter-based protocols, fixed fields protocols
(like IP and TCP) and variable-length fields protocols (like TLV-based
protocols).

Netzob can be used to infer the message format and the state machine
of a protocol through passive and active processes. Its objective is
to bring state of art academic researches to the operational field, by
leveraging bio-informatic and grammatical inferring algorithms in a
semi-automatic manner.

Once modeled or inferred, a protocol model can be used in our traffic
generation engine, to allow simulation of realistic and controllable
communication endpoints and flows.

The main features of Netzob are:

**Protocol Modelization**
   Netzob includes a complete model to represent the message format (aka its vocabulary)
   and the state machine of a protocol (aka its grammar).
**Protocol Inference**
   The vocabulary and grammar inference
   component provides both passive and
   active reverse engineering of communication flows through automated
   and manuals mechanisms.
**Traffic Generation**
   Given vocabulary and grammar models previously
   inferred or modelized, Netzob can understand and generate communication traffic
   with remote peers. It can thus act as either a client, a server or
   both.
**Protocol Fuzzing**
   Netzob helps security evaluators by simplifying the creation of
   fuzzers for proprietary or undocumented protocols. Netzob considers the format message and state machine of the
   protocol to generate optimized and specific test cases. Both mutation and generation are available for fuzzing.
**Import Communication Traces**
   Data import is available in two ways: either by
   leveraging the channel-specific captors (currently network and IPC --
   Inter-Process Communication), or by using specific importers (such as
   PCAP files, structured files and OSpy files).
**Export Protocol Models**
   This module permits to export an model of
   a protocol in formats that are understandable by third party software
   or by a human. Current work focuses on export format compatible with
   main traffic dissectors (Wireshark and Scapy) and fuzzers (Peach and
   Sulley).

A :ref:`dedicated tutorial<discover_features>` gives you an overview of the main features in practice.

Netzob has been initiated by security auditors of AMOSSYS and the
CIDre research team of Supélec to address the reverse engineering of
communication protocols.

Follow us on Twitter: `@Netzob <https://twitter.com/netzob>`_.

Example of Ethernet IEEE 802.3 Modelization
===========================================

This quick example illustrates format message modelization, with fixed-size
fields and several relationship fields (CRC32, Size and Padding).

.. code-block:: python

    >>> from netzob.all import *
    >>>
    >>> eth_length = Field(bitarray('0000000000000000'), "eth.length")
    >>> eth_llc = Field(Raw(nbBytes=3), "eth.llc")  # IEEE 802.2 header
    >>> eth_payload = Field(Raw(), name="eth.payload")
    >>> eth_padding = Field(Padding([eth_length,
    ...                              eth_llc,
    ...                              eth_payload],
    ...                             data=Raw(nbBytes=1),
    ...                             modulo=8*60),
    ...                     "eth.padding")
    >>>
    >>> eth_crc_802_3 = Field(bitarray('00000000000000000000000000000000'), "eth.crc")
    >>> eth_crc_802_3.domain = CRC32([eth_length,
    ...                               eth_llc,
    ...                               eth_payload,
    ...                               eth_padding],
    ...                              dataType=Raw(nbBytes=4,
    ...                                           unitSize=UnitSize.SIZE_32))
    >>>
    >>> eth_length.domain = Size([eth_llc, eth_payload],
    ...                          dataType=uint16(), factor=1./8)
    >>>
    >>> symbol = Symbol(name="ethernet_802_3",
    ...                 fields=[eth_length,
    ...                         eth_llc,
    ...                         eth_payload,
    ...                         eth_padding,
    ...                         eth_crc_802_3])
    >>> print(symbol.str_structure())
    ethernet_802_3
    |--  eth.length
         |--   Size(['eth.llc', 'eth.payload']) - Type:Integer(0,65535)
    |--  eth.llc
         |--   Data (Raw(nbBytes=3))
    |--  eth.payload
         |--   Data (Raw(nbBytes=(0,8192)))
    |--  eth.padding
         |--   Padding(['eth.length', 'eth.llc', 'eth.payload']) - Type:Raw(nbBytes=1)
    |--  eth.crc
         |--   Relation(['eth.length', 'eth.llc', 'eth.payload', 'eth.padding']) - Type:Raw(nbBytes=4)


Installation of Netzob
======================

.. toctree::
   :maxdepth: 2
   :caption: Installation

   installation/python

..
   installation/debian
   installation/gentoo
   installation/windows

Protocol Modelization with Netzob
=================================

.. toctree::
   :maxdepth: 2
   :caption: Protocol Modelization

   language_specification/dataspec
   language_specification/statemachinespec
   language_specification/protospec

Protocol Inference with Netzob
==============================

*Note: this section should be completed*

..
   .. toctree::
      :maxdepth: 2

      user_guide/inference/index

Traffic Generation with Netzob
==============================

.. toctree::
   :maxdepth: 2
   :caption: Traffic Generation

   language_specification/trafficgeneration
   language_specification/actor

.. note::

   Several examples of actor usages are provided below:

   * :ref:`Common automaton for a client and a server<ActorExample1>`
   * :ref:`Dedicated automaton for a client and a server<ActorExample2>`
   * :ref:`Modification of the emitted symbol by a client through a callback<ActorExample3>`
   * :ref:`Modification of the emitted symbol by a server through a callback<ActorExample4>`
   * :ref:`Modification of the current transition by a client through a callback<ActorExample5>`
   * :ref:`Modification of the current transition of a server through a callback<ActorExample6>`
   * :ref:`Transition with no input symbol<ActorExample7>`
   * :ref:`How to catch all read symbol timeout<ActorExample8>`
   * :ref:`How to catch all receptions of unexpected symbols<ActorExample9>`
   * :ref:`How to catch all receptions of unknown messages<ActorExample10>`
   * :ref:`Several actors on the same communication channel<ActorExample13>`

Protocol Fuzzing with Netzob
============================

Fuzzing can be applied on format message, state machine or both at the
same time. Fuzzing strategies may leverage either mutation of
generation approaches.

.. toctree::
   :maxdepth: 2
   :caption: Fuzzing

   language_specification/fuzzing
   language_specification/fuzzing_automata

.. note::

   Thanks to the :class:`Actor <netzob.Simulator.Actor.Actor>`
   componant, it is possible to fuzz specific messages at specific
   states in an automaton. This allows to defined fine-tuned fuzzing
   strategies. Several examples of actor usages in a fuzzing context
   are provided below:

   * :ref:`Message format fuzzing from an actor<ActorExample11>`
   * :ref:`Message format fuzzing from an actor, at a specific state<ActorExample12>`

Import Communication Traces with Netzob
=======================================

Netzob supports import of communication traces from the following resources:

* Raw messages
* Raw files
* PCAP files


Export Protocol Models with Netzob
==================================

Netzob supports export of protocols in the following formats:

* XML meta representation
* Scapy Dissector
* :ref:`Wireshark Dissector<tutorial_wireshark>`


..
   Tutorials
   =========

.. :ref:`Get started with Netzob<tutorial_get_started>`
   The goal of this tutorial is to present the usage of each main
   component of Netzob (inference of message format, construction of
   the state machine and generation of traffic) through an undocumented
   protocol.

..
   :ref:`Discover features of Netzob<discover_features>`
      The goal of this tutorial is to present the usage of each main
      component of Netzob (inference of message format, construction of
      the state machine, generation of traffic and fuzzing) through an undocumented
      protocol.

..
   :ref:`Modeling your Protocol with Netzob<tutorial_modeling_protocol>`
      This tutorial details the main features of Netzob's protocol modeling
      aspects. It shows how your protocol fields can be described with Netzob's
      language.     
  
.. :ref:`Auto-generation of Peach pit files/fuzzers<tutorial_peach>`
   This tutorial shows how to take advantage of the Peach exporter
   plugin provided in Netzob to automatically generate Peach pit
   configuration files, thus allowing to do smart fuzzing on
   undocumented protocols.

.. :ref:`Auto-generation of Wireshark dissectors<tutorial_wireshark>`
   This tutorial shows how to leverage Netzob' format message inference
   in order to automatically generate Wireshark dissectors for
   proprietary or undocumented protocols.


Licences
========

Netzob code in provided under the GPLv3 licence.

The documentation is under the CC-BY-SA licence.
