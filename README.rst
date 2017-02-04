==========================================
Netzob : Inferring Communication Protocols
==========================================

.. image:: https://travis-ci.org/netzob/netzob.svg?branch=next
    :target: https://travis-ci.org/netzob/netzob
    :alt: Continuous integration

.. image:: https://coveralls.io/repos/github/netzob/netzob/badge.svg?branch=next
    :target: https://coveralls.io/github/netzob/netzob?branch=next
    :alt: Code coverage

.. image:: https://landscape.io/github/netzob/netzob/next/landscape.svg?style=flat
    :target: https://landscape.io/github/netzob/netzob/next
    :alt: Code health

.. image:: https://readthedocs.org/projects/gef/badge/?version=latest
    :target: https://netzob.readthedocs.org/en/latest/
    :alt: Doc

.. image:: https://img.shields.io/badge/Python-3-brightgreen.svg
    :target: https://github.com/netzob/netzob
    :alt: Python3

.. image:: https://img.shields.io/badge/freenode-%23netzob-yellowgreen.svg
    :target: https://webchat.freenode.net/?channels=#netzob
    :alt: IRC

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
Once inferred, a protocol model can be used in our traffic generation engine, to allow simulation of realistic
and controllable communication endpoints and flows.

Netzob handles different types of protocols: text protocols (like HTTP and IRC), delimiter-based protocols,
fixed fields protocols (like IP and TCP) and variable-length fields protocols (like TLV-based protocols).

Technical Description
---------------------

This version of Netzob must be used as a Python 3 library. It can either be imported in your scripts
or in your favorite interactive shell (ipython?).

Once installed, we recommend the following statement to import Netzob::

  from netzob.all import *

Netzob's source code is mostly made of Python (90%) with some specific extensions in C (6%). 

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

First thing to do is to check the version of your python3 interpretor.
Netzob requires python 3::

  $ python3 --version
  Python 3.4.2

As a 'classic' python project, Netzob is provided with its
``setup.py``. This file defines what and how to install the project on a
python hosting OS.

This file depends on ``setuptools`` which like few other modules cannot be
automatically installed. The reason why, you have to manually install the
following bunch of prerequisites before initiating Netzob's install process.

* python3
* python3-dev
* python3-setuptools
* build-essential  
  
We also highly recommend to install the following additional dependencies:

* python-sphinx (for the documentation)

Once the required dependencies are installed, you can build and install Netzob::

  # python3 setup.py install

Or if you prefer a more developer-friendly install::

  $ python3 setup.py develop --user

  
Docker container
^^^^^^^^^^^^^^^^

A docker build is offered from the docker registry repository. You can download 
it from command line with the following command:: 

  $ docker pull netzob/netzob


Start it
--------

Once installed, running Netzob is as simple as executing the provided script::

  $ ./netzob

This script is in Python's path if you've installed Netzob, otherwise
(in developer mode), it's located in the top distribution directory.

Docker container
^^^^^^^^^^^^^^^^

If you used the docker container, the following command will allow you to start 
netzob with your current directory attached to ``/data`` into the container::

  $ docker run --rm -it -v $(pwd):/data netzob/netzob

Miscellaneous
-------------

Configuration of Log Level
^^^^^^^^^^^^^^^^^^^^^^^^^^

Environment variable ```NETZOB_LOG_VERBOSITY``` can be use to set the logging level. The numeric values of logging levels are given in the Python Documentation of the `Logging Module <https://docs.python.org/3.5/library/logging.html#levels>`_. For example, the following command starts netzob in *DEBUG* mode::

  $ NETZOB_LOG_LEVEL=10 ./netzob

Configuration requirements for Network and PCAP input
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Capturing data from network interfaces often requires admin privileges. 
Before we provide a cleaner and secure way (see issue 425 on the bugtracker for updated information - https://dev.netzob.org/issues/425), a possible *HACK* is to provide additional capabilities to the python binary::

$ sudo setcap cap_net_raw=ep /usr/bin/python3.XX

Configuration requirements for IPC input on Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following command must be triggered before collecting IPC exchanges with Netzob on Ubuntu (see https://www.kernel.org/doc/Documentation/security/Yama.txt)::

$ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"

Documentation
=============

The folder ``doc/documentation`` contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
``doc/documentation/source`` with the following commands::

  $ sphinx-apidoc -T -e -f -o doc/documentation/source/developer_guide/API/ src/netzob/
  $ find doc/documentation/source/developer_guide/API/ -type f -exec sed -i ':a;N;$!ba;s/Subpackages\n-----------\n\n.. toctree::\n/Subpackages\n-----------\n\n.. toctree::\n    :maxdepth: 1\n    /g' {} +
  $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/

An up-to-date version of the documentation is hosted on the `Read The Docs platform <https://netzob.readthedocs.org>`_.
  
Contributing
============

There are multiple ways to help-us.

Defects and Features  Requests
------------------------------

Help-us by reporting bugs and requesting features using the `Bug Tracker <https://github.com/netzob/netzob/issues>`_.

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

Licenses
========

This software is provided under the GPLv3 License. See the ``COPYING.txt`` file
in the top distribution directory for the full license text.

The documentation is under the CC-BY-SA licence.


Extra
=====

.. figure:: http://www.netzob.org/img/logo.png
   :width: 200 px
   :alt: Zoby, the official mascot of Netzob
   :align: center

   Zoby, the official mascot of Netzob.
