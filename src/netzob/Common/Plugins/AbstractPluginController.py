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
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Vocabulary.Controllers.VocabularyController import VocabularyController

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| AbstractPluginController:
#|     Regroup methods any plugins' controllers must be able to access
#+---------------------------------------------------------------------------+
class AbstractPluginController(object):

    def __init__(self, netzob, plugin, view):
        super(AbstractPluginController, self).__init__()
        self.netzob = netzob
        self.plugin = plugin
        self.view = view

    def getCurrentProject(self):
        """Computes the current project. It may returns None if no
        current project is yet loaded.
        @return: the current project L{netzob.Common.Project:Project}
        """
        return self.netzob.getCurrentProject()

    def getVocabularyController(self):
        """getVocabularyController:
                Returns the controller associated with the vocabulary"""
        return self.netzob.getPerspectiveController(VocabularyController.PERSPECTIVE_ID)

    def getPlugin(self):
        return self.plugin

    def getView(self):
        return self.view
