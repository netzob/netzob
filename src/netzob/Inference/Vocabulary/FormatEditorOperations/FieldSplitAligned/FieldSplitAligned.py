
#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.AbstractField import AbstractField
from netzob.Inference.Vocabulary.FormatEditor import FormatEditor
from netzob.Common.C_Extensions.WrapperArgsFactory import WrapperArgsFactory
from netzob import _libNeedleman

@NetzobLogger
class FieldSplitAligned(object):
    """This class align the data attached to a specified field
    and build a field definition based on the result of the alignment.

    The alignement is based on Needleman & Wunsch sequence alignement.
    
    >>> import binascii
    >>> from netzob.all import *
    >>> samples = ["01ff00ff", "022ff0000ff0", "03ff000000ff", "0444ff00000000ff", "05ff0000000000ff", "06ff000000000000ff"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print symbol
              01ff00ff
          022ff0000ff0
          03ff000000ff
      0444ff00000000ff
      05ff0000000000ff
    06ff000000000000ff
    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol)
    >>> #print symbol
    
    
    """

    def __init__(self, doInternalSlick=False):
        """Constructor.

        """
        self.doInternalSlick = doInternalSlick


    @typeCheck(AbstractField)
    def execute(self, field):
        """Execute the alignement on the specified field.

        :parameter field: the field that will be aligned
        :type field: :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        """
        if field is None:
            raise TypeError("Field cannot be None")

        # First step: we clean and reset the field
        FormatEditor.resetFormat(field)

        # Retrieve all the segment of messages to align
        values = field.getValues(encoded=False, styled=False)
    
        if len(values) == 0:
            return

        # Execute the alignement
        (alignment, semanticTags, score) = self._alignData(values)

    @typeCheck(list, list)
    def _alignData(self, values, semanticTags=None):
        """Align the specified data with respect to the semantic tags
        identified over the data.

        :parameter values: values to align
        :type values: a list of hexastring.
        :keyword semanticTags: semantic tags to consider when aligning
        :type semanticTags: a list of :class:`netzob.Common.Models.Vocabulary.SemanticTag.SemanticTag`
        :return: the alignment, its score and the semantic tags
        :rtype: a tupple (alignement, semanticTags, score)
        """
        if values is None or len(values) == 0:
            raise TypeError("At least one value must be provided.")

        for val in values:
            if val is None or not isinstance(val, str):
                raise TypeError("At least one value is None or not an str which is not authorized.")
            
        if semanticTags is None:
            semanticTags = []
            semanticTags = [dict() for v in values]

        if len(semanticTags) != len(values):
            raise TypeError("There should be a list of semantic tags for each value")

        # Prepare the argument to send to the C wrapper
        toSend = [(''.join(values[iValue]), semanticTags[iValue]) for iValue in xrange(len(values))]

        wrapper = WrapperArgsFactory("_libNeedleman.alignMessages")
        wrapper.typeList[wrapper.function](toSend)

        debug = True
        (score1, score2, score3, regex, mask, semanticTags) = _libNeedleman.alignMessages(self.doInternalSlick, self._cb_executionStatus, debug, wrapper)
        scores = (score1, score2, score3)

        self._logger.debug("regex={0}".format(repr(regex)))
        self._logger.debug("mask={0}".format(repr(mask)))
        self._logger.debug("scores={0}".format(scores))

    def _cb_executionStatus(self, stage, donePercent, currentMessage):
        """Callback function called by the C extension to provide
        info on the current status.
        """
        pass            


    @property
    def doInternalSlick(self):
        return self.__doInternalSlick

    @doInternalSlick.setter
    @typeCheck(bool)
    def doInternalSlick(self, doInternalSlick):
        if doInternalSlick is None:
            raise TypeError("doInternalSlick cannot be None")
        self.__doInternalSlick = doInternalSlick
        
