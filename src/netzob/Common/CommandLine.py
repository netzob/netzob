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
import optparse
import logging

#+---------------------------------------------------------------------------+
#| Local imports
#+---------------------------------------------------------------------------+
from netzob import release


#+----------------------------------------------
#| CommandLine
#+----------------------------------------------
class CommandLine(object):
    """Reads, validates and parses the command line arguments provided by
    users"""

    def __init__(self):
        self.parser = None
        self.providedOptions = None
        self.providedArguments = None
        self.configure()

    def configure(self):
        """Configure the parser based on Netzob's usage and the
        definition of its options and arguments"""
        self.usage = "usage: %prog [options]"
        self.parser = optparse.OptionParser(self.usage, prog=release.appname,
                                            version=release.version)
        self.parser.add_option("-w", "--workspace",
                               dest="workspace", help="Path to the workspace")
        self.parser.add_option("-b", "--bug-reporter", action="store_true", dest="bugReport", help="Activate the bug reporter")
        self.parser.add_option("-d", "--debugLevel", dest="debugLevel", help="Activate debug information ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')")

        # register the group of options for plugins
        groupPlugins = optparse.OptionGroup(self.parser, "Manage Netzob's plugins")
        groupPlugins.add_option('--plugin-list', help='List the available plugins', action="store_true", dest="plugin_list")
        self.parser.add_option_group(groupPlugins)

    def parse(self):
        """Read and parse the provided arguments and options"""
        (self.providedOptions, self.providedArguments) = self.parser.parse_args()

    def isStartGUIRequested(self):
        """Compute and return if the user requested (through the command line arguments and options)
        to start the GTK GUI"""
        if not self.isManagePluginsRequested():
            return True

    def isManagePluginsRequested(self):
        """Compute and return is the user has requested to manage the plugins"""
        if self.parser is None:
            self.parse()
        if self.providedOptions is None:
            return False
        return self.providedOptions.plugin_list

    def getOptions(self):
        return self.providedOptions

    def getConfiguredParser(self):
        """Return (if available) the parser configured to manage provided
        arguments and options by user.
        @return: the parser"""
        return self.parser
