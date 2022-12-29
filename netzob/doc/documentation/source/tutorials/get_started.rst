.. currentmodule:: netzob

.. _tutorial_get_started:

Getting started with Netzob
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The goal of this tutorial is to present the usage of each main component
of Netzob (inference of message format, construction of the state
machine and generation of traffic) through an undocumented protocol.

You can download the protocol material here :

-  `Protocol
   PCAP <https://dev.netzob.org/attachments/132/target_protocol.pcap>`_
   : contains messages of the targeted protocol ;
-  `Protocol
   implementation <https://dev.netzob.org/attachments/127/target_protocol.tar.gz>`_
   : provide the server and client implementation of the protocol.

You can follow the tutorial with only the PCAP file. But, you will need
the implementation if you want to generate traffic and allow Netzob to
discuss with a real implementation.


Setting the Workspace
^^^^^^^^^^^^^^^^^^^^^

Just after installing Netzob, when you start it, you have to set the
workspace directory (as in Eclipe).

.. figure:: https://dev.netzob.org/attachments/119/tuto_workspace.png
   :align: center
   :alt:
    **Side note:** in Netzob, a workspace can be defined as a collection
    of projects and of configuration properties. The directory which
    host the workspace contains directories and files which includes
    configuration files (workspace.xml), the set of projects (directory
    projects) and other configuration resources (logging, traces, ...).
    When creating a new workspace, Netzob will generate the necessary
    workspace files based on templates. The directory "projects"
    includes a directory for each created project. You can specify the
    workspace on the command line (using the option "-w <path to the
    workspace>" when executing Netzob. Otherwise, it will read the user
    file located at "~/.netzob" to find out which workspace was lastly
    used. If none, Netzob will ask you at startup where the workspace
    is.


Your first project
^^^^^^^^^^^^^^^^^^

To create a project, navigate to the menu ``File`` > ``New project``.
Here, you can choose a project name which should be unique in the
workspace.

    **Side note:** by default, Netzob chooses a location inside a
    dedicated directory located in the "projects" directory of your
    current workspace. The newly created project is automatically
    selected which allow you to start working on it.

You can switch to another project at anytime through the use of the menu
``File`` > ``Open project from workspace``. Do not forget to save your
project before!

Capture traces
^^^^^^^^^^^^^^

The first step in the inferring process of a protocol in Netzob is to
capture and to import messages as samples. There are different methods
to retrieve messages depending of the communication channel used (files,
network, IPC, USB, etc.) and the format (PCAP, hex, raw binary flows,
etc.).

For this tutorial, you can import network messages with the provided
PCAP file. But we recommand to use the provided implementation to
generate samples of traffic and capture them with Netzob. You can do
this with the Netwok Capturer plugin, which is accessible in the menu
``File`` > ``Capture messages`` > ``Capture network traffic``.

.. figure:: https://dev.netzob.org/attachments/113/tuto_capture-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/106/tuto_capture.png
   :alt: 


As shown in the picture, you have to launch the capture at the Layer 4
on the localhost ``lo`` interface. As the targeted protocol works over
UDP, you'll be able to capture only the UDP payloads. Then launch the
server of the targeted protocol and then the client. This one will send
different commands to the server and wait for the response.

Once you have captured one session, you have to select the messages you
want to import (you should import everything) and click the Import
messages button. A popup will ask you if you want to allow duplicate
messages. It's better to not do so, to avoid unnecessary messages. We
recommend to repeat this import process 4 times, in order to have enough
variation between messages.


Infer vocabulary
^^^^^^^^^^^^^^^^

Let's now start the inference of the message format (vocabulary).

The next picture shows the whole vocabulary inference interface and the
intended meaning of each component.

.. figure:: https://dev.netzob.org/attachments/120/tuto_voca_ui_small.png
   :align: center
   :target: https://dev.netzob.org/attachments/123/tuto_voca_ui.png 
   :alt: 

The main window shows each message in raw hexadecimal format. You can
play with visualization attributes : right click on the symbol, then
select Visualization and the attribute you want to change (hex, decimal
or even string format, the unit size and potentially the sign and
endianness).

The following picture shows the rendering of the messages in hex format
(on the left) and string format (on the right). You can then see that
messages contain some interesting strings (``api_identify``,
``api_encrypt``, ``api_decrypt``, etc.).

.. figure:: https://dev.netzob.org/attachments/128/tuto_messages-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/129/tuto_messages.png
   :alt: 

You can use the filter functionality to display messages that contain a
specific pattern. Here, we filter with the ``api_identify`` pattern.

.. figure:: https://dev.netzob.org/attachments/107/tuto_messages3-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/101/tuto_messages3.png 
   :alt: 

This filter permits to easily retrieve the messages associated with a
potential identification command.

You can see that a '``#``\ ' character is present in each messages. You
can try to split the messages by forcing their partitioning with a
specific delimiter. To do so, use the Force partitioning functionality
available in the symbol list (either with a right click on a symbol, or
by selecting a symbol with its checkbox and then clicking on the Force
partitioning button right above).

.. figure:: https://dev.netzob.org/attachments/117/tuto_force_partitioning.png
   :align: center
   :alt: 

Using the '``#``\ ' string delimiter, you'll have the following result:

.. figure:: https://dev.netzob.org/attachments/130/tuto_force_part_result_small.png
   :align: center
   :target: https://dev.netzob.org/attachments/131/tuto_force_part_result.png 
   :alt: 

You may also want to play with Sequence alignment. This partitioning
enables message alignment according to their common patterns.

After playing with the different partitioning available, you are able
to retrieve the different commands associated with the targeted
protocol, as shown on the following picture.

.. figure:: https://dev.netzob.org/attachments/109/tuto_symboles-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/104/tuto_symboles.png 
   :alt: 

According to the name of the commands, you can see that a
``api_encrypt`` command is available. Let's have a look at its message
format, which looks like:

::

    [command]#[dataToEncrypt][padding]

Netzob enables you to indicate that a specific field has a mutable
content, which means its data is not fixed (such as the '#' delimiter)
nor part of a set of fixed elements (such as the command string).To
specify the structure of a field and its attributes, right click on a
field and select Edit Variable. A popup dialog displays a rooted tree
that corresponds to the inferred structure of the field. For example,
you should have all the observed values of the field (materialized
through DataVariable leafs) under an AlternateVariable node variable.

Regarding the targeted protocol, as we want to allow any data for the
current field, we first have to delete the ``AlternateVariableNode`` and
modify the root node to a ``DataVariable`` that has a mutable behavior,
as shown on the following picture.

.. figure:: https://dev.netzob.org/attachments/115/tuto_variable-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/105/tuto_variable.png 
   :alt: 

You can visualize the associated message format on bottom-left corner.
Its should display something like this:

.. figure:: https://dev.netzob.org/attachments/110/tuto_variable2-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/97/tuto_variable2.png
   :alt: 

Now that we have refined the ``api_encrypt`` command message, we have to
do the same for other commands that also take as parameter a user data:
``api_identify``, ``api_authentify`` and ``api_decrypt``, but also for
some response messages such as ``resp_decrypt`` and ``resp_encrypt``.

At this time, you have a satisfactory approximation the vocabulary. You
can now start to construct the state machine of the protocol.


Infer Grammar
^^^^^^^^^^^^^

In this tutorial, we won't explain the automatic inference (learning) of
the state machine. As the targeted protocol has a basic state machine,
we will simply show how to model it in Netzob.

A basic state machine contains states and transitions. In Netzob, we use
a complex structure to model the grammar of a protocol. This model
enables information's specification such as the response time between an input
symbol and an output symbol, or even the probability of the different
output messages given an uniq input message. This model is called an
SMMDT (Stochastic Mealy Machine with Deterministic Transitions).

The grammar perspective interface of Netzob enables the creation of:

-  states (initial or not);
-  semi-stochastic transitions (i.e. "normal" transitions);
-  open channel transitions;
-  close channel transitions.

.. figure:: https://dev.netzob.org/attachments/118/tuto_grammar_buttons.png
   :align: center
   :alt: 

Regarding our targeted protocol, we construct the associated model with
the following information:

-  1 open channel transition and an initial state;
-  1 close channel transition and a final state;
-  4 main states: init, identified, authenticated, closed;
-  depending on the current state, we are able or not to launch certain
   commands;
-  some commands will trigger transitions (``api_identify``,
   ``api_authentify`` and ``api_bye``).

Once modeled, this looks like:

.. figure:: https://dev.netzob.org/attachments/114/tuto_grammar-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/116/tuto_grammar.png
   :alt: 

Now that Netzob knows both the vocabulary and the grammar of the
targeted protocol, we are able to generate traffic that respect the
protocol model.


Generate traffic
^^^^^^^^^^^^^^^^

Let's go to the Simulator perspective of Netzob.

The simulator provides either client creation, server or both.
You can tell Netzob to talk with a real client or server implementation,
or you can just launch a client and a server inside Netzob and let them
talk together.

.. figure:: https://dev.netzob.org/attachments/121/tuto_simu_ui_small.png
   :align: center
   :target: https://dev.netzob.org/attachments/122/tuto_simu_ui.png
   :alt: 

Let's now create a client. We have to specify the following information:

-  **client name**;
-  **initiator** or not (i.e. who opens the communication channel ?): it
   will usally be yes for a client;
-  **client or server side**: client;
-  **protocol**: UDP for te targeted protocol;
-  **bind IP**: nothing here, as the client finds its own interface;
-  **bind port**: nothing here, as the client finds its own port;
-  **target IP**: 127.0.0.1;
-  **target port**: 4242.

Now start the real server implementation, select the client in Netzob
and click the Start button on the top-right corner. This will generate
and send commands to the real server, and you'll be able to see the
exchanged messages in the interface, as shown on the following picture.

.. figure:: https://dev.netzob.org/attachments/108/tuto_simu-small.png
   :align: center
   :target: https://dev.netzob.org/attachments/99/tuto_simu.png
   :alt: 

After this introductive tutorial, we'll be glade to have feedbacks and
to `help you <http://www.netzob.org/community>`_ (see our mailing list
`user@lists.netzob.org <mailto:user@lists.netzob.org>`_ or ou IRC
channel #netzob on Freenode).

If you want to go further and `start
contributing <http://www.netzob.org/development>`_ to Netzob, that is
perfect. There are many simple or complex tasks everyone can do:
translation, documentation, bug fix, feature proposal or implementation.
