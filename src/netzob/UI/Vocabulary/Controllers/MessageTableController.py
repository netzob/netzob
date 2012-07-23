'''
Created on 23 juil. 2012

@author: fabien
'''
from netzob.UI.Vocabulary.Views.MessageTableView import MessageTableView

class MessageTableController(object):

    def __init__(self, vocabularyPerspective):
        self.vocabularyPerspective = vocabularyPerspective
        self._view = MessageTableView(self)

    @property
    def view(self):
        return self._view

    def messageListBox_button_press_event_cb(self, box, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)

    def closeButton_clicked_cb(self, button):
        self.vocabularyPerspective.removeMessageTable(self.view)

    def messageListTreeView_button_press_event_cb(self, treeView, eventButton):
        self.vocabularyPerspective.setSelectedMessageTable(self.view)
