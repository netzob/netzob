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
from operator import methodcaller
import re
import struct

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from CodeBuffer import LUACodeBuffer
from Constants import SIG_SYMBOL_CHANGED, SIG_SAVE_SCRIPT
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage
from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from netzob.Common.SignalsManager import SignalsManager
from netzob.UI.NetzobWidgets import NetzobErrorMessage, NetzobWarningMessage
from WiresharkExporterError import WiresharkExporterError
from WiresharkExporterView import WiresharkExporterView
from WiresharkFilter import WiresharkFilterFactory


class WiresharkExporterController(AbstractExporterController):
    """
    Controller of Wireshark export plugin.
    """
    def __init__(self, netzob, plugin):
        view = WiresharkExporterView(plugin, self)
        super(WiresharkExporterController, self).__init__(netzob, plugin, view)

        # Intialize signals manager
        self.signalsManager = SignalsManager()

        # Attach events
        self.signalsManager.attach(self._onSymbolChanged_cb, (SIG_SYMBOL_CHANGED,))
        self.signalsManager.attach(self._onSaveScript_cb, (SIG_SAVE_SCRIPT,))

    def getMessageContext(self, msg):
        def clean(s):
            # Respect wireshark syntax.
            # Allowed are lower characters, digits, '-', '_' and '.'
            return re.sub("[^a-z\-_\.]", "_", str(s).lower())
        sym = msg.getSymbol()
        proto_name = clean(sym.getName())
        proto_keyname = proto_name.upper()
        proto_desc = "{} Protocol".format(proto_name.capitalize())
        class_var = "proto_{}".format(msg.getID().replace('-', '_'))
        if isinstance(msg, L4NetworkMessage):
            filter_name = msg.getL4Protocol()
        elif isinstance(msg, L3NetworkMessage):
            filter_name = msg.getL3Protocol()
        elif isinstance(msg, L2NetworkMessage):
            filter_name = msg.getL2Protocol()
        else:
            raise WiresharkExporterError("Cannot find a compatible protocol for {}.".format(msg))

        del sym

        return locals()

    def __writeDynSizeBlock(self, buf, field, sorted_ivalues):
        with buf.new_block("do"):
            buf << "local values = {{{}}}"\
                .format(", ".join('"{}"'.format(val) for val in sorted_ivalues))
            with buf.new_block("for k,v in next,values,nil do"):
                buf << "local vlen = v:len() / 2"
                with buf.new_block("if buffer(idx):len() >= vlen and tostring(ByteArray.new(v)) == tostring(buffer(idx,vlen):bytes()) then"):
                    buf << 'subtree:add(buffer(idx,vlen), "{prefix}: " .. v)'\
                        .format(prefix=field.getName())
                    buf << "idx = idx + vlen"
                    buf << "break"

    def __writeUniqueSizeBlock(self, buf, field, values):
        j = min(map(len, values))
        with buf.new_block("if buffer(idx):len() >= {} then".format(j)):
            buf << 'subtree:add(buffer(idx,{length}), "{prefix}: " .. buffer(idx,{length}))'\
                .format(length=j, prefix=field.getName())
            buf << "idx = idx + {}".format(j)

    def generateSymbolDissector(self, sym):
        msgs = sym.getMessages()
        ctx = self.getMessageContext(msgs[0])
        buf = LUACodeBuffer()
        buf << "--\n-- Symbol {proto_keyname}\n--\n".format(**ctx)
        buf << """{class_var} = Proto("{proto_name}", "{proto_name} Protocol")
function {class_var}.dissector(buffer, pinfo, tree)
  pinfo.cols.protocol = "{proto_keyname}"
  local subtree = tree:add({class_var}, buffer(), "{proto_desc}")
  local idx = 0
""".format(**ctx)

        fields = sym.getExtendedFields()
        splittedData = [msg.getSplittedData(fields, msg.data) for msg in msgs]
        with buf.new_block():
            for field, ivalues in zip(fields, zip(*splittedData)):
                sorted_ivalues = sorted(set(str(v) for v in ivalues if v), key=len, reverse=True)
                values = map(methodcaller('decode', 'hex'), ivalues)

                if len(set(map(len, values))) > 1:
                    self.__writeDynSizeBlock(buf, field, sorted_ivalues)
                else:
                    self.__writeUniqueSizeBlock(buf, field, values)
                # TODO: re-implement this...
                ## with buf.new_block():
                ##     buf_type = _getLuaTvbType(field)
                ##     if buf_type is not None:
                ##         buf << ':{}()'.format(buf_type))
                ##     buf << ')'

        # Register dissector function to specific filter criterion
        filter_ = WiresharkFilterFactory.getFilter(sym)
        luatype = _getLuaTableType(filter_.pytype)
        for expr in filter_.getExpressions():
            buf << """if not pcall(DissectorTable.get, "{0}") then
  DissectorTable.new("{0}", "Netzob-generated table", {type})
end
DissectorTable.get("{0}"):add({1}, {class_var})
""".format(*expr, type=luatype, **ctx)

        return buf.getvalue()

    def run(self):
        data = []
        proj = self.netzob.getCurrentProject()

        if not proj:
            NetzobErrorMessage(_("No project selected."), parent=self.netzob.view.mainWindow)
            return

        syms = proj.getVocabulary().getSymbols()
        dial = self.view.buildDialog()
        self.view.updateSymbols(syms)
        dial.show_all()

    def __call__(self):
        self.run()

    def getSignalsManager(self):
        """returns the signals manager"""
        return self.signalsManager

    ##########
    # Events #
    ##########
    def _onSymbolChanged_cb(self, sig, tv):
        sel = tv.get_selection()

        if not sel:
            return  # on closing, event occurs

        tm, it = sel.get_selected()
        sym_id = tm.get_value(it, 0)
        voca = self.netzob.getCurrentProject().getVocabulary()

        sym = voca.getSymbol(sym_id)
        if sym is None:
            self.view.clearText()
            for sym in voca.getSymbols():
                try:
                    self.view.appendText(self.generateSymbolDissector(sym))
                except WiresharkExporterError, wee:
                    self.view.appendComment(wee)
                    NetzobWarningMessage("[{}] {}".format(sym.getName(), wee), self.view.dialog)
        else:
            try:
                self.view.setText(self.generateSymbolDissector(sym))
            except WiresharkExporterError, wee:
                self.view.setComment(wee)
                NetzobErrorMessage("[{}] {}".format(sym.getName(), wee), self.view.dialog)

    def _onSaveScript_cb(self, sig, fname, value):
        with open(fname, 'w') as f:
            f.write(value)


def _getLuaTableType(pytype):
    if issubclass(pytype, (int, long)):
        return 'ftypes.UINT32'
    if issubclass(pytype, basestring):
        return 'ftypes.STRING'
    raise ValueError("Cannot match LUA type for {!s}".format(pytype))


# TODO: re-implement this...
## def _getLuaTvbType(field):
##     fmt = field.getFormat()
##     typ = None
##     if fmt in ['string', 'ipv4']:
##         typ = fmt
##     if 'decimal' == fmt:
##         typ = 'uint'
## # XXX: bug in lua
## #    if 'binary' == fmt: typ = 'bytes'
##     if 'little-endian' == field.getEndianess() and typ:
##         typ = 'le_{}'.format(typ)
##     return typ
