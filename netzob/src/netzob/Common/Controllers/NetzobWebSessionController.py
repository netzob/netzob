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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from flask import Flask

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Web.Extensions.ExtensionManager import ExtensionManager
from netzob.Web.Modules.ModuleManager import ModuleManager


@NetzobLogger
class NetzobWebSessionController(object):
    """Execute Netzob web interface"""

    def __init__(self, listen_host, listen_port):
        self.__listen_host = listen_host
        self.__listen_port = listen_port
        self.__app = self.__create_app(
            debug_mode = True
        )

    def __create_app(self, debug_mode):
        """This internal methods create the Flask application and configures it"""

        app = Flask(__name__)

        # lets set various config values
        app.config['SECRET_KEY'] = "this-really-needs-to-be-changed"
        app.config['URL_PREFIX'] = "/api"
        app.config['SWAGGER_UI_JSONEDITOR'] = debug_mode

        # configure the web extensions
        extension_manager = ExtensionManager()
        extension_manager.init_app(app)

        # configure the web modules
        module_manager = ModuleManager()
        module_manager.init_app(app)

        return app

    def start(self):
        self._logger.warn("Netzob web interface is available at http://{}:{}".format(self.__listen_host, self.__listen_port))
        self.__app.run(
            host = self.__listen_host,
            port = self.__listen_port,
            debug = self.__app.config['DEBUG']
        )

