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
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration


class SequenceAlignmentView(object):

    def __init__(self, controller):
        '''
        Constructor
        '''
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(
            ResourcesConfiguration.getStaticResources(),
            "ui", "vocabulary", "partitioning",
            "sequenceAlignement.glade"))
        self._getObjects(self.builder, ["sequenceDialog", "similarity_box",
                                        "sequence_execute", "sequence_cancel", "sequence_stop",
                                        "sequence_adjustment", "sequence_scale", "sequence_spinbutton",
                                        "radiobutton4bit", "radiobutton8bit",
                                        "orphanButton", "smoothButton",
                                        "sequence_progressbar", "stage0ProgressBar", "stage1ProgressBar",
                                        "stage2ProgressBar", "stage3ProgressBar", "stage4ProgressBar",
                                        "labelStage0", "labelStage1", "labelStage2", "labelStage3", "labelStage4"])
        self.controller = controller
        self.builder.connect_signals(self.controller)

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def run(self):
        self.sequenceDialog.run()

    def resetProgressBars(self):
        """Reset the initial values of all the
        progress bars declared in the interface."""
        self.labelStage0.show()
        self.stage0ProgressBar.show()
        self.stage0ProgressBar.set_fraction(0)

        self.labelStage1.show()
        self.stage1ProgressBar.show()
        self.stage1ProgressBar.set_fraction(0)

        self.labelStage2.show()
        self.stage2ProgressBar.show()
        self.stage2ProgressBar.set_fraction(0)

        self.labelStage3.show()
        self.stage3ProgressBar.show()
        self.stage3ProgressBar.set_fraction(0)

        self.labelStage4.show()
        self.stage4ProgressBar.show()
        self.stage4ProgressBar.set_fraction(0)

        self.sequence_progressbar.set_fraction(0)
