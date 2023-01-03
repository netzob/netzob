# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2012 AMOSSYS                                                |
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
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Messages.L2NetworkMessage import L2NetworkMessage
from netzob.Model.Vocabulary.Messages.L3NetworkMessage import L3NetworkMessage
from netzob.Model.Vocabulary.Messages.L4NetworkMessage import L4NetworkMessage


class WiresharkFilterFactory(object):
    @staticmethod
    def getFilter(sym):
        msg_ref = sym.messages[0]
        if isinstance(msg_ref, L4NetworkMessage):
            klass = WiresharkL4Filter
        elif isinstance(msg_ref, L3NetworkMessage):
            klass = WiresharkL3Filter
        elif isinstance(msg_ref, L2NetworkMessage):
            klass = WiresharkL2Filter
        else:
            raise ValueError("Unable to build filter for {!r}.".format(sym))
        return klass(sym)


class WiresharkFilter(object):
    def __init__(self, sym):
        self.sym = sym
        self.msg_ref = sym.messages[0]
        self.pytype = None

    def iterExpressions(self):
        raise NotImplementedError

    def getExpressions(self):
        return set(self.iterExpressions())


class WiresharkL4Filter(WiresharkFilter):
    def __init__(self, sym):
        super(WiresharkL4Filter, self).__init__(sym)
        self.proto = self.msg_ref.l4Protocol
        self.pytype = int

    def iterExpressions(self):
        for msg in self.sym.messages:
            for port in [msg.l4SourceAddress, msg.l4DestinationAddress]:
                yield ("{}.port".format(self.proto.lower()), int(port))


class WiresharkL3Filter(WiresharkFilter):
    def __init__(self, sym):
        super(WiresharkL3Filter, self).__init__(sym)
        self.proto = self.msg_ref.l3Protocol
        self.pytype = str

    def iterExpressions(self):
        for msg in self.sym.messages:
            for addr in [msg.l3SourceAddress, msg.l3DestinationAddress]:
                yield ("{}.addr".format(self.proto.lower()), '"{}"'.format(addr))


class WiresharkL2Filter(WiresharkFilter):
    def __init__(self, sym):
        super(WiresharkL2Filter, self).__init__(sym)
        self.proto = self.msg_ref.l2Protocol
        self.pytype = str

    def iterExpressions(self):
        for msg in self.sym.messages:
            for addr in [msg.l2SourceAddress, msg.l2DestinationAddress]:
                yield ("{}.addr".format("eth"), '"{}"'.format(addr))
