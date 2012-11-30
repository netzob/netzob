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
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import pkg_resources
import os
import sys


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

#+----------------------------------------------
#| NetzobPluginManagement:
#+----------------------------------------------
class NetzobPluginManagement(object):
    """Netzob entry point in order to manage netzob plugins"""

    def __init__(self, commandLineParser):
        self.commandLineParser = commandLineParser

    def start(self):
        if self.commandLineParser.getOptions().plugin_list:
            self.listAvailablePlugins()

    def listAvailablePlugins(self):
        print "Available plugins:"
        for entrypoint in pkg_resources.iter_entry_points('netzob.plugins'):
            # load the plugin in memory
            plugin_class = entrypoint.load()
            plugin_path = sys.modules[plugin_class.__module__].__file__
            print "+ {0} located in {1}".format(entrypoint.name, plugin_path)
