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
import inspect

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| PluginChecker:
#|     Checks if plugin is valid
#+---------------------------------------------------------------------------+
class PluginChecker(object):

    @staticmethod
    # The idea behind is "simple", we retrieve all the classes it implements
    # and verify the mandatory methods
    def isValidPlugin(pluginClass):
        logging.debug("Verify the plugin class {0} is a valid plugin".format(pluginClass))
        # First we retrieve its direct parents
        parentClasses = pluginClass.__bases__

        # We find which of its parent inherits from NetzobPlugin
        parentPluginClasses = []
        from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
        for parentClass in parentClasses:
            if issubclass(parentClass, NetzobPlugin):
                parentPluginClasses.append(parentClass)

        # The class doesn't subclass NetzobPlugin
        if len(parentPluginClasses) == 0:
            logging.warning("Plugin {0} is not a Netzob Plugin".format(pluginClass))
            return False

        # We retrieve all the method of the plugin class
        pluginMethods = inspect.getmembers(pluginClass, predicate=inspect.ismethod)

        # Now we verify if all the plugin parent classes are valid
        for parentPluginClass in parentPluginClasses:
            # We retrieve all the methods of our parent
            parentsMethods = inspect.getmembers(parentPluginClass, predicate=inspect.ismethod)

            # we compare and verify all the required methods are implemented
            for parentMethod in parentsMethods:
                found = False
                # Only methods marked as 'mandatory' are required
                if hasattr(parentMethod[1], "__mandatory__"):
                    mandatory = getattr(parentMethod[1], "__mandatory__")
                    if mandatory:
                        for pluginMethod in pluginMethods:
                            if parentMethod[0] == pluginMethod[0] and \
                                    (not hasattr(pluginMethod[1], "__mandatory__" or \
                                    not getattr(pluginMethod[1], "__mandatory__"))):
                                found = True
                                break
                        if not found:
                            logging.debug("Mandatory method {0} has not been found in plugin class.".format(parentMethod[0]))
                            return False

        return True
