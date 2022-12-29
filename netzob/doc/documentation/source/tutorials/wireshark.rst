.. currentmodule:: netzob

.. _tutorial_wireshark:

Export Wireshark dissectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Principle
^^^^^^^^^

`Wireshark <http://www.wireshark.org>`_ is an open-source packet
analyzer able to identify protocols and to highlight fields from the
data stream. Its main drawback is that it is only usefull on
documented/standard protocols. Within Netzob, which achieves
semi-automatic reverse engineering of protocols, we have developed an
exporter plugin that provides automatic generation of Wireshark dissectors
from proprietary or undocumented protocols. Dissectors are built in
`LUA <http://wiki.wireshark.org/Lua>`_ programming language.

Netzob provides a powerful datamodel in which fields are described with
the following information:

-  Regular expression (fixed or dynamic size)
-  Name (textual representation)
-  Format
-  Size
-  Endianness
-  Signing

All this information is gathered to generate a script including a
dissector used by Wireshark.

Language
^^^^^^^^

Wireshark can be statically extended with C modules similar to core
dissectors. Optionally, Wireshark can be configured to embed a LUA
interpretor. For modularity purposes, the Lua engine has been chosen
to extend Wireshark with Netzob generated dissectors.

Prerequisite
^^^^^^^^^^^^

You need Netzob in version 0.4.1 or above. The wireshark exporter
functionality is provided as a netzob core plugin (which is included in
the 0.4.1 version).

This tutorial assumes that the user have previously inferred the
specification of the targeted protocol. An example of protocol inference
is avaibale in the `Getting started with
Netzob <http://www.netzob.org/resources/tutorial_get_started>`_
tutorial.

Usage
^^^^^

#. Check that Wireshark supports Lua

   .. figure:: http://wiki.wireshark.org/Lua?action=AttachFile&do=get&target=lua-about.png
      :align: center
      :alt: 

#. Select a project

   Given a partitioned symbol in a project you can generate a wireshark
   dissector using the Export project menu item, then by selecting
   Wireshark.

   .. figure:: https://dev.netzob.org/attachments/158/2012-10-25-173314_1595x647_scrot_small.png
      :align: center
      :target: https://dev.netzob.org/attachments/82/2012-10-25-173314_1595x647_scrot.png
      :alt: 

   .. figure:: https://dev.netzob.org/attachments/159/2012-10-25-180841_1552x731_scrot_small.png
      :align: center
      :target: https://dev.netzob.org/attachments/83/2012-10-25-180841_1552x731_scrot.png
      :alt: 

   You should get a popup with the LUA script automatically generated:

   .. figure:: https://dev.netzob.org/attachments/161/2012-10-30-180554_987x807_scrot_small.png
      :align: center
      :target: https://dev.netzob.org/attachments/94/2012-10-30-180554_987x807_scrot.png
      :alt: 

#. Import into wireshark

   Two methods are available:

   -  Evaluate the Lua script in a Wireshark instance.

      In wireshark, select ``Tools > Lua > Evaluate`` and paste the
      generated code.

   -  Start wireshark with a specific Lua script.

      Start wireshark with the following parameters:
       ``wireshark -X lua_script:PATH_OF_LUA_SCRIPT``

      This will automatically import the Lua script on start.

#. Dissect data packets

   Within the lower panel of Wireshark, you should get the dissected packets:

   .. figure:: https://dev.netzob.org/attachments/160/2012-10-25-182017_956x1041_scrot_small.png
      :align: center
      :target: https://dev.netzob.org/attachments/85/2012-10-25-182017_956x1041_scrot.png
      :alt: 

Limitations
^^^^^^^^^^^

Variable size fields cannot be easily exported to the datamodel used by
Wireshark when we don't know the expected size. In this case, an error
message will popup preventing Netzob from generating the dissector. If
this happen, you have to complete the protocol model in order to find
the expected size of the dynamic field.

Improvements
^^^^^^^^^^^^

These ideas could be use to enhance dissection:

-  Use relations (field / size, repeat ...)
-  Look at future bitfield core implementation

What next ?
^^^^^^^^^^^

After this tutorial, we'll be glade to have feedbacks and to help you
(see our mailing list
`user@lists.netzob.org <mailto:user@lists.netzob.org>`_ or our IRC
channel #netzob on Freenode).

If you want to go further and `start contributing to
Netzob <http://www.netzob.org/development#becomecontributor>`_, that's
perfect. There are many simple or complex tasks everyone can do:
translation, documentation, bug fix, feature proposal or implementation.
