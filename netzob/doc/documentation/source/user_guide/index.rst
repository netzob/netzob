.. currentmodule:: netzob

.. _user_guide:

=================
Netzob User Guide
=================

Netzob is composed of different modules. This user guide will present
you how to use each of these modules.

:ref:`Importing data<import>`
  Data import is available in two ways: either by leveraging the
  channel-specific captors (currently network and IPC -- Inter-Process
  Communication), or by using specific importers (such as PCAP files,
  structured files and OSpy files).

:ref:`Reversing a protocol<inference>`
  The vocabulary and grammar inference methods constitute the core of
  Netzob. It provides both passive and active reverse engineering of
  communication flows through automated and manuals mechanisms.

:ref:`Generating traffic and simulting actors<simulation>`
  Given vocabulary and grammar models previously inferred, Netzob can
  understand and generate communication traffic between multiple
  actors. It can act as either a client, a server or both.

:ref:`Exporting protocol model<export>`
  This module permits to export an inferred model of a protocol in
  formats that are understandable by third party software or by a
  human. Current work focuses on export format compatible with main
  traffic dissectors (Wireshark and Scapy) and fuzzers (Peach and
  Sulley).


**Table of content**

.. toctree::
   :maxdepth: 2

   import/index
   inference/index
   simulation/index
   export/index
