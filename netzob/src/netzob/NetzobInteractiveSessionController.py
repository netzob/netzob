# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
import code

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob import release
from netzob.Common.Utils.Decorators import NetzobLogger


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
+----------------------------------------------------+
| {0} {1} - {2}
+----------------------------------------------------+
| Copyright:\t print(release.copyright)
| Contributors:\t print(release.contributors)
| License:\t print(release.license)
+----------------------------------------------------+
| Reverse Deeper with Netzob ({3})
+----------------------------------------------------+
""".format(release.appname, release.version, release.versionName, release.url)


class NetzobIPythonShellController(NetzobInteractiveSessionController):
    """Execute Netzob in an IPython embedded shell"""

    def __init__(self):
        import IPython
        self.shell = IPython.terminal.embed.InteractiveShellEmbed()

    def start(self):
        import netzob.all
        self.shell(header=self.getBanner(), module=netzob.all)


@NetzobLogger
class NetzobSessionControllerFactory(object):
    def __call__(self):
        try:
            return NetzobIPythonShellController()
        except Exception as e:
            self._logger.warning(
                "Cannot initialize IPython shell: {}".format(e))
        return NetzobInteractiveSessionController()
