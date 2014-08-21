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
import logging
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractView import NetzobAbstractView


class ApplicativeDataImportView(NetzobAbstractView):

    def __init__(self, controller):
        gladeFile = os.path.join("traceManager", "applicativeDataImportDialog.glade")
        super(ApplicativeDataImportView, self).__init__(controller, gladeFile, root="applicativeDataImportDialog", parent=None)
        self._getObjects(["importFileChooserButton", "errorImage", "okImage", "statusLabel", "applyButton"])
        self.logger = logging.getLogger(__name__)
        self.deactivateApply()

    def run(self):
        super(ApplicativeDataImportView, self).run()
        self.displayErrorMessage(None)
        self.displayStatusMessage(None)

    def getSelectedFileToImport(self):
        """getSelectedFileToImport:
        returns the file which has been provided by the user
        through the interface."""
        return self.importFileChooserButton.get_filename()

    def displayStatusMessage(self, message):
        """displayStatusMessages:
        This method display the informtive message on the import status
        on the Interface and destroy any error message"""
        self.errorImage.set_visible(False)
        if message is None:
            self.okImage.set_visible(False)
            self.statusLabel.set_label("")
            self.statusLabel.set_visible(False)
        else:
            self.okImage.set_visible(True)
            self.statusLabel.set_label(message)
            self.statusLabel.set_visible(True)

    def displayErrorMessage(self, message):
        """displayErrorMessage:
        This method displays provided error message with its image and
        hide any status message"""
        self.okImage.set_visible(False)
        if message is None:
            self.errorImage.set_visible(False)
            self.statusLabel.set_label("")
            self.statusLabel.set_visible(False)
        else:
            self.errorImage.set_visible(True)
            self.statusLabel.set_label(message)
            self.statusLabel.set_visible(True)

    def cancelButton_clicked_cb(self, button):
        """cancelButton_clicked_cb:
        Callback executed when the user wants to close the import view"""
        self.destroy()

    def activateApply(self):
        """activateApply:
        This method set sensitive the apply button"""
        self.applyButton.set_sensitive(True)

    def deactivateApply(self):
        """deactivateApply:
        This methode prevent the user to click on the apply button"""
        self.applyButton.set_sensitive(False)
