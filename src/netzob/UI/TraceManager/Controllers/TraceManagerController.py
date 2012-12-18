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
from gi.repository import Gtk, Gdk
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.TraceManager.Views.TraceManagerView import TraceManagerView
from netzob.UI.NetzobAbstractPerspectiveController import NetzobAbstractPerspectiveController


class TraceManagerController(NetzobAbstractPerspectiveController):
    """Trace Manager Controller. This view allows to manage traces
    that were imported in Netzob. This panel is accessible through the
    main view, using the switch panel dropdown."""

    def __init__(self, mainController):
        self.workspace = mainController.getCurrentWorkspace()
        super(TraceManagerController, self).__init__(mainController, TraceManagerView)

        self.currentTrace = None
        self.nameUpdated = False
        self.descriptionUpdated = False

        # Type of the data selected on the left treeview
        # ('TraceTreeView'). True means that ImportedTrace is/are
        # selected, else it means that Session is/are selected. We
        # can't have two types.
        self.traceSelectionIsATrace = None

        # Do we keep a copy of old traces on merge operations?
        self.mergeKeepCopy = True

        self._refreshTraceList()

    def _refreshTraceList(self, traceListIds=[], removedTraces=[]):
        """This function is the central place for updating the left
        treeview. It is in charge of adding or updating the model
        associated to the treeview, in a way the user won't notice it
        (the expanded rows are kept expanded, etc.).

        :param traceListIds: the list of traces that needs to be
        updated. If this list is empty, it means that we have to
        refresh the whole treeview."""

        def compare(a, b):
            return cmp(a.name.lower(), b.name.lower())

        traceListIds = set(traceListIds)

        view = self.view.traceTreeview
        model = view.get_model()

        # We refresh the complete trace list if no argument is passed.
        # In all cases, we store all traces to be added/updated in a
        # traceList list.
        if len(traceListIds) == 0:
            traceList = self.workspace.getImportedTraces()
            traceList.sort(cmp=compare)
            model.clear()
        else:
            traceList = map(lambda tid: self.workspace.getImportedTrace(tid), traceListIds)

        # All traces that are already in the 'model' are added in the
        # tracesInModel list.
        tracesInModel = []
        for item in model:
            tracesInModel.append(item[0])

        # First, we add all the traces that are not in the model.
        for trace in traceList:

            # Check if the trace is already in the model. If so, we
            # don't need to add in the model now.
            insert = True
            if trace.id in tracesInModel:
                insert = False
                continue

            # If not, let's insert it. We don't need to update the
            # sessions here, since these will be updated in the next
            # big block
            if insert:
                traceListIds.add(trace.id)

                date = trace.date.strftime("%x %X")
                tstamp = time.mktime(trace.date.timetuple())

                model.append(None,
                             [trace.id, trace.name, str(len(trace.messages)), date, str(tstamp)])

        selection = view.get_selection()

        # We save the selected rows, to select them again at the end.
        (model, selectedPaths) = selection.get_selected_rows()

        try:
            # We hold the 'changed' signal on the treeselection to avoid conflicts.
            selection.handler_block_by_func(self.traceTreeviewSelection_changed_cb)

            treeIter = model.get_iter_first()
            while treeIter is not None:
                # We iter over the traces in the model and update the
                # sessions if requested. Here we pay attention to keep
                # selection and expanded rows.

                path = model.get_path(treeIter)
                row = model[treeIter]
                expanded = view.row_expanded(path)

                # If we asked to refresh this trace
                if row[0] in traceListIds and row[0] not in removedTraces:
                    # Remove all children
                    for child in row.iterchildren():
                        model.remove(child.iter)

                    trace = self.workspace.getImportedTrace(row[0])
                    sessions = trace.getSessions()
                    sessions.sort(cmp=compare)

                    # Append all defined sessions
                    for session in sessions:
                        model.append(treeIter,
                                     [session.id, session.name, str(len(session.getMessages())), "", ""])

                    model.set_value(row.iter, 2, str(len(trace.getMessages())))

                # Let's expand the trace, if it was expanded before.
                if expanded:
                    view.expand_to_path(path)

                treeIter = model.iter_next(treeIter)

                # Trace has gone, we can remove it. We have to do this
                # at the end, just after we retrieve the next iter
                # (else, the iter_next() call will fail).
                if row[0] in removedTraces:
                    model.remove(row.iter)
        finally:
            # We unhold the 'changed' signal
            selection.handler_unblock_by_func(self.traceTreeviewSelection_changed_cb)

        # We select the previously selected rows
        if len(selectedPaths) > 0:
            selection.unselect_all()
            selection.select_path(selectedPaths[0])

    def deactivate(self):
        self.workspace.saveConfigFile()

    def traceTreeviewSelection_select_function_cb(self, selection, model, path, is_path_selected, treeStore):
        """This function is in charge of allowing or not, the
        selection of an item in the traceTreeview. This Treeview
        contains 'ImportedTrace' and 'Session', but we don't want the
        user to select two different kind of data."""

        # We allow the user to unselect an item.
        if is_path_selected:
            return True

        # This set permits to know if there is more than one type of
        # data selected.
        isRowATrace = set()

        isRowATrace.add(model[path].get_parent() is None)

        (model, selectedPaths) = selection.get_selected_rows()
        for path in selectedPaths:
            isRowATrace.add(model[path].get_parent() is None)

        # If 'isRowATrace' set contains two items, it means that user
        # wants to select one ImportedTrace and one Session at the
        # same time. We can't. Really.
        if len(isRowATrace) == 2:
            return False

        # Selected item type is kept, to avoid this whole check each
        # time.
        self.traceSelectionIsATrace = isRowATrace.pop()

        return True

    def traceTreeviewSelection_changed_cb(self, selection):
        model, paths = selection.get_selected_rows()

        if len(paths) > 0:
            # Save name, if it was updated
            if self.nameUpdated:
                self.currentTrace.name = self.view.traceNameEntry.get_text()
                self.nameUpdated = False

            # Save description, if it was updated
            if self.descriptionUpdated:
                self.currentTrace.description = self.view.traceDescriptionEntry.get_text()
                self.descriptionUpdated = False

            if len(paths) == 1:
                # If only one item is selected, update the 'Trace
                # Properties' box.

                row = model[paths[0]]
                parentRow = row.get_parent()

                if parentRow is None:
                    traceId = row[0]
                    trace = self.workspace.getImportedTrace(traceId)
                    sessionFilter = None

                else:
                    traceId = parentRow[0]
                    trace = self.workspace.getImportedTrace(traceId)
                    sessionFilter = trace.getSession(row[0])

                self.view.traceDeleteAction.set_sensitive(True)
                self._refreshProjectProperties(trace, session=sessionFilter)
                self.currentTrace = trace
                self.view.traceNameCellrenderertext.set_property('editable', True)

            else:
                # Else, we can't display nor edit anything.
                self._resetCurrentTrace()
                self.view.traceNameCellrenderertext.set_property('editable', False)

                if self.traceSelectionIsATrace:
                    self.view.traceMergeAction.set_sensitive(True)
                else:
                    self.view.traceMergeAction.set_sensitive(False)

        else:
            self.view.traceDeleteAction.set_sensitive(False)
            self.view.traceNameEntry.set_sensitive(False)
            self.view.traceDescriptionEntry.set_sensitive(False)
            self.view.traceMergeAction.set_sensitive(False)
            self._resetCurrentTrace()

    def messageListSelection_changed_cb(self, selection):
        model, paths = selection.get_selected_rows()

        if len(paths) > 0:
            self.view.messageDeleteAction.set_sensitive(True)

        else:
            self.view.messageDeleteAction.set_sensitive(False)

    def traceDeleteAction_activate_cb(self, button):
        """This callback is called when user clicks on the 'Remove
        Selected Traces' button. A warning dialog is displayed before
        deleting the traces."""

        selection = self.view.traceTreeview.get_selection()
        model, paths = selection.get_selected_rows()

        # UI prevents to select more than one type of item in the left
        # treeview. We just have to check the first item.
        if model[paths[0]].get_parent() is None:
            result = self.view.showTraceDeletionConfirmDialog()

            removedTraces = []

            if result == Gtk.ResponseType.YES:
                for treeiter in paths:
                    traceId = model[treeiter][0]
                    trace = self.workspace.getImportedTrace(traceId)
                    removedTraces.append(traceId)

                    self.log.info("You asked to remove trace {0} (id={1}).".format(trace.name, traceId))
                    self.workspace.removeImportedTrace(trace)

                self._refreshProjectProperties()
                selection.unselect_all()
                self._refreshTraceList(removedTraces=removedTraces)

        # Selected item is a session
        else:
            sessionsToDelete = []
            sessionsNames = []
            for path in paths:
                trace = self.workspace.getImportedTrace(model[path].get_parent()[0])
                session = trace.getSession(model[path][0])
                sessionsNames.append(session)
                sessionsToDelete.extend([(trace, session)])

            result = self.view.showSessionDeletionConfirmDialog(sessionsNames)

            if result == Gtk.ResponseType.YES:
                updatedTraces = []

                for (trace, session) in sessionsToDelete:
                    self.log.info("You asked to remove session {0} (id={1}) from trace {2}.".format(session.name, session.id, trace.name))
                    trace.removeSession(session)
                    updatedTraces.append(trace.id)

                self.workspace.saveConfigFile(overrideTraces=updatedTraces)
                self._refreshProjectProperties()
                self._refreshTraceList(updatedTraces)
                selection.unselect_all()

    def _resetCurrentTrace(self):
        """Unset the currently selected trace and update variables
        related to it."""

        self.currentTrace = None
        self.nameUpdated = False
        self.descriptionUpdated = False

        self._refreshProjectProperties()

    def _refreshProjectProperties(self, trace=None, session=None):
        """This method allows to refresh the project properties
        panel. This code is in charge of enabling or disabling entries
        used for name and description.

        If trace is None, this means that there is no currently
        selected trace (which was removed or something).

        If sessionFilter is not None, it means that only a specific
        session should be displayed.

        :param trace: the currently selected trace (of type
        ImportedTrace)
        :param session: the currently selected session (of type
        Session)"""

        model = self.view.currentTraceMessageListstore
        model.clear()

        if trace is None:
            sensitivity = False
            name = ""
            description = ""
            date = ""
            dataType = ""

        else:
            sensitivity = True
            name = trace.name
            description = trace.description
            date = trace.date.strftime("%c")
            dataType = trace.type

            # If a session filter was given asked, we only show the
            # messages related to that session. Else, we display all
            # messages.
            if session is not None:
                messageList = session.getMessages()
            else:
                messageList = trace.getMessages()

            for message in messageList:
                if message.session is not None:
                    sessionName = message.session.name
                    sessionSortKey = "{0};{1}".format(message.session.id,
                                                      message.session.messages.index(message))
                else:
                    sessionName = ""
                    sessionSortKey = ""

                model.append([message.id,
                              message.timestamp,
                              message.type,
                              message.getStringData(),
                              sessionName,
                              sessionSortKey])

        # Name
        self.view.traceNameEntry.set_sensitive(sensitivity)
        self.view.traceNameEntry.set_text(name)
        self.nameUpdated = False

        # Description
        self.view.traceDescriptionEntry.set_sensitive(sensitivity)
        self.view.traceDescriptionEntry.set_text(description)
        self.descriptionUpdated = False

        # Date
        self.view.traceImportDate.set_sensitive(sensitivity)
        self.view.traceImportDate.set_sensitive(sensitivity)
        self.view.traceImportDate.set_text(date)

        # Data type
        self.view.traceDataType.set_sensitive(sensitivity)
        self.view.traceDataType.set_text(dataType)

        # Message list
        self.view.messageListTreeview.set_sensitive(sensitivity)

    def traceTreeview_button_press_event_cb(self, treeView, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            selection = treeView.get_selection()
            (model, selected_paths) = selection.get_selected_rows()

            try:
                # Select the row on which user clicked
                (selectedPath, selectedColumn, x, y) = treeView.get_path_at_pos(event.x, event.y)
                if selectedPath not in selected_paths:
                    selection.unselect_all()
                    selection.select_path(selectedPath)

                self.view.traceListPopup.popup(None, None, None, None, event.button, event.time)
                return True

            except:
                return False

    def traceNameCellrenderertext_edited_cb(self, cell, path, value):
        """This callbacks allows to change the name of a trace or the
        name of a session."""

        if len(value) == 0:
            self.view.showNameErrorWarningDialog()
            self.nameUpdated = False
            return False

        # If the selected row doesn't has a parent, we have to update
        # the ImportedTrace name. Else, we have to update the session
        # name.

        row = self.view.traceTreestore[path]
        if row.get_parent() is not None:
            session = self.currentTrace.getSession(row[0])
            session.name = value
            self.view.traceTreestore[path][1] = value
            self.log.info("Updated session name (id={0}) from {1} to {2}".format(session.id, session.name, value))
            self.workspace.saveConfigFile(overrideTraces=[self.currentTrace.id])

        else:
            self._changeCurrentTraceName(value, path)

    def traceNameEntry_changed_cb(self, text):
        self.nameUpdated = True

    def traceNameEntry_focus_out_event_cb(self, entry, data):
        if self.nameUpdated:
            self.nameUpdated = False

            newName = entry.get_text()
            if len(newName) == 0:
                self.view.showNameErrorWarningDialog()
                self.view.traceNameEntry.grab_focus()
                self.nameUpdated = True
                return

            model, paths = self.view.traceTreeviewSelection.get_selected_rows()

            assert len(paths) == 1
            self._changeCurrentTraceName(newName, paths[0])

    def traceDescriptionEntry_changed_cb(self, text):
        if len(text.get_text()) > 0:
            self.descriptionUpdated = True

    def traceDescriptionEntry_focus_out_event_cb(self, entry, data):
        if self.descriptionUpdated:
            self.descriptionUpdated = False

            model, treeiter = self.view.traceTreeviewSelection.get_selected_rows()
            if treeiter is not None:
                newDescription = entry.get_text()
                self.currentTrace.description = newDescription

    def _changeCurrentTraceName(self, newName, path):
        """This method allows to change the name of the currently
        selected trace, to update the left panel, etc."""

        trace = self.currentTrace

        self.log.info("Updating trace (id={0}) from {1} to {2}".format(trace.id, trace.name, newName))

        trace.name = newName
        self.view.traceTreestore[path][1] = newName
        self.view.traceNameEntry.set_text(newName)

        self.nameUpdated = False

    def traceMergeAction_activate_cb(self, button):
        response = self.view.showMergeTracesDialog()

        if response == 1:
            self.log.info("Asked to clone traces")

            model, paths = self.view.traceTreeview.get_selection().get_selected_rows()

            traceIds = []
            for treeiter in paths:
                traceIds.append(model[treeiter][0])

            newName = self.view.mergeDialogNameEntry.get_text()
            newTrace = self.workspace.mergeImportedTraces(traceIds, name=newName, keep=self.mergeKeepCopy)

            if self.mergeKeepCopy:
                updatedTraces = traceIds
                removedTraces = []
            else:
                updatedTraces = []
                removedTraces = traceIds
            updatedTraces.append(newTrace.id)

            self.view.traceTreeview.get_selection().unselect_all()
            self._refreshTraceList(traceIds, removedTraces=removedTraces)

    def mergeDialogNameEntry_changed_cb(self, entry):
        if len(entry.get_text()) > 0:
            self.view.mergeDialogValidate.set_sensitive(True)
        else:
            self.view.mergeDialogValidate.set_sensitive(False)

    def mergeDialogCreateCopyCheckbox_toggled_cb(self, toggle):
        if toggle.get_active():
            self.mergeKeepCopy = True
        else:
            self.mergeKeepCopy = False

    def messageListTreeview_button_press_event_cb(self, treeView, event):
        """This code is in charge of enabling the popup menu when
        clicking a row of the message list view."""

        if event.type == Gdk.EventType.BUTTON_PRESS:
            # Select the row on which user clicked
            selection = treeView.get_selection()
            (model, selected_paths) = selection.get_selected_rows()
            path = treeView.get_path_at_pos(event.x, event.y)

            if path is None:
                return False

            (selectedPath, selectedColumn, x, y) = path

            if event.button == 3:
                # Select the row on which user clicked
                if selectedPath not in selected_paths:
                    selection.unselect_all()
                    selection.select_path(selectedPath)
                    (model, selected_paths) = selection.get_selected_rows()

                self.view.messageListPopup.popup(None, None, None, None, event.button, event.time)
                return True

    def messageDeleteAction_activate_cb(self, button):
        assert self.currentTrace is not None

        selection = self.view.messageListTreeview.get_selection()
        (model, paths) = selection.get_selected_rows()

        result = self.view.showMessageDeletionConfirmDialog()

        if result == Gtk.ResponseType.YES:
            trace = self.currentTrace

            for treeiter in paths:
                messageId = model[treeiter][0]

                self.log.info("You asked to remove message '{0}' from trace '{1}' (id={2}).".format(messageId,
                                                                                                    trace.name,
                                                                                                    trace.id))

                trace.removeMessage(messageId)

            # Lets save the new modified trace. Here we force trace
            # save.
            self.workspace.saveConfigFile(overrideTraces=[trace.id])

            self._refreshTraceList([trace.id])
            self._refreshProjectProperties(trace)
            selection.unselect_all()
