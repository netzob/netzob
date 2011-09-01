.. currentmodule:: src

.. _inputs:

Inputs
======

Netzob can handle multiple kinds of input data. Hence, you can analyze network traffic, IPC communications, files structures, etc.
An analysis manipulates messages. 
It's possible to integrates multiple types of messages in the same analysis. Therefore, Netzob accepts the presence of network and files
messages in the same analysis if you want to.

AbstractMessage
---------------
All the messages inherits from this definition and therefore has the following parameters :

* a unique ID
* a data field represented with an array of hex

NetworkMessage
--------------
A network message is defined with the following parameters :

* a timestamp
* the ip source
* the ip target
* the protocol (TCP/UDP/ICMP...)
* the layer 4 source port
* the layer 4 target port


Definition of a NetworkMessage :

.. automodule:: src.netzob.Common.Models.NetworkMessage

    .. autoclass:: NetworkMessage
    	:members

Definition of the factory for XML processing of a NetworkMessage :

.. automodule:: src.netzob.Common.Models.Factories.NetworkMessageFactory

    .. autoclass:: NetworkMessageFactory   
  
FileMessage
--------------
A file message is defined with the following parameters :

* a filename
* the line number in the file
* the creation date of the file
* the last modification date of the file
* the owner of the file
* the size of the file


Definition of a NetworkMessage :

.. automodule:: src.netzob.Common.Models.FileMessage

    .. autoclass:: FileMessage
    	:members

Definition of the factory for XML processing of a FileMessage :

.. automodule:: src.netzob.Common.Models.Factories.FileMessageFactory

    .. autoclass:: FileMessageFactory   
  