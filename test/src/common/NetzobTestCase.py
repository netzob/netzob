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
import unittest
import os.path
import logging
logging.basicConfig(level=logging.INFO)


# from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
# from netzob import NetzobResources
# from netzob.Common.Workspace import Workspace

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+


class NetzobTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.debug = True

    def setUp(self):
        pass
        # We compute the static resources path
        # resourcesPath = "resources/"
        # staticPath = os.path.join(resourcesPath, "static/netzob/")
        # NetzobResources.STATIC_DIR = staticPath

        # # We compute the test (user) resources path
        # resourcesPath = "test/resources/"
        # # We retrieve the full name of the child class (the caller)
        # for m in self.__class__.__module__.split('.'):
        #     resourcesPath = os.path.join(resourcesPath, m)
        # workspacePath = os.path.join(resourcesPath, ResourcesConfiguration.VAR_WORKSPACE_LOCALFILE)
        # # Before setting workspace, we verify it exists
        # if os.path.isdir(workspacePath):
        #     NetzobResources.WORKSPACE_DIR = workspacePath
