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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Inference.Vocabulary.Clustering.AbstractClusteringAlgorithm import AbstractClusteringAlgorithm
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.UI import NetzobWidgets


class ClusteringProfilesView(object):

    def __init__(self, controller, profiles):
        '''
        Constructor
        '''
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(),
                                                "ui", "vocabulary", "clustering",
                                                "clusteringProfilesView.glade"))
        self._getObjects(self.builder, ["clusteringProfilesDialog",
                                        "closeButton",
                                        "deleteProfileButton",
                                        "saveProfileButton",
                                        "customizeProfileToggleButton",
                                        "executeProfileButton",
                                        "availableAlgorithmsListStore",
                                        "currentAlgorithmsListStore",
                                        "profilesListStore",
                                        "nameProfileEntry",
                                        "descriptionProfileTextView",
                                        "addAlgorithmButton",
                                        "deleteCurrentAlgorithmButton",
                                        "downCurrentAlgorithmButton",
                                        "upCurrentAlgorithmButton",
                                        "availableClusteringProfilesComboBox",
                                        "configureCurrentAlgorithmViewport",
                                        "algorithmsComboBox",
                                        "availableAlgorithmsListStore",
                                        "currentAlgorithmsListStore",
                                        "currentAlgorithmsTreeView",
                                        "executionProgressBar",
                                        "customizeProfileBox",
                                        "saveAsProfileButton"
                                        ])
        self.controller = controller
        self.builder.connect_signals(self.controller)

        self.updateViewWithListOfClusteringProfiles(profiles)

    def updateViewWithListOfClusteringProfiles(self, profiles):
        self.profiles = profiles
        self.profilesListStore.clear()
        for profile in self.profiles:
            self.profilesListStore.append([str(profile.getID()), profile.getName(), str(profile.getDescription())])

    def _getObjects(self, builder, objectsList):
        for obj in objectsList:
            setattr(self, obj, builder.get_object(obj))

    def getCurrentProfile(self):
        """Returns the current selected profile"""
        selectedProfileID = None
        tree_iter = self.availableClusteringProfilesComboBox.get_active_iter()
        if tree_iter is not None:
            model = self.availableClusteringProfilesComboBox.get_model()
            selectedProfileID = model[tree_iter][0]

        if selectedProfileID is None:
            return None

        for profile in self.profiles:
            if str(profile.getID()) == selectedProfileID:
                return profile
        return None

    def getDescriptionOfCurrentProfile(self):
        descriptionBuffer = self.descriptionProfileTextView.get_buffer()
        if descriptionBuffer is not None:
            return descriptionBuffer.get_text(descriptionBuffer.get_start_iter(), descriptionBuffer.get_end_iter(), False)

    def getSelectedAlgorithmClassToAdd(self):
        selectedAlgoClass = None
        tree_iter = self.algorithmsComboBox.get_active_iter()
        if tree_iter is not None:
            model = self.algorithmsComboBox.get_model()
            selectedAlgoClass = model[tree_iter][0]
        if selectedAlgoClass is None:
            return None
        for algorithm in AbstractClusteringAlgorithm.getAllClusteringAlgorithms():
            if str(algorithm.__name__) == selectedAlgoClass:
                return algorithm
        return None

    def updateViewWithSelectedAlgorithmInCurrentProfile(self, algorithm):
        if algorithm is None:
            self.deleteCurrentAlgorithmButton.set_sensitive(False)
            self.downCurrentAlgorithmButton.set_sensitive(False)
            self.upCurrentAlgorithmButton.set_sensitive(False)
            self.clearCurrentAlgorithmViewPort()
        else:
            self.deleteCurrentAlgorithmButton.set_sensitive(True)
            self.downCurrentAlgorithmButton.set_sensitive(True)
            self.upCurrentAlgorithmButton.set_sensitive(True)
            self.clearCurrentAlgorithmViewPort()

    def updateButtonsWithSelectedAlgorithm(self, algorithm):
        if algorithm is None:
            self.addAlgorithmButton.set_sensitive(False)
        else:
            self.addAlgorithmButton.set_sensitive(True)

    def getCurrentAlgorithmSelected(self):
        selectedAlgorithmID = None
        selectionTreeview = self.currentAlgorithmsTreeView.get_selection()
        if selectionTreeview is None:
            return None

        (model, tree_iter) = selectionTreeview.get_selected()
        if tree_iter is not None:
            selectedAlgorithmID = model[tree_iter][0]

        if selectedAlgorithmID is None:
            return None

        for algorithm in self.getCurrentProfile().getAlgorithms():
            if str(algorithm.getID()) == selectedAlgorithmID:
                return algorithm
        return None

    def updateFieldWithCurrentProfile(self, profile=None):
        if profile is None:
            self.descriptionProfileTextView.get_buffer().set_text("")
            self.descriptionProfileTextView.set_sensitive(False)
            self.algorithmsComboBox.set_sensitive(False)

            self.addAlgorithmButton.set_sensitive(False)
            self.deleteProfileButton.set_sensitive(False)
            self.saveProfileButton.set_sensitive(False)
            self.saveAsProfileButton.set_sensitive(False)
            self.executeProfileButton.set_sensitive(False)

            self.clearCurrentAlgorithmViewPort()
            self.hideCustomizeProfile()
            self.customizeProfileToggleButton.set_active(False)
            self.customizeProfileToggleButton.set_sensitive(False)
        else:
            if profile.getDescription() is not None:
                self.descriptionProfileTextView.get_buffer().set_text(profile.getDescription())
            else:
                self.descriptionProfileTextView.get_buffer().set_text("")
            self.descriptionProfileTextView.set_sensitive(True)
            self.algorithmsComboBox.set_sensitive(True)
            self.addAlgorithmButton.set_sensitive(False)

            if profile.isWritable():
                self.saveProfileButton.set_sensitive(True)
                self.deleteProfileButton.set_sensitive(True)
            else:
                self.saveProfileButton.set_sensitive(False)
                self.deleteProfileButton.set_sensitive(False)

            self.saveAsProfileButton.set_sensitive(True)
            self.executeProfileButton.set_sensitive(True)

            self.availableAlgorithmsListStore.clear()
            for algorithm in AbstractClusteringAlgorithm.getAllClusteringAlgorithms():
                self.availableAlgorithmsListStore.append([str(algorithm.__name__), str(algorithm.__algorithm_name__)])

            self.currentAlgorithmsListStore.clear()
            for algorithm in profile.getAlgorithms():
                self.currentAlgorithmsListStore.append([str(algorithm.getID()), algorithm.getName()])

            self.clearCurrentAlgorithmViewPort()

            self.customizeProfileToggleButton.set_sensitive(True)

    def clearCurrentAlgorithmViewPort(self):
        children = self.configureCurrentAlgorithmViewport.get_children()
        for c in children:
            self.configureCurrentAlgorithmViewport.remove(c)

    def requestForDuplicateProfileName(self):
        """Request the new name of the profile through
        a dedicated dialog"""
        return NetzobWidgets.NetzobInputDialog(self.clusteringProfilesDialog, "Save as a new profile", "Profile's name", True)

    def requestForProfileName(self):
        """Request the new name of the profile through
        a dedicated dialog"""
        return NetzobWidgets.NetzobInputDialog(self.clusteringProfilesDialog, "Create a new clustering profile", "Profile's name", True)

    def askUserToConfirmDeleteProfile(self, profile):
        """Request the user to confirm before deleting
        the provided profile.
        @param profile the profile which will be deleted if the user accepts
        @return True if the user confirms the deletion of the profile"""
        return NetzobWidgets.NetzobQuestionMessage(_("Do you confirm the deletion of the clustering profile {0}".format(profile.getName())))

    def displayError(self, message):
        """Display a specific dialog to show an error to the user"""
        NetzobWidgets.NetzobErrorMessage(message, self.clusteringProfilesDialog)

    def run(self):
        self.clusteringProfilesDialog.run()

    def destroy(self):
        self.clusteringProfilesDialog.destroy()

    def showCustomizeProfile(self):
        self.customizeProfileBox.show_all()

    def hideCustomizeProfile(self):
        self.customizeProfileBox.hide()
