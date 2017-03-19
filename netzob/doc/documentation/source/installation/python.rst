.. currentmodule:: netzob

.. _installation_python:

Installation documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

This page presents how to install Netzob as a Python package.

Dependency requirements
^^^^^^^^^^^^^^^^^^^^^^^

As a 'classic' python project, Netzob is provided with its *setup.py*.
This file defines what and how to install the project on a Python
hosting OS.

This file depends on *setuptools* which like few other modules cannot be
automatically installed. This is the reason why you have to manually
install the following bunch of prerequisites before initiating Netzob's
install process:

-  python
-  python-dev
-  python-impacket
-  libxml2-dev
-  libxslt-dev
-  python-setuptools
-  gtk3
-  graphviz

We also highly recommend to install the following additional
dependencies:

-  python-babel (for the translations)
-  python-sphinx (for the documentation)

Install Netzob with easy\_install
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

      $ easy_install netzob

Install Netzob from .tar.gz package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First retrieve the Netzob package:

::

      $ wget http://www.netzob.org/repository/XXX/Netzob-XXX.tar.gz

where XXX corresponds to the version you want to install (see
`http://www.netzob.org/download <http://www.netzob.org/download>`_ for
available versions).

Then, you can either install a package locally (developer mode) or on
the system.

Install Netzob locally (developer
mode)\ `¶ <#Install-Netzob-locally-developer-mode>`_

Once the required dependencies are installed, you can install Netzob on
its current directory:

::

      $ python setup.py build
      $ python setup.py develop --user

Install Netzob on the system\ `¶ <#Install-Netzob-on-the-system>`_

You can also install Netzob as a Python system package:

::

      $ python setup.py build
      $ python setup.py develop
      $ python setup.py install

Start Netzob
^^^^^^^^^^^^

Once installed, running Netzob is as simple as executing:

::

      $ ./netzob

Or if you've installed Netzob as a Python system package, just type:

::

      $ netzob

Netzob help options
^^^^^^^^^^^^^^^^^^^

Netzob handles some command line options:

::

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

Configuration requirements for Network and PCAP input:

::

      $ sudo setcap cap_net_raw=ep /usr/bin/python2.XX

Configuration requirements for IPC input on Ubuntu::

::

      $ sudo bash -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope" 

Building the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

The folder *doc/documentation* contains all the documentation of Netzob.

The user manual can be generated based on RST sources located in folder
*doc/documentation/source* with the following command:

::

      $ sphinx-build -b html doc/documentation/source/ doc/documentation/build/
