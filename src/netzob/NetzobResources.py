# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import os.path
import sys

#+---------------------------------------------------------------------------+
#| Establishes the path for static resources
#+---------------------------------------------------------------------------+
STATIC_DIR = os.path.join(sys.exec_prefix, "share/netzob")
LOCAL_STATIC_DIR = "./resources/static/netzob"

PLUGINS_STATIC_DIR = os.path.join(sys.exec_prefix, "share/netzob/plugins")
LOCAL_PLUGINS_STATIC_DIR = "./resources/static/netzob_plugins"

#+---------------------------------------------------------------------------+
#| Establishes the path for workspace resources (only used by testing)
#+---------------------------------------------------------------------------+
WORKSPACE_DIR = None

#+---------------------------------------------------------------------------+
#| Locale's directory
#+---------------------------------------------------------------------------+
LOCALES_DIR = os.path.join(sys.exec_prefix, "share/locale")
LOCAL_LOCALES_DIR = "./resources/static/netzob/locales/"


#+---------------------------------------------------------------------------+
#| Unique Binary Identifier (DO NOT EDIT ITS VALUE)
#| Warning, this variable is automatically updated in the building process.
#| None : It's the copied version of this file which will be edited not this one.
#+---------------------------------------------------------------------- -----+
BID = "$BID"
