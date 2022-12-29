===========================================================
Netzob : Protocol Reverse Engineering, Modeling and Fuzzing
===========================================================

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
and fuzzing of communication protocols. This tool enables inference of the message format (vocabulary)
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

:Website: https://github.com/netzob/netzob
:Twitter: Follow Netzob's official accounts (@Netzob)

Get Started with Netzob
=======================

Install it
----------

First thing to do is to check the version of your python3 interpretor.
Netzob requires python 3.8::

  $ python3 --version
  Python 3.8.10

Netzob is provided with its ``setup.py``. This file defines what and
how to install the project on a python hosting OS. This file depends
on ``setuptools`` which like few other modules cannot be automatically
installed.

You have to install the following system dependencies::

  $ apt-get install -y python3 python3-dev python3-setuptools build-essential libpcap-dev libgraph-easy-perl libffi-dev

Then, create a virtualenv::

  $ mkdir venv
  $ virtualenv venv
  $ ./venv/bin/activate

Once the required dependencies are installed, you can build and install Netzob::

  (venv) $ pip3 install Cython==0.29.32  # Should be manually installed because of setup.py dependency
  (venv) $ pip3 install numpy==1.14.3    # Should be manually installed because of randomstate dependency
  (venv) $ pip3 install -e .

We also highly recommend to install the following additional dependencies::

  (venv) $ pip3 install python-sphinx (for the documentation)

  
Start Netzob CLI
----------------

Once installed, running Netzob CLI is as simple as executing the provided script::

  (venv) $ netzob

Miscellaneous
-------------

Configuration of Log Level
^^^^^^^^^^^^^^^^^^^^^^^^^^

Environment variable ```NETZOB_LOG_VERBOSITY``` can be use to set the logging level. The numeric values of logging levels are given in the Python Documentation of the `Logging Module <https://docs.python.org/3.5/library/logging.html#levels>`_. For example, the following command starts netzob in *DEBUG* mode::

  $ NETZOB_LOG_LEVEL=10 ./netzob

Configuration requirements for IPC input on Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following command must be triggered before collecting IPC exchanges with Netzob on Ubuntu (see https://www.kernel.org/doc/Documentation/security/Yama.txt)::

  $ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"

Documentation
=============

The folder ``doc/documentation`` contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
``doc/documentation/source`` with the following commands::

  $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/
  
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

You're interested in joining, please contact us!

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

.. figure:: https://raw.githubusercontent.com/netzob/netzob/next/netzob/doc/documentation/source/zoby.png
   :width: 200 px
   :alt: Zoby, the official mascot of Netzob
   :align: center

   Zoby, the official mascot of Netzob.
