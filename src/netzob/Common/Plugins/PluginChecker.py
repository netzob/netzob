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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin


class PluginChecker(object):

    @staticmethod
    def isValidPlugin(pluginClass):
        """Checks if pluginClass is a valid Netzob plugin"""
        # We only have to check here that pluginClass inherits
        # from NetzobPlugin. We CANNOT use issubclass() here.
        # Indeed, as NetzobPlugin is an Abstract Base Class (abc), plugin
        # developers can register their class as a subclass of NetzobPlugin by
        # calling NetzobPlugin.register(MyPluginClass). Once a class is
        # registered (ie it was passed as first argument of the register
        # method), issubclass(MyPluginClass, NetzobPlugin) will return True.
        # When MyPluginClass is registered (by calling
        # NetzobPlugin.register(MyPluginClass)), python checks that all
        # abstract methods and abstract properties are implemented. However,
        # MyPluginClass does NOT inherits any method from NetzobPlugin.
        #
        # Here we want to make sure that pluginClass inherits from NetzobPlugin
        # and that it was not registered, that's why we cannot use issubclass here.
        #
        # See http://docs.python.org/library/abc.html
        # See http://www.doughellmann.com/PyMOTW/abc/index.html#module-abc
        if PluginChecker._inheritsFromNetzobPlugin(pluginClass):
            return True
        logging.error(("Plugin implemented in class {0} rejected because it "
                       "does not inherit from NetzobPlugin").format(pluginClass))
        return False

    @staticmethod
    def _inheritsFromNetzobPlugin(klass):
        parentClassList = klass.__bases__
        if NetzobPlugin in parentClassList:
            return True
        for parentClass in parentClassList:
            if PluginChecker._inheritsFromNetzobPlugin(parentClass):
                return True
        return False
