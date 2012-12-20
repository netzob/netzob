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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk, GObject
import gi
gi.require_version('Gtk', '3.0')

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.BugReporter import BugReporter, BugReporterException
from netzob.UI.Common.Views.BugReporterView import BugReporterView
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI.Common.Views.BugReporterCertificateErrorView import BugReporterCertificateErrorView


class BugReporterController(object):

    def __init__(self, mainController, exceptionClass, exceptionInstance, traceback):
        self.exceptionClass = exceptionClass
        self.exceptionInstance = exceptionInstance
        self.traceback = traceback
        self.apiKey = ResourcesConfiguration.extractAPIKeyDefinitionFromLocalFile()
        self._view = BugReporterView(self, parent=mainController.view.mainWindow)
        self.log = logging.getLogger(__name__)
        self.disableRemoteCertificateVerification = False

        self.bugReporter = BugReporter()
        self.bugReporter.prepareBugReport(exceptionClass,
                                          exceptionInstance,
                                          traceback)

    @property
    def view(self):
        return self._view

    def bugReporter_cancel_clicked_cb(self, widget):
        """Callback executed when the user don't want to save the
        report"""

        self._view.bugReporter.destroy()

    def bugReporter_save_clicked_cb(self, widget):
        """callback executed when the user request to send the
        report"""

        # verify :
        # 0) server is UP
        # 1) server https certificate is known
        # 2) API Key is valid
        if not self.bugReporter.isServerUp():
            self.displayErrorAndInfoMessage(_("Impossible to contact the remote server."), None)
            return

        if not self.bugReporter.isServerCertificateValid():
            self.displayServerCertificate()
            return

        else:
            self.sendBugReport()

    def sendBugReport(self):
        try:

            # FIXME: update UI now that key is configured globally
            # save the provided api key
            apiKey = self._view.bugReporterApiKeyEntry.get_text()
            self.bugReporter.apiKey = apiKey
            if self._view.bugReporterRememberAPIKeyCheckButton.get_active():
                # Remember the API Key
                self.log.info("Saving the API Key in the user configuration file.")
                ResourcesConfiguration.saveAPIKey(apiKey)
            else:
                # Forget the saved API Key
                self.log.debug("Forget the API Key from the user configuration file.")
                ResourcesConfiguration.saveAPIKey(None)

            infoMessage = self.bugReporter.sendBugReport()

            self._view.bugReporterSaveButton.set_sensitive(False)
            self._view.bugReporterCancelButton.set_sensitive(True)
            self._view.bugReporterCancelButton.set_label(_("Close"))

            self.displayErrorAndInfoMessage(None, infoMessage)

        except BugReporterException, e:
            self.displayErrorAndInfoMessage(str(e), None)

    def displayErrorAndInfoMessage(self, errorMessage, infoMessage):
        self._view.bugReporterMessageBox.show_all()
        if errorMessage is not None:
            self._view.bugReporterWarnImg.show()
            self._view.bugReporterInfoImg.hide()
            self._view.bugReporterWarnLabel.set_text(errorMessage)
        elif infoMessage is not None:
            self._view.bugReporterInfoImg.show()
            self._view.bugReporterWarnImg.hide()
            self._view.bugReporterWarnLabel.set_text(infoMessage)
        else:
            self._view.bugReporter.destroy()

    def bugReporter_entry_changed_cb(self, widget):
        """Callback executed when the user modify the API Key entry"""

        self.apiKey = self._view.bugReporterApiKeyEntry.get_text()

        if self.apiKey is not None and len(self.apiKey) > 0:
            self._view.bugReporterSaveButton.set_sensitive(True)
        else:
            self._view.bugReporterSaveButton.set_sensitive(False)

    def run(self):
        """Run the controller and displays the view"""

        self._view.bugTrackerEntry.set_text(self.bugReporter.targetBugReport)
        self._view.bugTrackerEntry.set_sensitive(False)

        # FIXME: API key is now managed in workspace configuration
        apiKey = self.bugReporter.apiKey
        if apiKey is not None:
            self._view.bugReporterApiKeyEntry.set_text(apiKey)
            self._view.bugReporterRememberAPIKeyCheckButton.set_active(True)
        else:
            self._view.bugReporterSaveButton.set_sensitive(False)

        self._view.reportTextView.get_buffer().set_text(self.bugReporter.getReportContent())
        self._view.run()

    def displayServerCertificate(self):
        remoteCertificate = self.bugReporter.getServerCertificate()

        # Display the error dialog
        self._errorCertificateView = BugReporterCertificateErrorView(self)
        self._errorCertificateView.certificateErrorTextView.get_buffer().set_text(remoteCertificate)
        self._errorCertificateView.run()

    def certificateErrorApplyButton_clicked_cb(self, widget):
        self.disableRemoteCertificateVerification = True
        self._errorCertificateView.certificateError.destroy()

        self.displayErrorAndInfoMessage(_("The server's certificate won't be verified."), None)
        self.sendBugReport()

    def certificateErrorCancelButton_clicked_cb(self, widget):
        self.disableRemoteCertificateVerification = False
        self._errorCertificateView.certificateError.destroy()
