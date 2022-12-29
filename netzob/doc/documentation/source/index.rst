.. currentmodule:: netzob

====================
Netzob documentation
====================

**Netzob** is an open source tool for reverse engineering,
modelization, traffic generation and fuzzing of communication
protocols. It can be used to infer the message format and the state
machine of a protocol through passive and active processes. The model
can afterward be used to simulate realistic and controllable traffic.

The main features of Netzob are:

**Protocol Modelization**
   Netzob includes a complete model to represent the message format (aka its vocabulary)
   and the state machine of a protocol (aka its grammar).
**Protocol Inference**
   The vocabulary and grammar inference
   methods constitute the core of Netzob. It provides both passive and
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

.. toctree::
   :hidden:
   :maxdepth: 2

   overview/index

Netzob has been initiated by security auditors of AMOSSYS and the
CIDre research team of Supélec to address the reverse engineering of
communication protocols. A detailed overview of the project is
:ref:`available here<overview>`.

Follow us on Twitter: `@Netzob <https://twitter.com/netzob>`_.


Installation of Netzob
======================

.. toctree::
   :maxdepth: 2

   installation/python

..
   installation/debian
   installation/gentoo
   installation/windows

Protocol Modelization with Netzob
=================================

.. toctree::
   :maxdepth: 2

   language_specification/dataspec
   language_specification/statemachinespec
   language_specification/protospec

Protocol Inference with Netzob
==============================

.. toctree::
   :maxdepth: 2

   user_guide/inference/index

Traffic Generation with Netzob
==============================

.. toctree::
   :maxdepth: 2

   language_specification/trafficgeneration
   language_specification/actor

Protocol Fuzzing with Netzob
============================

.. toctree::
   :maxdepth: 2

   language_specification/fuzzing


Import Communication Traces with Netzob
=======================================
.. toctree::
   :maxdepth: 2

   user_guide/import/index


Export Protocol Models with Netzob
==================================
.. toctree::
   :maxdepth: 2

   user_guide/export/index

Tutorials
=========

.. toctree::
   :hidden:
   :maxdepth: 2

   tutorials/discover_features
   tutorials/get_started
   tutorials/modeling_protocol
   tutorials/peach
   tutorials/wireshark


.. :ref:`Get started with Netzob<tutorial_get_started>`
   The goal of this tutorial is to present the usage of each main
   component of Netzob (inference of message format, construction of
   the state machine and generation of traffic) through an undocumented
   protocol.

:ref:`Discover features of Netzob<discover_features>`
   The goal of this tutorial is to present the usage of each main
   component of Netzob (inference of message format, construction of
   the state machine, generation of traffic and fuzzing) through an undocumented
   protocol.

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
