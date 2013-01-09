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
import uuid
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.ResourcesConfiguration import ResourcesConfiguration
from netzob.Common.Session import Session
from netzob.Common.Plugins.NetzobPlugin import NetzobPlugin
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.Common.Controllers.MoveMessageController import MoveMessageController
from netzob.UI.Vocabulary.Controllers.Menus.ContextualMenuOnLayerController import ContextualMenuOnLayerController
from netzob.UI.NetzobWidgets import NetzobQuestionMessage, NetzobErrorMessage, NetzobInfoMessage


#+----------------------------------------------
#| SessionController:
#|     Controller for session rendering
#+----------------------------------------------
class SessionController(object):

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self.netzob = vocabularyController.netzob
        self._view = vocabularyController._view
        self.log = logging.getLogger(__name__)

        self.view.sessionListTreeViewSelection.set_select_function(self.session_list_selection_function, None)
        self.session_list_set_selection = True

    @property
    def view(self):
        return self._view

    def updateLeftPanel(self):
        self.updateSessionList()
        self.updateSessionListToolbar()
        self.updateSessionProperties()

    ## Session List
    def updateSessionList(self):
        """Updates the session list of the left panel, preserving the current
        selection"""
        # Retrieve sessions of the current project vocabulary (if one selected)
        sessionList = []
        if self.getCurrentProject() is not None and self.getCurrentProject().getVocabulary() is not None:
            sessionList.extend(self.getCurrentProject().getVocabulary().getSessions())

        checkedSessionsIDList = []
        for row in self.view.sessionListStore:
            if (row[self.view.SESSIONLISTSTORE_SELECTED_COLUMN]):
                checkedSessionsIDList.append(row[self.view.SESSIONLISTSTORE_ID_COLUMN])
        # Block selection changed handler
        self.view.sessionListTreeViewSelection.handler_block_by_func(self.sessionListTreeViewSelection_changed_cb)
        self.view.sessionListStore.clear()
        for session in sessionList:
            pIter = self.addRowSessionList(checkedSessionsIDList, session.getName(),
                                          len(session.getMessages()),
                                          str(session.getID()))
        self.setSelectedSessionFromSelectedSessionTable()
        self.view.sessionListTreeViewSelection.handler_unblock_by_func(self.sessionListTreeViewSelection_changed_cb)

    def setSelectedSessionFromSelectedSessionTable(self):
        if self.vocabularyController.selectedMessageTable is None:
            self.setSelectedSession(None)
        else:
            sessionTableSession = self.vocabularyController.selectedMessageTable.displayedObject
            self.setSelectedSession(sessionTableSession)

    def addRowSessionList(self, checkedSessionsIDList, name, message, symID):
        """Adds a row in the session list of left panel
        @type  selection: boolean
        @param selection: if selected session
        @type  name: string
        @param name: name of the session
        @type  message: string
        @param message: number of message in the session
        @type  image: string
        @param image: image of the lock button (freeze partitioning)"""
        i = self.view.sessionListStore.append(None)
        self.view.sessionListStore.set(i, self.view.SESSIONLISTSTORE_SELECTED_COLUMN, (symID in checkedSessionsIDList))
        self.view.sessionListStore.set(i, self.view.SESSIONLISTSTORE_TOPLEVEL_COLUMN, True)
        self.view.sessionListStore.set(i, self.view.SESSIONLISTSTORE_NAME_COLUMN, name)
        self.view.sessionListStore.set(i, self.view.SESSIONLISTSTORE_MESSAGE_COLUMN, message)
        self.view.sessionListStore.set(i, self.view.SESSIONLISTSTORE_ID_COLUMN, symID)
        return i

    def updateSessionListToolbar(self):
        """Enables or disable buttons of the session list toolbar"""
        selectedSessionsCount = self.countSelectedSessions()
        self.view.concatSessionButton.set_sensitive((selectedSessionsCount >= 2))
        self.view.deleteSessionButton.set_sensitive((selectedSessionsCount >= 1))

        # We emit signals depending of the number of selected sessions
        if selectedSessionsCount == 0:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SESSIONS_NONE_CHECKED)
        elif selectedSessionsCount == 1:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SESSIONS_SINGLE_CHECKED)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SESSIONS_MULTIPLE_CHECKED)

    def countSelectedSessions(self):
        count = 0
        for row in self.view.sessionListStore:
            if row[self.view.SESSIONLISTSTORE_SELECTED_COLUMN]:
                count += 1
        return count

    def getCheckedSessionList(self):
        if self.getCurrentProject() is None:
            return []
        currentVocabulary = self.getCurrentProject().getVocabulary()
        selectedSessionList = []
        for row in self.view.sessionListStore:
            if row[self.view.SESSIONLISTSTORE_SELECTED_COLUMN]:
                session_id = row[self.view.SESSIONLISTSTORE_ID_COLUMN]
                session = currentVocabulary.getSessionByID(session_id)
                selectedSessionList.append(session)
        return selectedSessionList

    def setSelectedSession(self, session):
        selection = self.view.sessionListTreeView.get_selection()
        if session is None:
            selection.unselect_all()
        else:
            path = self.getSessionPathInSessionList(session)
            if path is not None:
                selection.select_path(path)

    def getSelectedSession(self):
        """Returns the selected session in the list of sessions"""
        currentVocabulary = self.getCurrentProject().getVocabulary()
        model, iter = self.view.sessionListTreeView.get_selection().get_selected()
        if iter is not None:
            symID = model[iter][self.view.SESSIONLISTSTORE_ID_COLUMN]
            return currentVocabulary.getSessionByID(symID)
        return None

    def getSessionPathInSessionList(self, session):
        symID = session.getID()
        for path, row in enumerate(self.view.sessionListStore):
            if row[self.view.SESSIONLISTSTORE_ID_COLUMN] == symID:
                return path

    def getDisplayedObject(self):
        if self.vocabularyController.selectedMessageTable is None:
            return None
        return self.vocabularyController.selectedMessageTable.getDisplayedObject()

    def getCurrentProject(self):
        return self.netzob.getCurrentProject()


    # Properties
    def getSessionProperties(self):
        """Create the list of properties associated
        with the current displayed session"""
        properties = []
        session = self.vocabularyController.getDisplayedObjectInSelectedMessageTable()
        if session is not None:
            properties = session.getProperties()
        return properties

    def updateSessionProperties(self):
        # clean store
        self.view.sessionPropertiesListstore.clear()
        # get session properties
        properties = self.getSessionProperties()
