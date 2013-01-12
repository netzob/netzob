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

    def __init__(self, vocabularyController, symbols=[]):
        self.vocabularyController = vocabularyController
        self.symbols = symbols
        self.profiles = []
        self.profiles.extend(vocabularyController.getCurrentWorkspace().getClusteringProfiles())
        self._view = ClusteringProfilesView(self, self.profiles)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def algorithmsComboBox_changed_cb(self, widget):
        """Callback executed when the algorithms has changed"""
        currentAlgorithm = self._view.getSelectedAlgorithmClassToAdd()
        self._view.updateButtonsWithSelectedAlgorithm(currentAlgorithm)

    def availableClusteringProfilesComboBox_changed_cb(self, widget):
        """Callback executed when the user changes the current profile"""
        currentProfile = self._view.getCurrentProfile()
        self._view.updateFieldWithCurrentProfile(currentProfile)

    def addAlgorithmButton_clicked_cb(self, widget):
        currentAlgorithmClass = self._view.getSelectedAlgorithmClassToAdd()
        currentProfile = self._view.getCurrentProfile()

        currentProfile.addAlgorithm(currentAlgorithmClass())
        self._view.updateFieldWithCurrentProfile(currentProfile)

    def currentAlgorithmsTreeView_cursor_changed_cb(self, widget):
        currentAlgorithm = self._view.getCurrentAlgorithmSelected()
        self._view.updateViewWithSelectedAlgorithmInCurrentProfile(currentAlgorithm)

        if currentAlgorithm is not None:
            controller = currentAlgorithm.getConfigurationController()
            if controller is not None:
                controller.run(self._view.configureCurrentAlgorithmViewport)

    def deleteCurrentAlgorithmButton_clicked_cb(self, widget):
        currentProfil = self._view.getCurrentProfile()
        currentAlgorithm = self._view.getCurrentAlgorithmSelected()
        if currentProfil is not None and currentAlgorithm is not None:
            currentProfil.removeAlgorithm(currentAlgorithm)
        self._view.updateFieldWithCurrentProfile(currentProfil)

    def downCurrentAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Down the selected algorithm")

    def upCurrentAlgorithmButton_clicked_cb(self, widget):
        self.log.info("Up the selected algorithm")

    def deleteProfileButton_clicked_cb(self, widget):
        self.log.info("Delete selected profile")

    def saveProfileButton_clicked_cb(self, widget):
        self.log.info("Save selected profile")

        currentProfile = self._view.getCurrentProfile()
        if currentProfile is None:
            self.log.warning("No profile selected")
            return

        if not currentProfile.isWritable():
            self.log.warning("Cannot save the profile {0} since its not a writable one.".format(self.currentProfile.getName()))
            return

    def saveAsProfileButton_clicked_cb(self, widget):
        """This callback offers to duplicate the current profile
        under a new profile"""
        self.log.debug("Execute the save-as action on the current clustering profile")

        currentProfile = self._view.getCurrentProfile()
        if currentProfile is None:
            self.log.warning("No profile selected")
            return

        duplicateName = None
        # Request for profile name
        while duplicateName is None:
            duplicateName = self.view.requestForDuplicateProfileName()
            if duplicateName is None:
                return

            # Verify no profile already exists with this name
            found = False
            for profile in self.profiles:
                if profile.getName() == duplicateName:
                    found = True
                    break

            if found:
                self.log.debug("A profile with the name already exists.")
                self.view.displayError(_("A profile already exists with this name, please provide another one"))
                duplicateName = None

        self.log.debug("A new profil ({0}) will be created.".format(duplicateName))

        newProfile = currentProfile.duplicate(duplicateName)

        if newProfile is not None:
            # Save this profile in the workspace
            self.vocabularyController.getCurrentWorkspace().addClusteringProfile(newProfile)
            self.profiles.append(newProfile)
            self.view.updateViewWithListOfClusteringProfiles(self.profiles)
            self.log.debug("A duplicated profile has been successfuly created.")
        else:
            self.log.warning("An error occured which prevented the creation of the new profile")

    def executeProfileButton_clicked_cb(self, widget):
        currentProfile = self._view.getCurrentProfile()
        newSymbols = currentProfile.execute(self.symbols)
        if newSymbols is None or len(newSymbols) == 0:
            self.log.warning("An error occured while executing the clustering process")
            return
        # Update the current project with the new symbols
        currentVocabulary = self.vocabularyController.getCurrentProject().getVocabulary()
        for symbol in self.symbols:
            currentVocabulary.removeSymbol(symbol)
        for newSymbol in newSymbols:
            if len(newSymbol.getMessages()) > 0:
                currentVocabulary.addSymbol(newSymbol)
            else:
                self.log.debug("Remove an empty cluster from the results of the clustering algorithm")
        self.vocabularyController.restart()

        # Close the clustering profile view
        self.destroy()

    def customizeProfileToggleButton_toggled_cb(self, widget):
        if widget.get_active() and self._view.getCurrentProfile() is not None:
            self.view.showCustomizeProfile()
        elif not widget.get_active():
            self._view.hideCustomizeProfile()

    def closeButton_clicked_cb(self, widget):
        self.destroy()

    def run(self):
        self._view.run()

    def destroy(self):
        self._view.destroy()
