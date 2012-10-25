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
import re
import struct

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Models.L4NetworkMessage import L4NetworkMessage
from netzob.Common.Models.L3NetworkMessage import L3NetworkMessage
from netzob.Common.Models.L2NetworkMessage import L2NetworkMessage
from netzob.Common.Plugins.Exporters.AbstractExporterController import AbstractExporterController
from netzob.UI.NetzobWidgets import NetzobErrorMessage, NetzobWarningMessage
from CodeBuffer import CodeBuffer
from WiresharkExporterError import WiresharkExporterError
from WiresharkExporterView import WiresharkExporterView
from WiresharkFilter import WiresharkFilterFactory


class WiresharkExporterController(AbstractExporterController):
    """
    Controller of Wireshark export plugin.
    """
    def __init__(self, netzob, plugin):
        view = WiresharkExporterView(plugin, self)
        view.subscribe_signal('SymbolChanged', self._onSymbolChanged_cb)
        super(WiresharkExporterController, self).__init__(netzob, plugin, view)

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
            raise ValueError("Cannot find a compatible protocol for {}.".format(msg))

        del sym

        return locals()

    def generateSymbolDissector(self, sym):
        msg_ref = sym.getMessages()[0]
        ctx = self.getMessageContext(msg_ref)
        buf = CodeBuffer()
        buf.write("--\n-- Symbol {proto_keyname}\n--\n".format(**ctx))
        buf.write("""{class_var} = Proto("{proto_name}", "{proto_name} Protocol")
function {class_var}.dissector(buffer, pinfo, tree)
  pinfo.cols.protocol = "{proto_keyname}"
  local subtree = tree:add({class_var}, buffer(), "{proto_desc}")
""".format(**ctx))
        i = 0

        # XXX: do not use msg_ref here, not valid for all msgs
        fields = sym.getExtendedFields()
        splittedData = msg_ref.getSplittedData(fields, msg_ref.data)
        for field, ivalue in zip(fields, splittedData):
            value = ivalue.decode('hex')
            fmt = field.getFormat()

            # raise an error when a non-trailing dynamic regex is encountered
            if field.isRegexOnlyDynamic() and field.getIndex() < len(fields) - 1:
                raise WiresharkExporterError(_("Cannot handle dynamic-size fields"))

            with buf:
                buf.write('if buffer({start}):len() > 0 then\n'.format(start=i))
                j = len(value)
                with buf:
                    if field.isRegexOnlyDynamic():
                        buf.write('subtree:add(buffer({start}), "{prefix}: " .. buffer({start})'
                                  .format(start=i, prefix=field.getName()))
                    else:
                        buf.write('subtree:add(buffer({start},{length}), "{prefix}: " .. buffer({start},{length})'
                                  .format(start=i, length=j, prefix=field.getName()))
                    buf_type = _getLuaTvbType(field)
                    if buf_type is not None:
                        buf.write(':{}()'.format(buf_type))
                    buf.write(')\n')
            buf.write('end\n')
            i += j
        buf.write("end\n")  # end of dissector function

        # Register dissector function to specific filter criterion
        filter_ = WiresharkFilterFactory.getFilter(sym)
        luatype = _getLuaTableType(filter_.pytype)
        for expr in filter_.getExpressions():
            buf.write("""if not pcall(DissectorTable.get, "{0}") then
  DissectorTable.new("{0}", "Netzob-generated table", {type})
end
DissectorTable.get("{0}"):add({1}, {class_var})
""".format(*expr, type=luatype, **ctx))

        return buf.getvalue()

    def run(self):
        data = []
        proj = self.netzob.getCurrentProject()

        if not proj:
            NetzobErrorMessage(_("No project selected."))
            return

        syms = proj.getVocabulary().getSymbols()
        dial = self.view.buildDialog()
        self.view.updateSymbols(syms)
        dial.show_all()

    def __call__(self):
        self.run()

    ##########
    # Events #
    ##########
    def _onSymbolChanged_cb(self, tv):
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
                    self.view.appendText("-- {}\n".format(wee))
                    NetzobWarningMessage("[{}] {}".format(sym.getName(), wee))
        else:
            try:
                self.view.setText(self.generateSymbolDissector(sym))
            except WiresharkExporterError, wee:
                NetzobErrorMessage("[{}] {}".format(sym.getName(), wee))


def _getLuaTableType(pytype):
    if issubclass(pytype, (int, long)):
        return 'ftypes.UINT32'
    if issubclass(pytype, basestring):
        return 'ftypes.STRING'
    raise ValueError("Cannot match LUA type for {!s}".format(pytype))


def _getLuaTvbType(field):
    fmt = field.getFormat()
    typ = None
    if fmt in ['string', 'ipv4']:
        typ = fmt
    if 'decimal' == fmt:
        typ = 'uint'
# XXX: bug in lua
#    if 'binary' == fmt: typ = 'bytes'
    if 'little-endian' == field.getEndianess() and typ:
        typ = 'le_{}'.format(typ)
    return typ
