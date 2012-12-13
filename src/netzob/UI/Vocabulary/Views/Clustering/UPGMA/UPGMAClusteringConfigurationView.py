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
import os
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Inference.Vocabulary.Clustering.AbstractDistanceAlgorithm import AbstractDistanceAlgorithm
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
#from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class UPGMAClusteringConfigurationView(object):

    def __init__(self, controller):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)
        from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui", "vocabulary", "clustering",
                                                "UPGMAClusteringConfigurationView.glade"))
        self._getObjects(self.builder, ["frame",
                                        "equivalenceSpinButton",
                                        "equivalenceThresholdScale",
                                        "equivalenceThresholdAdjustement",
                                        "distanceAlgorithmListStore"
                                        ])
        self.controller = controller
        self.builder.connect_signals(self.controller)

        # register all the distance available algorithms
        distancesAlgorithms = AbstractDistanceAlgorithm.getAllDistanceAlgorithms()
        for algo in distancesAlgorithms:
            self.distanceAlgorithmListStore.append([str(algo)])

    def getEquivalenceThresholdValue(self):
        return self.equivalenceThresholdAdjustement.get_value()

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self, viewport):
        viewport.add(self.frame)
        self.frame.show_all()

    def destroy(self):
        self.clusteringProfilesDialog.destroy()
