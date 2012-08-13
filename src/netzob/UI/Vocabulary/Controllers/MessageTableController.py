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
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.MessageTableView import MessageTableView


class MessageTableController(object):

    def __init__(self, vocabularyPerspective):
        self.vocabularyPerspective = vocabularyPerspective
        self._view = MessageTableView(self)
        self.selectedMessage = None

    @property
    def view(self):
        return self._view

    def getSelectedMessage(self):
        return self.selectedMessage

    def messageTableTreeView_changed_event_cb(self, selection):
        """Callback executed when the user
        clicks on a message in the MessageTable"""
        if selection is not None:
            (model, rows) = selection.get_selected_rows()
            if rows is not None and len(rows) > 0:
                iter = rows[0]
                msgID = model[iter][0]
                if msgID is not None:
                    self.selectedMessage = self.vocabularyPerspective.getCurrentProject().getVocabulary().getMessageByID(msgID)
                    self.vocabularyPerspective.updateMessageProperties()
                    return
        self.selectedMessage = None
        self.vocabularyPerspective.updateMessageProperties()

    def messageListBox_button_press_event_cb(self, box, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)

    def closeButton_clicked_cb(self, button):
        self.vocabularyPerspective.removeMessageTable(self.view)

    def messageTableTreeView_button_press_event_cb(self, treeView, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)

    def messageTableTreeView_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def messageTableTreeView_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)

    def messageTableBox_enter_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(True)

    def messageTableBox_leave_notify_event_cb(self, treeView, data=None):
        self.view.treeViewHeaderGroup.setAllColumnsFocus(False)
