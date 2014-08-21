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
from netzob.Common.ApplicativeData import ApplicativeData, ApplicativeDataException
from netzob.UI.NetzobAbstractController import NetzobAbstractController
from netzob.UI.TraceManager.Views.ApplicativeDataImportView import ApplicativeDataImportView


class ApplicativeDataImportController(NetzobAbstractController):
    """Allow to import applicative data from files"""

    def __init__(self, mainController):
        super(ApplicativeDataImportController, self).__init__(mainController, ApplicativeDataImportView)
        self.logger = logging.getLogger(__name__)
        self.parsedApplicativeData = []

    def applyButton_clicked_cb(self, button):
        """applyButton_clicked_cb:
        Callback executed when the user apply the imports of found Applicative Data"""
        for data in self.parsedApplicativeData:
            self.logger.debug("Registerig application data {0} in session".format(data.getName()))
            self.mainController.getSession().addApplicativeData(data)
        self.parsedApplicativeData = []
        self.mainController.refresh()
        self.destroy()

    def cancelButton_clicked_cb(self, button):
        """cancelButton_clicked_cb:
        Callback executed when the user users wants to stop the import MVC"""
        self.destroy()

    def importFileChooserButton_file_set_cb(self, button):
        """importFileChooserButton_file_set_cb:
        Callback executed when the user has provided a new file"""
        # Retrieve the selected file
        toImport = self.view.getSelectedFileToImport()
        if toImport is None:
            self.logger.debug("No file selected, impossible to import it")
            return

        self.logger.debug("File to import: {0}".format(toImport))
        try:
            self.parsedApplicativeData = ApplicativeData.loadFromCSV(toImport)
            self.view.displayStatusMessage(_("{0} applicative data have been found.".format(len(self.parsedApplicativeData))))
            self.view.activateApply()
        except ApplicativeDataException, e:
            self.logger.warning("An error prevented to parse and extract the applicative data from provided file {0} : {1}".format(toImport, e))
            self.view.displayErrorMessage(_("Error : {0}".format(e)))
            self.view.deactivateApply()
