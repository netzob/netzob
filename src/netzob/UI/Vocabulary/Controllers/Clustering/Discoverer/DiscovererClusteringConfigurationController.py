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
from netzob.UI.Vocabulary.Views.Clustering.Discoverer.DiscovererClusteringConfigurationView import DiscovererClusteringConfigurationView

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


class DiscovererClusteringConfigurationController(object):
    """Controller for the configuration of the Discoverer Clustering process"""

    def __init__(self, DiscovererClustering):
        self.discovererClustering = DiscovererClustering
        self._view = DiscovererClusteringConfigurationView(self)
        self.logger = logging.getLogger(__name__)

    def getAlgorithm(self):
        return self.discovererClustering

    def maximumMessagePrefixAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getMaximumMessagePrefix())
        except Exception, e:
            self.log.warn("Invalid Maximum Message Prefix ({0}))".format(e))
            value = None
        self.discovererClustering.setMaximumMessagePrefix(value)

    def minimumLengthTextSegmentsAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getMinimumLengthTextSegments())
        except Exception, e:
            self.log.warn("Invalid Minimum Length Text Segments ({0}))".format(e))
            value = None
        self.discovererClustering.setMinimumLengthTextSegments(value)

    def minimumClusterSizeAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getMinimumClusterSize())
        except Exception, e:
            self.log.warn("Invalid Minimum Cluster Size ({0}))".format(e))
            value = None
        self.discovererClustering.setMinimumClusterSize(value)

    def maximumDistinctValuesFDAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getMaximumDistinctValuesFD())
        except Exception, e:
            self.log.warn("Invalid Maximum Distinct Values for FD ({0}))".format(e))
            value = None
        self.discovererClustering.setMaximumDistinctValuesFD(value)

    def alignmentMatchScoreAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getAlignmentMatchScore())
        except Exception, e:
            self.log.warn("Invalid Alignment Match Score ({0}))".format(e))
            value = None
        self.discovererClustering.setAlignmentMatchScore(value)

    def alignmentMismatchScoreAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getAlignmentMismatchScore())
        except Exception, e:
            self.log.warn("Invalid Alignment Mismatch Score ({0}))".format(e))
            value = None
        self.discovererClustering.setAlignmentMismatchScore(value)

    def alignmentGapScoreAdjustment_value_changed_cb(self, widget):
        try:
            value = int(self._view.getAlignmentGapScore())
        except Exception, e:
            self.log.warn("Invalid Alignment Gap Score ({0}))".format(e))
            value = None
        self.discovererClustering.setAliggnmentGapScore(value)

    @property
    def view(self):
        return self._view

    def run(self, attachedView):
        self._view.run(attachedView)

    def destroy(self):
        self._view.destroy()
