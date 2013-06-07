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
import code

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob import release


class NetzobInteractiveSessionController(object):
    """Execute Netzob in an Interactive Session"""

    DEFAULT_INTERPRETOR = "python -i"

    def __init__(self):
        self.console = code.InteractiveConsole()
        self.interpretor = NetzobInteractiveSessionController.DEFAULT_INTERPRETOR

    def start(self):
        if self.interpretor == NetzobInteractiveSessionController.DEFAULT_INTERPRETOR:
            self.console.runsource("from netzob.all import *")
            self.console.interact(banner=self.getBanner())

    def getBanner(self):
        """getBanner:
        Computes and returns a string which includes the
        banner to display on the interpretor startup.
        @return L{str}"""
        return """
+-----------------------------------------------------
| {0} {1} - {2}
+-----------------------------------------------------
| See Copyright:\t release.copyright
| See Contributors:\t release.contributors
| See License:\t\t release.license
+-----------------------------------------------------
| Reverse Deeper with Netzob ({3})
+-----------------------------------------------------
""".format(release.appname, release.version, release.versionName, release.url)
