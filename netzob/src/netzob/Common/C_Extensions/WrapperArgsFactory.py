# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
from netzob.Common.C_Extensions.WrapperMessage import WrapperMessage
from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
from netzob.Common.NetzobException import NetzobException
# from netzob import _libScoreComputation  # type: ignore


class WrapperArgsFactory(object):
    """Factory dedicated to the manipulation of arguments passed to C wrapper.
    This object will be transfered to the C extensions with its attributes which are:
    - self.typeList : a map between function name and function pointer
    - self.function : the function for which the parameters will be wrapped.
    """

    def __init__(self, function):
        self.typeList = {
            "_libScoreComputation.computeSimilarityMatrix":
            self.computeSimilarityMatrix,
            "_libNeedleman.alignMessages":
            self.alignMessages
        }

        if (function in list(self.typeList.keys())):
            self.function = function
        else:
            raise NetzobException("Function " + str(function) +
                                  " not implemented")

    def __str__(self):
        return str(self.args)

    def computeSimilarityMatrix(self, symbols):
        self.args = []
        for s in symbols:
            self.args.append(WrapperMessage(s.messages[0], str(id(s))))

    def alignMessages(self, values):
        self.args = []
        for (data, tags) in values:
            message = RawMessage(data=data)
            for pos, tag in list(tags.items()):
                message.addSemanticTag(pos, tag)
            self.args.append(WrapperMessage(message, "Virtual symbol"))
