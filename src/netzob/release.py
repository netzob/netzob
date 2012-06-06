# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
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

#+---------------------------------------------------------------------------+
#| Official name of the project : Netzob
#+---------------------------------------------------------------------------+
name = "Netzob"

#+---------------------------------------------------------------------------+
#| Official name of the application
#+---------------------------------------------------------------------------+
appname = name

#+---------------------------------------------------------------------------+
#| Current OFFICIAL version of the application
#|    the version number must be changed during the last commit before
#|    the tag release.
#|    Development version has version number increased and is
#|    postfixed by ~git
#+---------------------------------------------------------------------------+
version = "0.3.3"
versionName = "FlyingRazorback"

#+---------------------------------------------------------------------------+
#| Copyright mentions
#+---------------------------------------------------------------------------+
copyright = "Copyright (C) 2011 Georges Bossert and Frédéric Guihéry"

#+---------------------------------------------------------------------------+
#| Description of the application
#+---------------------------------------------------------------------------+
description = "Inferring communication protocols"

#+---------------------------------------------------------------------------+
#| Platforms on which the application can be executed
#+---------------------------------------------------------------------------+
platforms = "Linux_x86, Linux_x64"

#+---------------------------------------------------------------------------+
#| Authors names
#+---------------------------------------------------------------------------+
author = "Georges Bossert, Frédéric Guihéry"

#+---------------------------------------------------------------------------+
#| Email to contact authors
#+---------------------------------------------------------------------------+
author_email = "contact@netzob.org"

#+---------------------------------------------------------------------------+
#| Official website of the application
#+---------------------------------------------------------------------------+
url = "http://www.netzob.org"

#+---------------------------------------------------------------------------+
#| Official url to download the application
#+---------------------------------------------------------------------------+
download_url = "http://www.netzob.org/download"

#+---------------------------------------------------------------------------+
#| Keywords to describe the application
#+---------------------------------------------------------------------------+
keywords = ["Protocol", "Inference", "Networking", "Reverse Engineering", "Security"]

#+---------------------------------------------------------------------------+
#| Long description
#+---------------------------------------------------------------------------+
long_description = """
Inferring communication protocols

=================================


Netzob simplifies the work for security auditors by providing a complete framework
for the reverse engineering of communication protocols.


It handles different types of protocols : text protocols (like HTTP and IRC), fixed fields protocols (like IP and TCP)
and variable fields protocols (like ASN.1 based formats).
Netzob is therefore suitable for reversing network protocols, structured files and system and process
flows (IPC and communication with drivers). Netzob is provided with modules dedicated to capture data in
multiple contexts (network, file, process and kernel data acquisition)."""

#+---------------------------------------------------------------------------+
#| License used to publish the tool
#+---------------------------------------------------------------------------+
licenseName = "GPLv3"
license = """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
