==========================================
Netzob : Inferring Communication Protocols
==========================================

About Netzob
============

Functional Description
-----------------------

Netzob is an opensource tool for reverse engineering, traffic generation 
and fuzzing of communication protocols. This tool allows to infer the message format (vocabulary) 
and the state machine (grammar) of a protocol through passive and active processes. 
Its objective is to bring state of art academic researches to the operational field, 
by leveraging bio-informatic and grammatical inferring algorithms in a semi-automatic manner.

Netzob is suitable for reversing network protocols, structured files and system and 
process flows (IPC and communication with drivers and devices). 
Dedicated modules are provided to capture and import data in multiple contexts (network, file and process data acquisition). 
Once inferred, a protocol model can afterward be exported to third party tools (Peach, Scapy, Wireshark, etc.) 
or used in the traffic generation engine, to allow simulation of realistic and controllable communication endpoints and flows.

Netzob handles different types of protocols: text protocols (like HTTP and IRC), delimiter-based protocols, 
fixed fields protocols (like IP and TCP) and variable-length fields protocols (like TLV-based protocols).

Technical Description
---------------------

Netzob's source code is mostly made of Python (90%) with some specific
extensions in C (6%). It includes a graphical interface based on GTK3.

The tool is made of a core (officially maintained) and of bunch of
plugins (exporters, importers, ...). Some plugins are provided by the team while others are
created and managed directly by users.

More Information
---------------- 

:Website: `http://www.netzob.org <http://www.netzob.org>`_
:Email: `contact@netzob.org <contact@netzob.org>`_
:Mailing list: Two lists are available, use the `SYMPA web interface <https://lists.netzob.org/wws>`_ to register.
:IRC: You can hang-out with us on Freenode's IRC channel #netzob @ freenode.org.
:Wiki: Discuss strategy on `Netzob's wiki <https://dev.netzob.org/projects/netzob/wiki>`_
:Twitter: Follow Netzob's official accounts (@Netzob)

Get Started with Netzob
=======================

Install it
----------

There are two main ways of installing Netzob. The first one is based on 
per-OS installers while the other one is more 'pythonic'.

We recommend the per-OS installers for 'normal' users while
testers, developers and python experts might prefer the 'pythonic' way.

Per-OS Installers:
^^^^^^^^^^^^^^^^^^

Please follow the specification documentations for each supported platform:

:Debian/Ubuntu: `Installation documentation on Debian (wiki) <https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Debian>`_
:Gentoo: `Installation documentation on Gentoo (wiki) <https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Gentoo>`_

Pythonic Installer:
^^^^^^^^^^^^^^^^^^^

As a 'classic' python project, Netzob is provided with its
``setup.py``. This file defines what and how to install the project on a
python hosting OS.

This file depends on ``setuptools`` which like few other modules cannot be
automatically installed. The reason why, you have to manually install the 
following bunch of prerequisites before initiating Netzob's install process.

* python
* python-dev
* python-impacket
* libxml2-dev
* libxslt-dev
* python-setuptools
* python-gi
* gir1.2-gtk-3.0, gir1.2-glib-2.0, gir1.2-gdkpixbuf-2.0, gir1.2-pango-1.0
* libgtk-3-0
* graphviz

We also highly recommend to install the following additional dependencies:

* python-babel (for the translations)
* python-sphinx (for the documentation)

Once the required dependencies are installed, you can test (developer mode) Netzob::

  python setup.py build
  python setup.py develop

and install it::

  $ python setup.py install

Start it
--------

Once installed, running Netzob is as simple as executing the provided script::

  $ ./netzob

This script is in Python's path if you've installed Netzob, otherwise
(in developer mode), its located in the top distribution directory.


Miscellaneous
-------------

Configuration requirements for Network and PCAP input::

  $ sudo setcap cap_net_raw=ep /usr/bin/python2.XX

Configuration requirements for IPC input on Ubuntu::

  $ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"

Documentation
=============

The folder ``doc/documentation`` contains all the documentation of Netzob. 

The user manual can be generated based on RST sources located in folder
``doc/documentation/source`` with the following command::

  $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/

Contributing
============

There are multiple ways to help-us.

Defects and Features  Requests
------------------------------

Help-us by reporting bugs and requesting features using the `Bug Tracker <https://dev.netzob.org/projects/netzob/issues>`_.

Translation
-----------

Netzob has `support <https://dev.netzob.org/projects/netzob/wiki/Translation_support>`_ for translation. 
Currently English and French languages are supported. New languages are welcome.

Join the Development Team
-------------------------

To participate in the development, you need to get the latest version,
modify it and submit your changes. 

These operations are detailed on Netzob's wiki through the following
pages:

* `Accessing and using Git Repositories for Netzob development <https://dev.netzob.org/projects/netzob/wiki/Accessing_and_using_Git_Repositories_for_Netzob_development>`_
* `First steps for a new developer <https://dev.netzob.org/projects/netzob/wiki/First_steps_for_a_new_developer>`_

You're interested in joining, please contact-us !

Authors, Contributors and Sponsors
==================================

See the top distribution file ``AUTHORS.txt`` for the detailed and updated list 
of authors, contributors and sponsors.

License
=======

This software is licensed under the GPLv3 License. See the ``COPYING.txt`` file
in the top distribution directory for the full license text.
