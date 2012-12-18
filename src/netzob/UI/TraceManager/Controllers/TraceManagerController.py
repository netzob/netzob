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
