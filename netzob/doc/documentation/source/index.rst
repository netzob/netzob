.. currentmodule:: netzob

====================
Netzob documentation
====================

**Netzob** is an open source tool for reverse engineering, traffic
generation and fuzzing of communication protocols. It can be used to infer
the message format and the state machine of a protocol through passive
and active processes. The model can afterward be used to simulate
realistic and controllable traffic.

The main :ref:`features<overview>` of Netzob are:

**Protocol Vocabulary Modeling and Inference**
  Netzob includes a complete model to represent the message format of
  a protocol (aka its vocabulary). Using specific algorithms, it
  can learn it from provided traces.

**Protocol Grammar Modeling and Inference**
  The state machine of a protocol (aka its grammar) defines the valid
  sequences of exchanged messages. Netzob can learn it
  semi-automatically using specific algorithms.

**Protocol Simulation**
  To support the inferring process, a dynamic analysis is perfomed
  based on simulated actors. These can initiate and take part in a
  complex communication following the infered protocol.


Contact information
===================

:Website: `http://www.netzob.org <http://www.netzob.org>`_
:Email: `contact@netzob.org <contact@netzob.org>`_
:Mailing list: Users, developers and announces lists are available, use the `SYMPA web interface <https://lists.netzob.org/wws>`_ to register.
:IRC: You can hang-out with us on Freenode's IRC channel #netzob @ freenode.org.
:Wiki: Discuss strategy on `Netzob's wiki <https://dev.netzob.org/projects/netzob/wiki>`_
:Twitter: Follow Netzob's official accounts (@Netzob)


Netzob Overview
===============

.. toctree::
   :hidden:
   :maxdepth: 2

   overview/index

Netzob has been initiated by security auditors of AMOSSYS and the
CIDre research team of Supélec to address the reverse engineering of
communication protocols. A detailed overview of the project is
:ref:`available here<overview>`.


Tutorials
=========

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


.. Installation Guides
  ===================

  .. toctree::
     :hidden:
     :maxdepth: 2

     installation/index
     installation/python
     installation/debian
     installation/gentoo
     installation/windows

  * :ref:`Python package installation<installation_python>`
  * :ref:`Debian package installation<installation_debian>`
  * :ref:`Gentoo package installation<installation_gentoo>`
  * :ref:`Windows package installation<installation_windows>`


.. User Guide
   ==========
   
   Read the :ref:`Netzob User Guide<user_guide>`.
   
   .. toctree::
   :maxdepth: 2

      user_guide/import/index
      user_guide/inference/index
      user_guide/simulation/index
      user_guide/export/index


API Documentation
=================

.. toctree::
   :maxdepth: 1

   developer_guide/API/netzob


Developer Guide
===============

See how you can :ref:`contribute to Netzob<contributing>`

Indices and tables
==================

* :ref:`Table of content<main_toc>`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Licences
========

Netzob code in provided under the GPLv3 licence.

The documentation is under the CC-BY-SA licence.
