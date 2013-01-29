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
from gi.repository import Gtk, Gdk
import logging
import os

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.NetzobAbstractPerspectiveView import NetzobAbstractPerspectiveView


class TraceManagerView(NetzobAbstractPerspectiveView):

    def __init__(self, controller):
        gladeFile = os.path.join("traceManager", "traceManagerView.glade")
        menubar = os.path.join("traceManager", "traceManagerMenuToolbar.ui")
        popupFile = os.path.join("traceManager", "popupMenu.ui")

        super(TraceManagerView, self).__init__(controller,
                                               gladeFile,
                                               root="TraceManagerView",
                                               uiMenuBar=menubar,
                                               actionGroup="actionGroup")

        self._getObjects(["traceTreeview",
                          "traceTreestore",
                          "messageListTreeview",
                          "traceNameCellrenderertext",
                          "traceTreeviewSelection",
                          "traceSessionNewAction",
                          "traceDeleteAction",
                          "traceNameEntry",
                          "traceDescriptionEntry",
                          "traceImportDate",
                          "traceDataType",
                          "currentTraceMessageListstore",
                          "traceMergeAction",
                          "traceImportInProjectAction",

                          "currentTraceMessageListstore",
                          "messageListTreeview",
                          "messageDeleteAction",

                          # Merge dialog
                          "mergeDialogValidate",
                          "mergeDialogCreateCopyCheckbox",
                          "mergeDialogNameEntry",

                          # Import in project dialog
                          "importInProjectNameEntry",
                          "importInProjectKeepDuplicatesCheckbox",
                          "importInProjectKeepPropsCheckbox",
                          "importInProjectDialogValidate",
                          ])

        self.traceTreeviewSelection.set_select_function(self.controller.traceTreeviewSelection_select_function_cb,
                                                        self.traceTreestore)

        self.uiManager = Gtk.UIManager()
        self.uiManager.insert_action_group(self.actionGroup)
        self.uiManager.add_ui_from_file(self._findUiResource(popupFile))

        # Getting popup for the Trace List
        self.traceListPopup = self.uiManager.get_widget("/TraceListPopupMenu")

        # Getting popup for the Message List
        self.messageListPopup = self.uiManager.get_widget("/MessageListPopupMenu")

        # Configuring Drag&Drop
        self.messageListTreeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                                          [],
                                                          Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        self.messageListTreeview.drag_source_add_text_targets()

        self.traceTreeview.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.traceTreeview.enable_model_drag_dest([],
                                                  Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
        self.traceTreeview.drag_dest_add_text_targets()

    def showTraceDeletionConfirmDialog(self):
        """A warning dialog is displayed before deleting the traces."""

        dlg = Gtk.MessageDialog(self.controller.mainController.view.mainWindow,
                                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                Gtk.MessageType.WARNING,
                                Gtk.ButtonsType.NONE,
                                _("Are you sure you want to delete the selected traces?"))
        dlg.format_secondary_text(_("If you confirm, the selected traces will be permanently lost."))

        dlg.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dlg.add_button(_("Delete Traces"), Gtk.ResponseType.YES)
        dlg.set_default_response(Gtk.ResponseType.YES)

        result = dlg.run()
        dlg.destroy()

        return result

    def showSessionDeletionConfirmDialog(self, sessionNames):
        """A warning dialog is displayed before deleting the
        sessions.

        :param sessionNames: list of the session names."""

        dlg = Gtk.MessageDialog(self.controller.mainController.view.mainWindow,
                                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                Gtk.MessageType.WARNING,
                                Gtk.ButtonsType.NONE,
                                _("Are you sure you want to delete selected sessions and all the messages it contains?"))

        sessions = ", ".join(map(lambda s: "\"{0}\"".format(s.name), sessionNames))

        text = _("If you confirm, session {0} and associated messages will be permanently lost.".format(sessions))
        dlg.format_secondary_text(text)

        dlg.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dlg.add_button(_("Delete Session"), Gtk.ResponseType.YES)
        dlg.set_default_response(Gtk.ResponseType.YES)

        result = dlg.run()
        dlg.destroy()

        return result

    def showMessageDeletionConfirmDialog(self):
        """A warning dialog is displayed before deleting the
        messages."""

        dlg = Gtk.MessageDialog(self.controller.mainController.view.mainWindow,
                                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                Gtk.MessageType.WARNING,
                                Gtk.ButtonsType.NONE,
                                _("Are you sure you want to delete the selected messages?"))
        dlg.format_secondary_text(_("If you confirm, the selected messages will be permanently lost."))

        dlg.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dlg.add_button(_("Delete Messages"), Gtk.ResponseType.YES)

    def showNameErrorWarningDialog(self):
        dlg = Gtk.MessageDialog(self.controller.mainController.view.mainWindow,
                                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.OK,
                                _("You can't change the trace name to an empty one"))
        dlg.format_secondary_text(_("Please update the name of your trace set."))

        result = dlg.run()
        dlg.destroy()

    def showMergeTracesDialog(self):
        dlg = self.builder.get_object("mergeTracesDialog")
        dlg.set_transient_for(self.controller.mainController.view.mainWindow)

        self.mergeDialogNameEntry.set_text("")
        self.mergeDialogCreateCopyCheckbox.set_active(True)

        result = dlg.run()
        dlg.hide()

        return result

    def showImportInProjectDialog(self):
        dlg = self.builder.get_object("importInProjectDialog")
        dlg.set_transient_for(self.controller.mainController.view.mainWindow)

        self.importInProjectNameEntry.set_text("")
        self.importInProjectKeepDuplicatesCheckbox.set_active(True)
        self.importInProjectKeepPropsCheckbox.set_active(True)

        result = dlg.run()
        dlg.hide()

        return result

    def showErrorMessage(self, errorMessage, secondaryMessage=None):
        dlg = Gtk.MessageDialog(self.controller.mainController.view.mainWindow,
                                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.OK,
                                errorMessage)

        if secondaryMessage is not None:
            dlg.format_secondary_text(secondaryMessage)

        result = dlg.run()
        dlg.destroy()
