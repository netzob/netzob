.. currentmodule:: netzob

.. _installation_python:

Installation of Netzob
======================

This page presents how to install Netzob as a Python package.

Installing Netzob from sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First thing to do is to check the version of your python3 interpretor.
Netzob requires at least Python 3.8::

  $ python3 --version
  Python 3.8.10

Netzob is provided with its ``setup.py``. This file defines what and
how to install the project on a python hosting OS. This file depends
on ``setuptools`` which like few other modules cannot be automatically
installed.

You have to install the following system dependencies::

  $ apt-get install -y python3 python3-dev python3-setuptools virtualenv build-essential libpcap-dev libgraph-easy-perl libffi-dev

Then, create a virtualenv::

  $ cd netzob/
  $ mkdir venv
  $ virtualenv venv
  $ source venv/bin/activate

Once the required dependencies are installed, you can build and install Netzob::

  (venv) $ pip3 install Cython==0.29.32  # Should be manually installed because of setup.py dependency
  (venv) $ pip3 install -e .

We also highly recommend to install the following additional dependencies::

  (venv) $ pip3 install python-sphinx (for the documentation)

  
Once installed, running Netzob CLI is as simple as executing::

   $ netzob

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The folder *doc/documentation* contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
*doc/documentation/source* with the following command::

   $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/
