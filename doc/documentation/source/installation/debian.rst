.. currentmodule:: netzob

.. _installation_debian:


Installation documentation on Debian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Netzob's APT Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A dedicated APT repository (apt.netzob.org) is available for downloading
and installing Netzob.

Steps:

#. edit you ``/etc/apt/sources.list`` to add the netzob's repository
   URL,
#. import the GPG key used to sign the repository,
#. install netzob threw ``apt-get``.

Edit ``/etc/apt/sources.list``

You need to register the repository in your APT client by adding the
following entry (stable or unstable) in your ``/etc/apt/sources.list``
or through a dedicated file in ``/etc/apt/sources.list.d/``. Then you
need to import the gpg public key used to sign the repository.

**Unstable & testing ("Wheezy")**

::

    deb http://apt.netzob.org/debian/ unstable main
    deb-src http://apt.netzob.org/debian/ unstable main

**Stable ("Squeeze")**

::

    deb http://apt.netzob.org/debian/ squeeze-backports main
    deb-src http://apt.netzob.org/debian/ squeeze-backports main

Import GPG key\ `¶ <#Import-GPG-key>`_

The repository is signed, so APT may complain until you register the
archive key ``0xE57AEA26`` to your APT keyring. The fingerprint of the
key is ``D865 DCF0 9B9A 195C 49F0 E3F3 F750 1A13 E57A EA26`` and has
been signed by the followings:

-  0xA255A6A3 : Georges Bossert
   <`georges.bossert@supelec.fr <mailto:georges.bossert@supelec.fr>`_\ >
-  0x561F7A47 : Frederic Guihery
   <`frederic.guihery@amossys.fr <mailto:frederic.guihery@amossys.fr>`_\ >
-  0x04B1A89C : Olivier Tetard
   <`olivier.tetard@amossys.fr <mailto:olivier.tetard@amossys.fr>`_\ >

To import the key of the APT repository you can execute the following
commands :

::

    # wget https://dev.netzob.org/misc/debian_archive.asc -O -| gpg --import
    # gpg --export -a 0xF7501A13E57AEA26 | sudo apt-key add -

Install netzob\ `¶ <#Install-netzob>`_

You can install it with the following commands :

::

    # apt-get update
    # apt-get install netzob

Using the provided Debian package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing Netzob directly from the debian package (deb file) implies
you manually install the necessary packages in order to handle the
required dependencies. Therefore, the following commands can be executed
to install them :

::

    # apt-get install python python-ptrace python-hachoir-subfile python-matplotlib python-dpkt strace lsof python-pcapy python-bitarray python-dev libjs-sphinxdoc python-sphinx

Once the requirements are fullfilled you can download the debian file
(i386 or amd64) and install it using the following command for an i386
architecture (32 bits) :

::

    # dpkg -i netzob_0.3.0-1_i386.deb

or for an AMD64 (64 bits) :

::

    # dpkg -i netzob_0.3.0-1_amd64.deb

