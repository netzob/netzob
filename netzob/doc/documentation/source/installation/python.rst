.. currentmodule:: netzob

.. _installation_python:

Installation of Netzob
======================

This page presents how to install Netzob as a Python package.

Install Netzob from sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

  
Start Netzob
^^^^^^^^^^^^

Once installed, running Netzob CLI is as simple as executing::

   $ netzob

Netzob help options
^^^^^^^^^^^^^^^^^^^

Netzob handles some command line options::

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -w WORKSPACE, --workspace=WORKSPACE
                            Path to the workspace
      -b, --bug-reporter    Activate the bug reporter
      -d DEBUGLEVEL, --debugLevel=DEBUGLEVEL
                            Activate debug information ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

      Manage Netzob's plugins:
        --plugin-list       List the available plugins

Miscellaneous
^^^^^^^^^^^^^

Configuration requirements for IPC input on Ubuntu::

      $ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope" 

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The folder *doc/documentation* contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
*doc/documentation/source* with the following command::

      $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/
