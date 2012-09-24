..#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

About Netzob
============

Functionnal Description
-----------------------

Netzob is a complete framework for the reverse engineering of
communication protocols.

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

:Website: .. _netzob.org: http://www.netzob.org
:IRC: You can hang-out with us on Freenode's IRC channel .. _#netzob: irc://irc.freenode.net/netzob
:Wiki: Discuss strategy on .. _Netzob's wiki: https://dev.netzob.org/projects/netzob/wiki
:Twitter / Identica: Follow Netzob's official accounts on your favorite platform (@Netzob)

Get Started with Netzob
=======================

Install it
----------

There are two main ways of installing Netzob. The first one is based on 
per-OS installers while the other one is more 'pythonic'.

We recommend the per-OS installers for 'normal' users while
testers, developpers and python experts might prefer the Pythonic way.

Per-OS Installers:
------------------

Please follow the specification documentations for each supported platform:
:Debian/Ubuntu: .. _Installation documentation on Debian (wiki): https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Debian
:Gentoo: .. _Installation documentation on Gentoo (wiki): https://dev.netzob.org/projects/netzob/wiki/Installation_documentation_on_Gentoo

Pythonic Installer:
-------------------
As a 'classic' Python project, Netzob is provided with its
setup.py. This file defines what and how to install the project on a
python hosting OS.

This file depends on setuptools which like few other modules cannot be
automaticaly installed. Its why, you need to manually install the followings :

* python
* python-dev
* libxml2-dev
* libxslt-dev
* python-setuptools
* gtk3

Once the required dependencies are installed, you can test (developer mode) Netzob::
  python setup.py build
  python setup.py develop

and install it::
  python setup.py install


Authors, Contributors and Sponsors
==================================



Authors:
* Georges Bossert
* Frédéric Guihéry

Contributors:
* Olivier Tétard (Debian package maintainer)
* Goulven Guiheux (Windows package developer and maintainer)
* Maxime Olivier (Quality enforcer)
* Alexandre Pigné (Gentoo package maintainer)
* Franck Roland (developer)
* Fabien André (developer)
* Quentin Heyler (developer)
* Benjamin Dufour (developer)

Sponsors:
* AMOSSYS: http://www.amossys.fr
* Supélec: http://www.rennes.supelec.fr/ren/rd/cidre/





  
