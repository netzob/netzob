===========================================================
Netzob : Protocol Reverse Engineering, Modeling and Fuzzing
===========================================================

.. image:: https://img.shields.io/badge/Python-3-brightgreen.svg
    :target: https://github.com/netzob/netzob
    :alt: Python3

See complete documentation here: https://netzob.github.io/netzob/

About Netzob
============

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

Main features of Netzob
=======================

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

Netzob must be used as a Python 3 library. It can either be imported in your scripts
or in your favorite interactive shell (ipython?).

More Information
================

:Website: https://github.com/netzob/netzob
:Twitter: Follow Netzob's official accounts (@Netzob)

Netzob has been initiated by security auditors of AMOSSYS and the
CIDre research team of CentraleSupélec to address the reverse engineering and
fuzzing of communication protocols.

Documentation
=============

The documentation is available online at: https://netzob.github.io/netzob/

If you want to build the documentation, run the following command::

  $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/

Get Started with Netzob
=======================

Install it
----------

Installing Netzob system dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First thing to do is to check the version of your python3 interpretor.
Netzob requires at least Python 3.8::

  $ python3 --version
  Python 3.8.10

You have to install the following system dependencies::

  $ apt-get install -y python3 python3-dev python3-setuptools virtualenv build-essential libpcap-dev libgraph-easy-perl libffi-dev

Then, create a virtualenv::

  $ mkdir venv
  $ virtualenv venv
  $ source venv/bin/activate

Installing Netzob from PyPI
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can install Netzob from PyPI (recommended choice)::

  (venv) $ pip3 install netzob

Installing Netzob from sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have retrieved Netzob sources, the installation procedure is::

  (venv) $ pip3 install Cython==0.29.32  # Should be manually installed because of setup.py direct dependency
  (venv) $ pip3 install -e .
  
API usage
---------

Once installed, we recommend to use the Netzob API inside scripts, with the following statement to import Netzob::

  from netzob.all import *

Start Netzob CLI
----------------

Netzob also provides its own CLI, in order to play interactively with it::

  (venv) $ netzob

Contributing
============

There are multiple ways to help-us.

Defects and Features  Requests
------------------------------

Help-us by reporting bugs and requesting features using the `Bug Tracker <https://github.com/netzob/netzob/issues>`_.

Join the Development Team
-------------------------

To participate in the development, you need to get the latest version,
modify it and submit your changes.

You're interested in joining, please contact us!

Authors, Contributors and Sponsors
==================================

See the top distribution file ``AUTHORS.txt`` for the detailed and updated list
of authors, contributors and sponsors.

Licenses
========

This software is provided under the GPLv3 License. See the ``COPYING.txt`` file
in the top distribution directory for the full license text.

The documentation is under the CC-BY-SA licence.


Extra
=====

.. figure:: https://raw.githubusercontent.com/netzob/netzob/next/netzob/doc/documentation/source/zoby.png
   :width: 200 px
   :alt: Zoby, the official mascot of Netzob
   :align: center

   Zoby, the official mascot of Netzob.
