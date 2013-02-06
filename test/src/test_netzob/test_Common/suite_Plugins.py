# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2012 Georges Bossert and Frédéric Guihéry                   |
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
import unittest
import sys
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from common.NetzobTestCase import NetzobTestCase
import pkg_resources


def getSuite():
    functionsSuite = unittest.TestSuite()

    modulesOfTests = [test_Plugins]
    for module in modulesOfTests:
        functionsSuite.addTests(unittest.TestLoader().loadTestsFromTestCase(module))
    return functionsSuite


class test_Plugins(NetzobTestCase):

    def test_PluginList(self):
        """This test checks if all declared modules in the main source
        tree are compiled and loaded correctly.

        This is done by comparing the number of 'setup.py' under the
        src/netzob_plugins/*/* directory and the number of loadable
        plugins."""

        # Find loadable plugins
        loadedPlugins = 0
        for entrypoint in pkg_resources.iter_entry_points('netzob.plugins'):
            plugin_class = entrypoint.load()
            plugin_path = sys.modules[plugin_class.__module__].__file__
            loadedPlugins += 1

        # Find declared plugins (count plugins.py in src/netzob_plugins)
        availablePlugins = 0
        main_plugin_dir = os.path.abspath(os.path.join("src", "netzob_plugins"))
        plugin_categories = ["Capturers", "Importers", "Exporters"]
        for plugin_category in plugin_categories:
            plugin_dir = os.path.join(main_plugin_dir, plugin_category)
            plugin_list = os.listdir(plugin_dir)
            for plugin_name in plugin_list:
                if plugin_name != "__init__.py" and plugin_name != "__init__.pyc":
                    if os.path.isfile(os.path.join(plugin_dir, plugin_name, "setup.py")):
                        availablePlugins += 1

        self.assertEqual(loadedPlugins, availablePlugins)
