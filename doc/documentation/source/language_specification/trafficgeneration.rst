.. _trafficgeneration:

Sending and Receiving Messages
==============================

Underlying Concepts
-------------------

In the Netzob library, a **communication channel** is an element allowing a connection to a remote device. Generally, if the device is connected with an Ethernet network, the channel includes a socket object and all the properties used to configure it. The channel also provides the connection status and send/receive APIs.

Some specific channels make it possible to access and manipulate the underlying protocol header. These channels are prefixed with the term ``Custom``. The underlying protocol header takes the form of a :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>` for which we can specify a :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>` configuration.

These elements are described in this chapter.


.. _trafficgeneration_channel_list:

Communication Channel API
-------------------------

Each communication channel provides the following API:

.. autoclass:: netzob.Simulator.AbstractChannel.AbstractChannel()
   :members: open, close, __enter__, __exit__, read, write, write_map, flush, sendReceive, setSendLimit, clearSendLimit, set_rate, unset_rate

.. note::
   There are two ways to open and close a channel.
   **Both methods provide the same behavior**.

   1. either by using the related methods:
      :meth:`~netzob.Simulator.AbstractChannel.AbstractChannel.open` and
      :meth:`~netzob.Simulator.AbstractChannel.AbstractChannel.close`.
      Example:

      .. code-block:: python

         channel.open()
         try:
             channel.write(b'abcd')
         finally:
             channel.close()

   2. or by using Python contexts capability provided by the ``with`` statement
      and following methods:
      :meth:`~netzob.Simulator.AbstractChannel.AbstractChannel.__enter__` and
      :meth:`~netzob.Simulator.AbstractChannel.AbstractChannel.__exit__`.
      Example:

      .. code-block:: python

         with channel:
             channel.write(b'abcd')

Builder classes (see `Build pattern <https://en.wikipedia.org/wiki/Builder_pattern>`_)
are also available for each communication channel. They could be used to create
an instance of the channel class using generic keys.

This API is available through the following class:

.. autoclass:: netzob.Simulator.ChannelBuilder.ChannelBuilder
   :members: set, set_map, build

.. _channels:
                
Available Communication Channels
--------------------------------

The available communication channels are as follows:

* :class:`~netzob.Simulator.Channels.RawEthernetChannel.RawEthernetChannel`: this channel sends/receives Raw Ethernet frames.
* :class:`~netzob.Simulator.Channels.CustomEthernetChannel.CustomEthernetChannel`: this channel sends/receives Ethernet frames (with Ethernet header computed by this channel).
* :class:`~netzob.Simulator.Channels.CustomIPChannel.CustomIPChannel`: this channel sends/receives IP payloads (with IP header computed by this channel). 
* :class:`~netzob.Simulator.Channels.IPChannel.IPChannel`: this channel sends/receives IP payloads (with IP header computed by the OS kernel).
* :class:`~netzob.Simulator.Channels.UDPClient.UDPClient`: this channel provides the connection of a client to a specific IP:Port server over a UDP socket.
* :class:`~netzob.Simulator.Channels.TCPClient.TCPClient`: this channel provides the connection of a client to a specific IP:Port server over a TCP socket.
* :class:`~netzob.Simulator.Channels.UDPServer.UDPServer`: this channel provides a server listening to a specific IP:Port over a UDP socket.
* :class:`~netzob.Simulator.Channels.TCPServer.TCPServer`: this channel provides a server listening to a specific IP:Port over a TCP socket.
* :class:`~netzob.Simulator.Channels.SSLClient.SSLClient`: this channel provides the connection of a client to a specific IP:Port server over a TCP/SSL socket.
* :class:`~netzob.Simulator.Channels.DebugChannel.DebugChannel`: this channel provides a way to log I/Os into a specific stream.

.. _trafficgeneration_channels:
     
Each communication channel, with their associated builder class, is described
in the following sub-chapters.

RawEthernetChannel channel
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.RawEthernetChannel.RawEthernetChannel
.. autoclass:: netzob.Simulator.Channels.RawEthernetChannel.RawEthernetChannelBuilder

CustomEthernetChannel channel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.CustomEthernetChannel.CustomEthernetChannel
   :members: setProtocol
.. autoclass:: netzob.Simulator.Channels.CustomEthernetChannel.CustomEthernetChannelBuilder

CustomIPChannel channel
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.CustomIPChannel.CustomIPChannel
.. autoclass:: netzob.Simulator.Channels.CustomIPChannel.CustomIPChannelBuilder

IPChannel channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.IPChannel.IPChannel
.. autoclass:: netzob.Simulator.Channels.IPChannel.IPChannelBuilder

UDPClient channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.UDPClient.UDPClient
.. autoclass:: netzob.Simulator.Channels.UDPClient.UDPClientBuilder

TCPClient channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.TCPClient.TCPClient
.. autoclass:: netzob.Simulator.Channels.TCPClient.TCPClientBuilder

UDPServer channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.UDPServer.UDPServer
.. autoclass:: netzob.Simulator.Channels.UDPServer.UDPServerBuilder

TCPServer channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.TCPServer.TCPServer
.. autoclass:: netzob.Simulator.Channels.TCPServer.TCPServerBuilder

SSLClient channel
^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.SSLClient.SSLClient
.. autoclass:: netzob.Simulator.Channels.SSLClient.SSLClientBuilder

DebugChannel channel
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: netzob.Simulator.Channels.DebugChannel.DebugChannel
.. autoclass:: netzob.Simulator.Channels.DebugChannel.DebugChannelBuilder


.. raw:: latex

   \newpage
