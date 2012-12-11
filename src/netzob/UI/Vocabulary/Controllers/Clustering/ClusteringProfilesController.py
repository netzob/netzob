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
from locale import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.UI.Vocabulary.Views.Clustering.ClusteringProfilesView import ClusteringProfilesView
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class ClusteringProfilesController(object):
    """Manages the selection of the available clustering profiles"""

    def __init__(self, vocabularyController, fields=[]):
        self.vocabularyController = vocabularyController
        self.fields = fields
        self.profiles = []
        self.profiles.extend(vocabularyController.getCurrentWorkspace().getClusteringProfiles())
        self._view = ClusteringProfilesView(self, self.profiles)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def addAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Add selected algorithm in the list")

    def deleteCurrentAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Delete selected algorithm")

    def downCurrentAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Down the selected algorithm")

    def upCurrentAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Up the selected algorithm")

    def deleteProfileButton_clicked_cb(self, widget):
        self.log.info("Delete selected profile")

    def saveProfileButton_clicked_cb(self, widget):
        self.log.info("Save selected profile")

    def executeProfileButton_clicked_cb(self, widget):
        self.log.info("Execute selected profile")

    def closeButton_clicked_cb(self, widget):
        self.destroy()

    def run(self):
        self._view.run()

    def destroy(self):
        self._view.destroy()
