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

#+----------------------------------------------------------------------------
#| Global Imports
#+----------------------------------------------------------------------------
import os
import fileinput

from distutils.command.build_py import build_py


class pybuild_command(build_py):
    """Specialized builder for Netzob's python source file"""

    def getBID(self):
        """Retrieves from the definition of the C building process,
        the macros which include the definition of the BID.
        @return the BID is it exists (or None if not)"""

        for ext in self.distribution.ext_modules:
            for macro in ext.define_macros:
                if macro[0] is not None and macro[0] == "BID" and macro[1] is not None:
                    return macro[1]
        return None

    def build_module(self, module, module_file, package):
        result = build_py.build_module(self, module, module_file, package)

        if module_file == os.path.join("src", "netzob", "NetzobResources.py"):
            # Re-compute the path to the output file
            if isinstance(package, str):
                package = package.split('.')
            elif not isinstance(package, (list, tuple)):
                raise TypeError("'package' must be a string (dot-separated), list, or tuple")
            outfile = self.get_module_outfile(self.build_lib, package, module)
            if self.getBID() is not None:
                self.updateFileWithBID(outfile, self.getBID())
        return result

    def updateFileWithBID(self, file, bid):
        """Read the given file and rewrite it
        with the provided BID."""
        print("Update {0} with BID = {1}".format(file, bid))
        rFile = open(file, "r")
        initialContent = rFile.read()
        rFile.close()

        wFile = open(file, "w")
        wFile.write(initialContent.replace('BID = "$BID"', 'BID = {0}'.format(bid)))
        wFile.close()
