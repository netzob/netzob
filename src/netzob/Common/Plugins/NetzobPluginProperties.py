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
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.NetzobException import NetzobException
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin

class NetzobPluginProperties(NetzobPlugin):
    """This class allows easier implementation of a Netzob plugin
       and reduces the amount of boilerplate code written by providing
       the mandatory getName(), getVersion(), getDescription() and
       getAuthor() mandatory methods.

       For this methods to work properly,
       derived classes MUST INCLUDE the following attributes :
       - __plugin_name__ (str) : Name of the plugin
       - __plugin_version__ (str) : Version of the plugin
       - __plugin_version__ (str) : A description string for the plugin
       - __plugin_author__ (str) : Author of the plugin"""

    def getName(self):
        if not hasattr(self, "__plugin_name__"):
            raise NetzobException("Plugin using NetzobPluginProperties does not"
                    + " have the mandatory __plugin_name__ attribute")
        return self.__plugin_name__

    def getVersion(self):
        if not hasattr(self, "__plugin_version__"):
            raise NetzobException("Plugin using NetzobPluginProperties does not"
                    + " have the mandatory __plugin_version__ attribute")
        return self.__plugin_version__

    def getDescription(self):
        if not hasattr(self, "__plugin_description__"):
            raise NetzobException("Plugin using NetzobPluginProperties does not"
                    + " have the mandatory __plugin_description__attribute")
        return self.__plugin_description__

    def getAuthor(self):
        if not hasattr(self, "__plugin_author__"):
            raise NetzobException("Plugin using NetzobPluginProperties does not"
                    + " have the mandatory __plugin_author__ attribute")
        return self.__plugin_author__
