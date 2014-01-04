# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2014 Georges Bossert and Frédéric Guihéry              |
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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractController import NetzobAbstractController
from netzob.UI.TraceManager.Views.ApplicativeDataManagerView import ApplicativeDataManagerView
from netzob.UI import NetzobWidgets
from netzob.Common.ApplicativeData import ApplicativeData, ApplicativeDataException
from netzob.UI.TraceManager.Controllers.ApplicativeDataImportController import ApplicativeDataImportController


class ApplicativeDataManagerController(NetzobAbstractController):
    """Manage the list of available plugins"""

    def __init__(self, mainController, trace, session):
        self.trace = trace
        self.session = session
        self.mainController = mainController
        super(ApplicativeDataManagerController, self).__init__(mainController, ApplicativeDataManagerView)
        self.logger = logging.getLogger(__name__)

    def getSession(self):
        return self.session

    def refresh(self):
        self.view.refresh()

    def applicativeDataManagerWindow_destroy_cb(self, widget):
        super(ApplicativeDataManagerController, self).destroy()
        self.mainController._refreshProjectProperties(trace=self.trace, session=self.session)

    def removeButton_clicked_cb(self, button):
        """removeButton_clicked_cb:
        Callback executed when the user wants to delete some selected new applicative data"""
        self.logger.debug("Remove selected applicative data")
        toRemove = self.view.getSelectedApplicativeData()
        if len(toRemove) > 0:
            for applicativeData in toRemove:
                self.session.removeApplicativeData(applicativeData)
            self.view.refresh()

    def importButton_clicked_cb(self, button):
        """importButton_clicked_cb:
        Callback executed when the user wants to import some Application Data from CSV"""
        self.logger.debug("Import Application Data from CSV")

        # Starts the proper controller
        importController = ApplicativeDataImportController(self)
        importController.run()