#        # add session properties
        for prop in properties:
            line = self.view.sessionPropertiesListstore.append()
            self.view.sessionPropertiesListstore.set(line, self.view.SESSIONPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.sessionPropertiesListstore.set(line, self.view.SESSIONPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.view.sessionPropertiesListstore.set(line, self.view.SESSIONPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.sessionPropertiesListstore.set(line, self.view.SESSIONPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    def getMessageProperties(self):
        """Retrieve the current first selected message (in the
        selected TableMessage) and return its properties"""
        properties = []
        messages = self.vocabularyController.getSelectedMessagesInSelectedMessageTable()
        if messages is not None and len(messages) > 0:
            message = messages[0]
            if message is not None:
                properties = message.getProperties()
        return properties

    def updateMessageProperties(self):
        # clean store
        self.view.messagePropertiesListstore.clear()
        # get message properties
        properties = self.getMessageProperties()
        # add message properties
        for prop in properties:
            line = self.view.messagePropertiesListstore.append()
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_NAME_COLUMN, prop.getName())
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_VALUE_COLUMN, str(prop.getCurrentValue()))
            self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_EDITABLE_COLUMN, prop.isEditable)
            if prop.getPossibleValues() != []:
                liststore_possibleValues = Gtk.ListStore(str)
                for val in prop.getPossibleValues():
                    liststore_possibleValues.append([val])
                self.view.messagePropertiesListstore.set(line, self.view.MESSAGEPROPERTIESLISTSTORE_MODEL_COLUMN, liststore_possibleValues)

    ## Session List toolbar callbacks
    def selectAllSessionsButton_clicked_cb(self, toolButton):
        """
        select all the session in the session list
        @type  widget: boolean
        @param widget: if selected session
        """
        for row in self.view.sessionListStore:
            row[self.view.SESSIONLISTSTORE_SELECTED_COLUMN] = True
        self.updateSessionListToolbar()

    def unselectAllSessionsButton_clicked_cb(self, toolButton):
        """
        unselect all the session in the session list
        @type  widget: boolean
        @param widget: if selected session
        """
        for row in self.view.sessionListStore:
            row[self.view.SESSIONLISTSTORE_SELECTED_COLUMN] = False
        self.updateSessionListToolbar()

    def createSessionButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return

        builder2 = Gtk.Builder()
        builder2.add_from_file(os.path.join(ResourcesConfiguration.getStaticResources(), "ui", "dialogbox.glade"))
        dialog = builder2.get_object("createsession")
        dialog.set_transient_for(self.netzob.view.mainWindow)

        # Disable apply button if no text
        applybutton = builder2.get_object("session-button1")
        entry = builder2.get_object("session-entry1")
        entry.connect("changed", self.entry_disableButtonIfEmpty_cb, applybutton)

        result = dialog.run()
        if (result == 0):
            newSessionName = entry.get_text()
            newSessionId = str(uuid.uuid4())
            self.log.debug("A new session will be created with the given name: {0}".format(newSessionName))
            currentProject = self.netzob.getCurrentProject()
            newSession = Session(newSessionId, newSessionName, currentProject, "")
            currentProject.getVocabulary().addSession(newSession)
            self.updateLeftPanel()
            dialog.destroy()
        if (result == 1):
            dialog.destroy()

    def entry_disableButtonIfEmpty_cb(self, widget, button):
        if(len(widget.get_text()) > 0):
            button.set_sensitive(True)
        else:
            button.set_sensitive(False)

    def concatSessionButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # retrieve the checked sessions
        sessions = self.view.getCheckedSessionList()

        # Create a new session
        newSession = Session(str(uuid.uuid4()), "Merged", self.getCurrentProject())

        # fetch all their messages
        for sym in sessions:
            newSession.addMessages(sym.getMessages())

        #delete all selected sessions
        self.vocabularyController.emptyMessageTableDisplayingObjects(sessions)
        for sym in sessions:
            self.getCurrentProject().getVocabulary().removeSession(sym)

        #add the concatenate session
        self.getCurrentProject().getVocabulary().addSession(newSession)

        #refresh view
        self.updateLeftPanel()

    def deleteSessionButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        # Delete session
        for sym in self.view.getCheckedSessionList():
            currentProject = self.netzob.getCurrentProject()
            currentVocabulary = currentProject.getVocabulary()
            for mess in sym.getMessages():
                currentVocabulary.removeMessage(mess)
            currentVocabulary.removeSession(sym)
            self.vocabularyController.emptyMessageTableDisplayingObjects([sym])
        # Update view
        self.vocabularyController.updateSelectedMessageTable()
        self.updateLeftPanel()

    def newSessionTableButton_clicked_cb(self, toolButton):
        if self.getCurrentProject() is None:
            NetzobErrorMessage(_("No project selected."))
            return
        self.vocabularyController.addMessageTable(Session)

    def toggleSessionCellRenderer_toggled_cb(self, widget, buttonid):
        # Update this flag so the line won't be selected.
        self.session_list_set_selection = False
        model = self.view.sessionListStore
        model[buttonid][0] = not model[buttonid][0]
        self.updateSessionListToolbar()

    def session_list_selection_function(self, selection, model, path, selected, data):
        """This method is in charge of deciding if the current line of
        session tree view (sessionListTreeViewSelection) should be
        selected.

        If the users clicked on the checkbox, then, the current line
        should _not_ be selected. In other cases, the current line is
        selected.

        """

        if not self.session_list_set_selection:
            self.session_list_set_selection = True
            return False

        return True

    def sessionListTreeViewSelection_changed_cb(self, selection):
        """Callback executed when the user
        clicks on a session in the list"""
        if 1 != selection.count_selected_rows():
            return
        logging.debug("The current session has changed")
        (model, paths) = selection.get_selected_rows()
        aIter = model.get_iter(paths[0])  # We work on only one session/layer
        currentVocabulary = self.netzob.getCurrentProject().getVocabulary()
        if aIter is not None:
            logging.debug("Iter is not none")
            # We first check if the user selected a session
            ID = model[aIter][self.view.SESSIONLISTSTORE_ID_COLUMN]
            session = currentVocabulary.getSessionByID(ID)
            #self.vocabularyController.executeMoveTargetOperation(field.getSession())
            self.vocabularyController.setDisplayedObjectInSelectedMessageTable(session)
            self.updateSessionProperties()
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SESSIONS_SINGLE_SELECTION)
        else:
            self.netzob.getSignalsManager().emitSignal(SignalsManager.SIG_SESSIONS_NO_SELECTION)

    def sessionListTreeView_button_press_event_cb(self, treeview, eventButton):
        if 1 > treeview.get_selection().count_selected_rows():
            return
        # Popup a contextual menu if right click
        if eventButton.type == Gdk.EventType.BUTTON_PRESS and eventButton.button == 3:
            (model, paths) = treeview.get_selection().get_selected_rows()

            layers = []
            for path in paths:
                # Retrieve the selected layerFields
                layer_id = model[path][VocabularyView.SESSIONLISTSTORE_ID_COLUMN]
                if layer_id is not None:
                    layer = self.getCurrentProject().getVocabulary().getFieldByID(layer_id)
                    layers.append(layer)
                else:
                    return

            # Popup a contextual menu
            menuController = ContextualMenuOnLayerController(self.vocabularyController, layers)
            menuController.run(eventButton)
            return True  # To discard remaining signals (such as 'changed_cb')

################ TO BE FIXED
    def button_newview_cb(self, widget):
        self.focus = self.addSpreadSheet("empty", 0)
        self.focus.idsession = None

    def button_closeview_cb(self, widget, spreadsheet):
        spreadsheet.destroy()

        #refresh focus
        if self.focus.get_object("spreadsheet") == spreadsheet:
            self.focus = None
