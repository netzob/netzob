.. currentmodule:: netzob

.. _installation_python:

Installation of Netzob
======================

This page presents how to install Netzob as a Python package.

Installing Netzob system dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First thing to do is to check the version of your python3 interpretor.
Netzob requires at least Python 3.8::

  $ python3 --version
  Python 3.8.10

You have to install the following system dependencies::

  $ apt-get install -y python3 python3-dev python3-setuptools virtualenv build-essential libpcap-dev libgraph-easy-perl libffi-dev

Then, create a virtualenv::

  $ mkdir venv
  $ virtualenv venv
  $ source venv/bin/activate

Installing Netzob from Pypi
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can install Netzob from Pypi (recommended choice)::

  (venv) $ pip3 install netzob

Installing Netzob from sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have retrieved Netzob sources, the installation procedure is::

  (venv) $ pip3 install Cython==0.29.32  # Should be manually installed because of setup.py direct dependency
  (venv) $ pip3 install -e .
  
API usage
---------

Once installed, we recommend to use the Netzob API inside scripts, with the following statement to import Netzob::

  from netzob.all import *

Start Netzob CLI
----------------

Netzob also provides its own CLI, in order to play interactively with it::

  (venv) $ netzob

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The folder *doc/documentation* contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
*doc/documentation/source* with the following command::

   $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/
