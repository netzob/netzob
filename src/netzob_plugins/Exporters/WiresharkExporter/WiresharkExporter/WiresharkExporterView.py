# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from gettext import gettext as _

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Pango
from pygments.lexers import LuaLexer
from pygments.styles.pastie import PastieStyle as STYLE

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from Constants import SIG_SYMBOL_CHANGED, SIG_SAVE_SCRIPT
from netzob.Common.Plugins.Exporters.AbstractExporterView import AbstractExporterView


class WiresharkExporterView(AbstractExporterView):
    """
    GUI for exporting results in Wireshark LUA script.
    """

    def __init__(self, plugin, controller):
        super(WiresharkExporterView, self).__init__(plugin, controller)
        self.styles = {}

    def getDialog(self):
        return self.dialog

    def buildDialog(self):
        self.styles.clear()
        self.buffer = self.sym_store = None
        self.panel = self.buildPanel()
        self.panel.set_size_request(800, 600)
        self.dialog = Gtk.Dialog(_("Export project as Wireshark dissector"),
                                 flags=0, buttons=None)
        self.dialog.set_transient_for(self.controller.netzob.view.mainWindow)
        self.dialog.vbox.pack_start(self.panel, True, True, 0)
        return self.dialog

    def buildPanel(self):
        h_pan = Gtk.HPaned()
        h_pan.add1(self.buildSymbolTreeview())
        h_pan.add2(self.buildScriptView())
        v_box = Gtk.VBox()
        v_box.pack_start(self.buildToolbar(), False, False, 0)
        v_box.pack_end(h_pan, True, True, 0)
        v_box.set_focus_child(h_pan)
        return v_box

    def buildSymbolTreeview(self):
        self.sym_store = Gtk.TreeStore(str, str, str)
        sym_tv = Gtk.TreeView(self.sym_store)
        sym_tv.connect("cursor-changed", lambda tv: self.controller.getSignalsManager().emitSignal(SIG_SYMBOL_CHANGED, tv))

        rdr = Gtk.CellRendererText()
        col_syms = Gtk.TreeViewColumn(_("Symbols"), rdr, text=1)
        sym_tv.append_column(col_syms)

        sym_tv_scroll = Gtk.ScrolledWindow()
        sym_tv_scroll.set_size_request(150, -1)
        sym_tv_scroll.add(sym_tv)
        return sym_tv_scroll

    def buildScriptView(self):
        sw = Gtk.ScrolledWindow()
        textarea = Gtk.TextView()
        textarea.set_editable(False)
        textarea.modify_font(Pango.FontDescription('monospace'))
        self.buffer = textarea.get_buffer()
        sw.add(textarea)
        return sw

    def buildToolbar(self):
        tb = Gtk.Toolbar()
        save_but = Gtk.ToolButton(Gtk.STOCK_SAVE)
        save_but.connect("clicked", self._onSaveClicked_cb)
        close_but = Gtk.ToolButton(Gtk.STOCK_CLOSE)
        close_but.connect("clicked", self._onCloseClicked_cb)
        tb.insert(save_but, 0)
        tb.insert(close_but, 1)
        return tb

    def updateSymbols(self, syms):
        self.sym_store.clear()
        self.sym_store.append(None, ("-1", "{} [{}]".format(_("Entire project"), len(syms)), "0"))
        for sym in syms:
            self.sym_store.append(None, (str(sym.getID()), "{} [{}]".format(sym.getName(), len(sym.getMessages())), str(sym.field.getScore())))

    def getText(self):
        return self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)

    def clearText(self):
        self.buffer.set_text("")

    def setText(self, txt, with_colors=True):
        self.clearText()
        self.appendText(txt, with_colors)

    def setComment(self, txt, with_colors=True):
        self.clearText()
        self.appendComment(txt, with_colors)

    def appendText(self, txt, with_colors=True):
        if with_colors:
            for token, value in LuaLexer().get_tokens(txt):
                while not STYLE.styles_token(token) and token.parent:
                    token = token.parent
                if token not in self.styles:
                    self.styles[token] = tag = self.buffer.create_tag()
                    style = STYLE.style_for_token(token)
                    if style['bgcolor']:
                        tag.set_property('background', '#' + style['bgcolor'])
                    if style['color']:
                        tag.set_property('foreground', '#' + style['color'])
                    if style['bold']:
                        tag.set_property('weight', Pango.Weight.BOLD)
                    if style['italic']:
                        tag.set_property('style', Pango.Style.ITALIC)
                    if style['underline']:
                        tag.set_property('underline', Pango.Underline.SINGLE)
                start = self.buffer.get_end_iter()
                self.buffer.insert_with_tags(start, value, self.styles[token])
        else:
            self.buffer.insert(self.buffer.get_end_iter(), txt)

    def appendComment(self, txt, with_colors=True):
        for line in str(txt).split('\n'):
            self.appendText("-- {}\n".format(line), with_colors)

    ##########
    # Events #
    ##########
    def _onSaveClicked_cb(self, tb):
        chooser = Gtk.FileChooserDialog(_("Export as Wireshark script (LUA)"),
                                        action=Gtk.FileChooserAction.SAVE,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                 Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        chooser.set_current_name("wireshark.lua")
        chooser.set_do_overwrite_confirmation(True)
        if Gtk.ResponseType.ACCEPT == chooser.run():
            fname = chooser.get_filename()
            self.controller.getSignalsManager().emitSignal(SIG_SAVE_SCRIPT, fname, self.getText())
        chooser.destroy()

    def _onCloseClicked_cb(self, tb):
        self.dialog.destroy()
