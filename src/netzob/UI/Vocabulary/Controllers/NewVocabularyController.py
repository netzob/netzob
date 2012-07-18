from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from netzob.UI.Vocabulary.Views.NewVocabularyView import NewVocabularyView

class NewVocabularyController(object):

    def __init__(self, netzob=None):
        self._view = NewVocabularyView(self)

    @property
    def view(self):
        return self._view

    def button_selectAllSymbol_cb(self, widget):
        """Selects all the symbol in the symbol list"""
        model = self.builder.get_object("liststore1")
        #todo a continuer
        for s in model:
            s[0] = True

    def button_unSelectAllSymbol_cb(self, widget):
        """Unselect all the symbol in the symbol list"""
        model = self.builder.get_object("liststore1")
        #todo a continuer
        for s in model:
            s[0] = False

    def button_createSymbol_cb(self, widget):
        builder2 = Gtk.Builder()
        builder2.add_from_file(self.ressourceglade + "/ui/dialogbox.glade")
        createsymbol = self.builder.get_object("createsymbol")
        createsymbol.run()

