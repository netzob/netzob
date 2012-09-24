==========================================
Netzob : Inferring Communication Protocols
==========================================

About Netzob
============

Functionnal Description
-----------------------

**Netzob helps experts to reverse engineering communication protocols.**

It handles different types of protocols: text protocols (like HTTP and
IRC), fixed fields protocols (like IP and TCP) and variable fields
protocols (like ASN.1 based formats).  

Netzob is therefore suitable for reversing network protocols,
structured files and system and process flows (IPC and communication
with drivers). Netzob is provided with dedicated modules to capture
data in multiple contexts (network, file, process and kernel data
acquisition).

Technical Description
---------------------

Netzob's source code is mostly made of Python (90%) with some specific
extensions in C (6%). It includes a graphical interface based on GTK3.

The tool is made of a core (officialy maintained) and of bunch of
plugins. Some plugins are provided by the team while other plugins are
created and managed directly by users.

More Information
---------------- 

:Website: `http://www.netzob.org <http://www.netzob.org>`_
:Email: `contact@netzob.org <contact@netzob.org>`_
:Mailing list: Two lists are available, use the `SYMPA web interface <https://lists.netzob.org/wws>`_ to register on them.
:IRC: You can hang-out with us on Freenode's IRC channel `#netzob <irc://irc.freenode.net/netzob>`_
:Wiki: Discuss strategy on `Netzob's wiki <https://dev.netzob.org/projects/netzob/wiki>`_
:Twitter: Follow Netzob's official accounts (@Netzob)

Get Started with Netzob
=======================

Install it
----------

There are two main ways of installing Netzob. The first one is based on 
per-OS installers while the other one is more 'pythonic'.

We recommend the per-OS installers for 'normal' users while
testers, developpers and python experts might prefer the Pythonic way.

Per-OS Installers:
^^^^^^^^^^^^^^^^^^

Please follow the specification documentations for each supported platform:

:Debian/Ubuntu: `Installation documentation on Debian (wiki) <https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Debian>`_
:Gentoo: `Installation documentation on Gentoo (wiki) <https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Gentoo>`_

Pythonic Installer:
^^^^^^^^^^^^^^^^^^^

As a 'classic' Python project, Netzob is provided with its
``setup.py``. This file defines what and how to install the project on a
python hosting OS.

This file depends on setuptools which like few other modules cannot be
automaticaly installed. Its why, you need to manually install the followings :

* python
* python-dev
* libxml2-dev
* libxslt-dev
* python-setuptools
* gtk3

We also highly recommand to install the following additional dependencies :

* python-babel (for the translations)
* python-sphinx (for the documentation

Once the required dependencies are installed, you can test (developer mode) Netzob::

  python setup.py build
  python setup.py develop

and install it::

  $ python setup.py install

Start it
--------

Once installed, running Netzob is as simple as executing the provided script::

  $ ./netzob

This script is in Python's path if you've installed Netzob otherwise
(in developper mode), its located in the top distribution directory.

Documentation
=============

The folder ``doc/documentation`` contains all the documentation of Netzob. 

The user manual can be generated based on RST sources located in folder
``doc/documentation/source`` with the following command::

  $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/

Contributing
============

There are multiple ways to help-us.

Defeact and Features  Requests
------------------------------

Help-us by reporting bugs and requesting features using the `Bug Tracker <https://dev.netzob.org/projects/netzob/issues>`_.

Translation
-----------

Netzob has `support <https://dev.netzob.org/projects/netzob/wiki/Translation_support>`_ for translation. 
Currently english and french languages are supported. New languages are welcome.

Join the Development Team
-------------------------

To participate in the development, you need to get the latest version,
modify it and submit your changes. 

These operations are detailed on Netzob's wiki through the following
pages :

* `Accessing and using Git Repositories for Netzob development <https://dev.netzob.org/projects/netzob/wiki/Accessing_and_using_Git_Repositories_for_Netzob_development>`_
* `First steps for a new developer <https://dev.netzob.org/projects/netzob/wiki/First_steps_for_a_new_developer>`_

You're interested in joining, please contact-us !

Authors, Contributors and Sponsors
==================================

See ``Authors.rst`` file in the top distribution directory for the
updated list of Netzob's friends.

License
=======

This software is licensed under the GPLv3 License. See the ``COPYING.txt`` file
in the top distribution directory for the full license text.



  
