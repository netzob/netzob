.. currentmodule:: netzob

.. _installation_gentoo:

Installation documentation on Gentoo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From official portage (not yet available)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some build scripts have been published for future integration in
Portage.
While the scripts have not yet been accepted please refer to the
alternative procedure.

::

    # emerge -av netzob

From Gentoo overlay (recommended, automatic)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternative non official repositories are available on Gentoo which are
called "overlays".
The tool used to synchronize with these repositories is called "layman"

#. Installing layman

   ::

       # emerge app-portage/layman

#. Adding "lootr" repository containing Netzob ebuild scripts

   ::

       # layman -a lootr

#. Installing Netzob from this repository

   ::

       # emerge -av dev-python/netzob

From netzob repository (expert users only, manual installation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First step is to clone the netzob repository:

::

    # (~) git clone https://dev.netzob.org/git/netzob-gentoo.git

Then, declare this repository in the portage configuration file
*/etc/make.conf* by adding this line:

::

    PORTDIR_OVERLAY="/home/USER/netzob-gentoo/"

Synchronize portage

::

    # emerge --sync

Finally emerge Netzob package:

-  *tildarched (testing-like) systems:*

   ::

       # emerge -av netzob

-  *stable systems:*

   ::

       # ACCEPT_KEYWORDS="~x86" emerge -av netzob

