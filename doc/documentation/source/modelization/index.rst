.. currentmodule:: src

.. _modelization:

Modelization
============

Netzob provides a framework for the modelization of communication protocols. This framework includes the following function :



Options during alignment process
--------------------------------
aaa


Analyses after alignment process
--------------------------------
aaa


Visualization options
---------------------
aaa

Message contextual menu
-----------------------
aaa

Group contextual menu
---------------------
aaa

Type structure contextual menu
------------------------------
aaa







Payload extraction
------------------

The function "Find Size Fields", as its name suggests, is dedicated to find fields that contain any length value as well as the associated payload. It does this on each group. Netzob supports different encoding of the size field : big and little endian binary values are supported through size of 1, 2 and 4 bytes. The algorithm used to find the size fields and their associated payloads is desribed in the table XXX.

[INCLUDE ALGORITHM]

The following picture represents the application of the function on a trace example, and the associated effect when selecting a field/payload entry.

[INCLUDE FIGURE]

Messages distribution
---------------------

This function shows a graphical representation of the distribution of bytes per offset for each message of the current group. This function helps to identify entropy variation of each fields. Entropy variation combined with byte distribution help the user to infer the field type.

[INCLUDE GRAPH]

Data typing
-----------



Data carving
------------

Data carving is the process of extracting semantic information from fields or messages. Netzob allows the extraction of the following semantic information :

* URL
* email
* IP address

[INCLUDE FIGURE]

Refine regexes
--------------
aaa

Search
------
aaa

Slick regexes
-------------
aaa

Domain of definition
--------------------
aaa

Change type representation
--------------------------
aaa

Concatenate
-----------
aaa

Split column
------------
aaa

Merge columns
-------------
aaa

Properties
----------
aaa

Delete message
--------------
aaa

