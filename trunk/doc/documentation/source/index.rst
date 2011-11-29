.. currentmodule:: netzob

Welcome to Netzob's documentation!
==================================

**Netzob** simplifies the work for security auditors by providing a complete framework for the reverse engineering of communication protocols. It handles different types of protocols : text protocols (like HTTP and IRC), fixed fields protocols (like IP and TCP) and variable fields protocols (like ASN.1 based formats). Netzob is therefore suitable for reversing network protocols, stuctured files and system and process flows (IPC and communication with drivers). 

Netzob is provided with modules dedicated to capture data in multiple contexts (network, file, process and kernel data acquisition).

The big picture
===============

.. image:: netzob_archi.png
    :alt: Netzob functionalities

Table of contents
-----------------

.. toctree::
   :maxdepth: 2

   introduction/index
   import/index
   modelization/index
   modelization/vocabular
   modelization/grammar
   export/index
   simulation/index
   fuzzing/index
   Annexes/index
   API/index
   

The API section has a complete list of all the classes, methods,
attributes and functions of the :mod:`netzob` module, together with short
examples for many items.

A day Netzob will have a proper and efficient documentation. But this day, PYTHON will also have one ! :)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

