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
import traceback
import httplib2
import hashlib
import re

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.UI.Common.Views.BugReporterView import BugReporterView
from netzob import release
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from urllib2 import HTTPError
gi.require_version('Gtk', '3.0')
from gi.repository import GObject


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
class BugReporterController(object):
    """Manage the bug reporting when an exception occurs"""

    def __init__(self, exceptionClass, exceptionInstance, traceback):
        self.exceptionClass = exceptionClass
        self.exceptionInstance = exceptionInstance
        self.traceback = traceback
        self.apiKey = ResourcesConfiguration.extractAPIKeyDefinitionFromLocalFile()
        self._view = BugReporterView(self)
        self.log = logging.getLogger(__name__)
        self.shortTargetBugReport = "https://dev.netzob.org"
        self.targetBugReport = "{0}/projects/abr".format(self.shortTargetBugReport)

        self.project_id = "3"
        self.tracker_id = "1"
        self.customFieldSHA2ID = "5"

    @property
    def view(self):
        return self._view

    def bugReporter_cancel_clicked_cb(self, widget):
        """Callback executed when the user don't want to save the report"""
        self._view.bugReporter.destroy()

    def bugReporter_save_clicked_cb(self, widget):
        """callback executed when the user request to send the report"""
        self.log.debug("Start to send the report")
        reportContent = self.getReportContent()
        idDuplicateIssue = self.getIssueWithContent(reportContent)

        if idDuplicateIssue is not None:
            if idDuplicateIssue > 0:
                # Found a duplicated issue, we register the user as a watcher
                self.log.debug("Bug already reported but we register you on it")
                self.registerUserOnIssue(idDuplicateIssue)
        else:
            self.log.debug("Bug has not been reported")
            errorMessage = self.publishReport(reportContent)
            if errorMessage is None:
                pass

        # save the provided api key
        if self._view.bugReporterRememberAPIKeyCheckButton.get_active():
            # Remember the API Key
            self.log.info("Saving the API Key in the user configuration file.")
            ResourcesConfiguration.saveAPIKey(self.apiKey)
        else:
            # Forget the saved API Key
            self.log.debug("Forget the API Key from the user configuration file.")
            ResourcesConfiguration.saveAPIKey(None)

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
        self._view.bugTrackerEntry.set_text(self.targetBugReport)
        self._view.bugTrackerEntry.set_sensitive(False)
        if self.apiKey is not None:
            self._view.bugReporterApiKeyEntry.set_text(self.apiKey)
            self._view.bugReporterRememberAPIKeyCheckButton.set_active(True)
        else:
            self._view.bugReporterSaveButton.set_sensitive(False)
        self._view.reportTextView.get_buffer().set_text(self.getReportContent())
        self._view.run()

    def getReportContent(self):
        """Generates and returns the bug report content
        given the specified attributes which define the occurred exception."""
        reportContent = "Netzob version = {0}\n".format(release.version)
        reportContent = reportContent + ''.join(traceback.format_tb(self.traceback))
        reportContent = reportContent + '\n\n{0}: {1}'.format(self.exceptionClass, self.exceptionInstance)
        return reportContent

    def getIssueWithContent(self, reportContent):
        """Computes if an issue has this content.
        @return: -1 if an error occurred, None if none issue exists with the same reportContent, or the ID of the issue if it exists
        """
        sha1 = self.getSHA1Value(reportContent)
        try:
            h = httplib2.Http(disable_ssl_certificate_validation=False)
            api_url = "{0}/issues.xml?key={1}&project_id={2}&tracker_id={3}&cf_{4}={5}".format(self.targetBugReport, self.apiKey, self.project_id, self.tracker_id, self.customFieldSHA2ID, sha1)
            resp, content = h.request(api_url, 'GET')
            return self.getIssueIDFromXML(content)

        except HTTPError, e:
            logging.error("An HTTPError occurred while trying to report the bug {0}".format(e))
            errorMessage = "Impossible to connect to the remote server"
        return -1

    def publishReport(self, reportContent):
        """Send the report"""
        errorMessage = None

        subject = "Exception on {0}".format(self.exceptionClass)
        sha1 = self.getSHA1Value(reportContent)

        xmlContent = """<?xml version="1.0"?>
  <issue>
    <project_id>{0}</project_id>
    <tracker_id>{1}</tracker_id>
    <subject><![CDATA[{2}]]></subject>
    <description><![CDATA[{3}]]></description>
    <custom_fields type="array">
        <custom_field id="{4}">
            <value>{5}</value>
        </custom_field>
      </custom_fields>
  </issue>""".format(self.project_id, self.tracker_id, subject, reportContent, self.customFieldSHA2ID, sha1)
        try:
            h = httplib2.Http(disable_ssl_certificate_validation=False)
            api_url = "{0}/issues.xml?key={1}".format(self.targetBugReport, self.apiKey)
            resp, content = h.request(api_url, 'POST', xmlContent, headers={'Content-Type': 'application/xml'})
        except HTTPError, e:
            logging.error("An HTTPError occurred while trying to report the bug {0}".format(e))
            errorMessage = "Impossible to connect to the remote server"
        except Exception, e:
            logging.error("An Exception occurred while trying to report the bug {0}".format(e))
            errorMessage = "An exception occurred while reporting."
        return errorMessage

    def registerUserOnIssue(self, issueID):
        """Register the current user on the provided Issue ID"""
        """Send the report"""
        errorMessage = None

        xmlContent = """<?xml version="1.0"?>
  <issue>
      <notes>+1</notes>
  </issue>"""
        try:
            h = httplib2.Http(disable_ssl_certificate_validation=False)
            api_url = "{0}/issues/{1}.xml?key={2}".format(self.targetBugReport, issueID, self.apiKey)
            resp, content = h.request(api_url, 'PUT', xmlContent, headers={'Content-Type': 'application/xml'})
        except HTTPError, e:
            logging.error("An HTTPError occurred while trying to report the bug {0}".format(e))
            errorMessage = "Impossible to connect to the remote server"
        except Exception, e:
            logging.error("An Exception occurred while trying to report the bug {0}".format(e))
            errorMessage = "An exception occurred while reporting."
        return errorMessage

    def getSHA1Value(self, content):
        """Computes and returns the SHA1 value in string
        of the provided string"""
        m = hashlib.sha1(content)
        return str(m.hexdigest())

    def getIssueIDFromXML(self, content):
        """Parse the provided XML and search for
        a possible XML id of issue in it.
        It also verify the user didn't already report it
        """
        try:
            pos = content.index("<issue><id>")
            if pos > 0:
                pos2 = content[pos:].index("</id>")
                idIssue = content[pos + len("<issue><id>"):pos + pos2]
                if int(idIssue) > 0:

                    issueContent = self.getCompleteDefinitionOfIssue(idIssue)
                    if issueContent is not None:
                        # now we verify the user didn't already reported it
                        authorXML = self.getCurrentAuthorXMLDefinition()
                        if authorXML is None:
                            return 0

                        if authorXML in issueContent:
                            # author already reported it
                            self.log.debug("You have already reported/identified this bug, thank you")
                            return 0
                        else:
                            return int(idIssue)
        except Exception, e:
            logging.error("An exception occurred while parsing the XML : {0}".format(e))
        return None

    def getCompleteDefinitionOfIssue(self, idIssue):
        xmlContent = None
        try:
            h = httplib2.Http(disable_ssl_certificate_validation=False)
            api_url = "{0}/issues/{1}.xml?include=journals&key={2}".format(self.shortTargetBugReport, idIssue, self.apiKey)
            resp, xmlContent = h.request(api_url, 'GET')
        except HTTPError, e:
            logging.error("An HTTPError occurred while trying to fetch user info {0}".format(e))
        except Exception, e:
            logging.error("An Exception occurred while trying to fetch user info {0}".format(e))
        return xmlContent

    def getCurrentAuthorXMLDefinition(self):
        xmlAuthor = None
        try:
            h = httplib2.Http(disable_ssl_certificate_validation=False)
            api_url = "{0}/users/current.xml?key={1}".format(self.shortTargetBugReport, self.apiKey)
            resp, content = h.request(api_url, 'GET')

            regex = "<user><id>(.*)</id><login>(.*)</login><firstname>(.*)</firstname><lastname>(.*)</lastname>(.*)"
            m = re.search(regex, content)
            idUser = m.group(1)
            firstnameUser = m.group(3)
            lastnameUser = m.group(4)

            xmlAuthor = "name=\"{0} {1}\" id=\"{2}\"".format(firstnameUser, lastnameUser, idUser)

        except HTTPError, e:
            logging.error("An HTTPError occurred while trying to fetch user info {0}".format(e))
        except Exception, e:
            logging.error("An Exception occurred while trying to fetch user info {0}".format(e))
        return xmlAuthor
