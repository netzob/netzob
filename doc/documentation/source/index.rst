.. currentmodule:: src 


Welcome to Netzob's documentation!
==================================

**Netzob** simplifies the work for security auditors by providing a complete framework for the reverse engineering of communication protocols. It handles different types of protocols : text protocols (like HTTP and IRC), fixed fields protocols (like IP and TCP) and variable fields protocols (like ASN.1 based formats). Netzob is therefore suitable for reversing network protocols, stuctured files and system and process flows (IPC and communication with drivers). 

Netzob is provided with modules dedicated to capture data in multiple contexts (network, file, process and kernel data acquisition).


Features
--------
* Handle the following inputs as initial data :

    * Pcap files
    * Network capturing (with Scapy)
    * Structured files with unknown format
    * Intra Processus communication (API calls)
    * Inter Processus Communication (pipes, shared memory and sockets)
    * Kernel Memory (with a dedicacted module) 
	

* Metadata representation of inputs
* Clustering (Regroups equivalent messages using) :
	* an UPGMA Algorithm to regroup similar messages
	* an openMP and MPI implementation 

* Sequencing, Alignment (Identification of fields in messages) :
	* Needleman & Wunsch Implementation 

* Fields dependencies identification
	* length fields and associated payloads
	* encapsulated messages identifications 

* Fields type identification
	* Primary types : binary, ascii, num, base64...
	* Definition domain, unique elements and intervals
	* Data carving (tar gz, png, jpg, ...)
	* Semantic data identification (emails, IP ...) 

* Fuzzing :
	* Live instrumentation through a dedicated proxy
	* Possibilities of variations :

* Data and types :
	* Length
	* Fields dependencies 

* Results exports :
	* XML meta representations of infered protocol,
	* Dedicated New Wireshark Disector 

Documentation
-------------

The manual provides an introduction to the module and details most its capabilities.

The reference section has a complete list of all the classes, methods, attributes and functions of the :mod:`src` module, together with short examples for many items.

Some good starting points in the documentation are

* :ref:`introduction`
* :ref:`inputs`
* :ref:`creation`
* :ref:`reading`
* :ref:`quick_reference`
* :ref:`API`
* :ref:`Annexes`

A day NETZOB will have a proper and efficient documentation. But this day, PYTHON will also have one ! :)

.. toctree::
   :hidden:

   contents

.. toctree::
   :hidden:



	
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

