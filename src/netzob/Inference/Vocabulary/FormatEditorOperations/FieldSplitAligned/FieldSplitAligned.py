
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
from netzob.Common.Models.Types.AbstractType import AbstractType
from netzob.Common.Models.Types.TypeConverter import TypeConverter
from netzob.Common.Models.Types.HexaString import HexaString
from netzob.Common.Models.Types.Raw import Raw
from netzob.Common.Models.Types.BitArray import BitArray
from netzob.Common.Models.Vocabulary.Field import Field
from netzob import _libNeedleman


@NetzobLogger
class FieldSplitAligned(object):
    """This class align the data attached to a specified field
    and build a field definition based on the result of the alignment.

    The alignement is based on Needleman & Wunsch sequence alignement.

    >>> import binascii
    >>> from netzob.all import *
    >>> samples = ["01ff00ff", "0222ff0000ff", "03ff000000ff", "0444ff00000000ff", "05ff0000000000ff", "06ff000000000000ff"]
    >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
    >>> symbol = Symbol(messages=messages)
    >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
    >>> print symbol
              01ff00ff
          0222ff0000ff
          03ff000000ff
      0444ff00000000ff
      05ff0000000000ff
    06ff000000000000ff
    >>> fs = FieldSplitAligned()
    >>> fs.execute(symbol)
    >>> #print symbol


    """

    def __init__(self, unitSize=AbstractType.UNITSIZE_8, doInternalSlick=False):
        """Constructor.

        """
        self.doInternalSlick = doInternalSlick
        self.unitSize = unitSize

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

        # Check the results
        if alignment is None:
            raise ValueError("Impossible to compute an alignment for the specifed data")

        # Build Fields based on computed alignement and semantic tags
        self._updateFieldsFromAlignment(field, alignment, semanticTags)

    @typeCheck(AbstractField, str, dict)
    def _updateFieldsFromAlignment(self, field, alignment, semanticTags):
        """This methods creates a regex based on the computed alignment
        by the Needleman&Wunsch algorithm and the attached semantic tags.

        @param field : the field for which it creates the regex (and the sub fields)
        @param align : the string representing the common alignment between messages of the symbol.
        @param semanticTags : the list of tags attached to each half-bytes of the provided alignment."""

        if field is None:
            raise TypeError("Field cannot be None")
        if alignment is None:
            raise TypeError("Alignment cannot be None")
        if semanticTags is None:
            raise TypeError("SemanticTags cannot be None")

        # Create fields following the alignment
        self._splitFieldFollowingAlignment(field, alignment)
        self._logger.debug(field)

    def _splitFieldFollowingAlignment(self, field, align):
        """Update the field definition with new fields following the
        specified align."""

        # STEP 1 : Create a field separation based on static and dynamic fields
        leftAlign, rightAlign = self._splitAlignment(align)
        splited = self._mergeAlign(leftAlign, rightAlign)
        step1Fields = []
        for (entryVal, entryDyn) in splited:
            if entryDyn:
                newField = Field(Raw(nbBytes=(0, len(entryVal) / 2)))
            else:
                newField = Field(Raw(TypeConverter.convert(entryVal, HexaString, Raw)))
            step1Fields.append(newField)
            field.children.append(newField)

        self._logger.debug(splited)

    def _splitAlignment(self, align):
        """Splits the specified alignment which is composed of hexastring and of dynamic sections ("-")
        The idea is to separate in two (left and right) and then to merge the splitted left and the splitted right.

        >>> import random
        >>> fs = FieldSplitAligned()
        >>> data = "-----01987640988765--876--678987--67898-------6789789-87987978----"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['-----', True], ['01987640988765', False], ['--', True], ['876', False], ['--', True], ['678987', False], ['--', True], ['67898', False], ['-------', True], ['6789789', False], ['-', True], ['87987978', False], ['----', True]]
        >>> data = "-------------------------------"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['-------------------------------', True]]
        >>> data = "98754678998765467890875645"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['98754678998765467890875645', False]]
        >>> data = "---------------987-----6789765--568767---568776897689---567876------------------5678657865-9876579867789-9876879-9876787678657865467876546"
        >>> print fs._mergeAlign(*fs._splitAlignment(data))
        [['---------------', True], ['987', False], ['-----', True], ['6789765', False], ['--', True], ['568767', False], ['---', True], ['568776897689', False], ['---', True], ['567876', False], ['------------------', True], ['5678657865', False], ['-', True], ['9876579867789', False], ['-', True], ['9876879', False], ['-', True], ['9876787678657865467876546', False]]
        >>> nbField = random.randint(50000, 200000)
        >>> tab = []
        >>> for i in range(nbField):
        ...     if i%2 == 0:
        ...         tab.append("-"*random.randint(1, 20))
        ...     else:
        ...         tab.append("".join([random.choice('0123456789abcdef') for x in range(random.randint(1, 20))]))
        >>> data = "".join(tab)
        >>> nbField == len(fs._mergeAlign(*fs._splitAlignment(data)))
        True

        """
        if len(align) == 1:
            return ([[align[0], align[0] == "-"]], [])
        elif len(align) == 2:
            return ([[align[0], align[0] == "-"]], [[align[1], align[1] == "-"]])

        indexHalf = len(align) / 2
        leftAlign = align[0:indexHalf]
        rightAlign = align[indexHalf:]

        leftLeftAlign, rightLeftAlign = self._splitAlignment(leftAlign)
        mergedLeftAlign = self._mergeAlign(leftLeftAlign, rightLeftAlign)

        leftRightAlign, rightRightAlign = self._splitAlignment(rightAlign)
        mergedRightAlign = self._mergeAlign(leftRightAlign, rightRightAlign)

        return (mergedLeftAlign, mergedRightAlign)

    def _mergeAlign(self, leftAlign, rightAlign):
        if len(leftAlign) == 0:
            return rightAlign
        if len(rightAlign) == 0:
            return leftAlign
        if leftAlign[-1][1] == rightAlign[0][1]:
            leftAlign[-1][0] = leftAlign[-1][0] + rightAlign[0][0]
            align = leftAlign + rightAlign[1:]
        else:
            align = leftAlign + rightAlign
        return align

    def _temp(self, align):
        self._logger.debug("Align = {0}".format(align))
        for i, val in enumerate(align):

            if (val == "-"):
                if (found is False):
                    start = i
                    found = True
            else:
                if (found is True):
                    found = False
                    nbTiret = i - start
                    self._logger.debug("Add dyn raw : {0}".format(nbTiret / 2))
                    domains.append(Raw(nbBytes=(0, nbTiret / 2)))
                    self._logger.debug("Converting : {0}".format(val))
                    domains.append(Raw(TypeConverter.convert(val, HexaString, Raw)))
                else:
                    if len(domains) == 0:
                        domains.append(Raw(TypeConverter.convert(val, HexaString, Raw)))
                    else:
                        prevVal = TypeConverter.convert(domains[-1].value, BitArray, Raw)
                        domains[-1] += Raw(prevVal + TypeConverter.convert(val, HexaString, Raw))
        if (found is True):
            nbTiret = i - start + 1
            domains.append(Raw(nbBytes=(0, nbTiret)))

        # We have a computed the 'simple' regex,
        # and represent it using the field representation
        step1Fields = []
        for domainElt in domains:
            if domainElt is None:
                pass
            innerField = Field(domain=domainElt)
            step1Fields.append(innerField)
            field.children.append(innerField)

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

        debug = False
        (score1, score2, score3, regex, mask, semanticTags) = _libNeedleman.alignMessages(self.doInternalSlick, self._cb_executionStatus, debug, wrapper)
        scores = (score1, score2, score3)

        # Deserialize returned info
        alignment = self._deserializeAlignment(regex, mask, self.unitSize)
        semanticTags = self._deserializeSemanticTags(semanticTags, self.unitSize)

        return (alignment, semanticTags, scores)

    def _cb_executionStatus(self, stage, donePercent, currentMessage):
        """Callback function called by the C extension to provide
        info on the current status.
        """
        pass

    def _deserializeSemanticTags(self, tags, unitSize=AbstractType.UNITSIZE_8):
        """Deserialize the information returned from the C library
        and build the semantic tags definitions from it.
        """
        result = dict()
        arTags = tags.split(';')
        j = 0
        for iTag, tag in enumerate(arTags):
            result[j] = tag
            if unitSize == AbstractType.UNITSIZE_8:
                j = j + 1
                result[j] = tag
            else:
                raise ValueError("Unsupported unitsize.")
            j += 1
        return result

    def _deserializeAlignment(self, regex, mask, unitSize=AbstractType.UNITSIZE_8):
        """
        deserializeAlignment: Transforms the C extension results
        in a python readable way
        @param regex the C returned regex
        @param mask the C returned mask
        @param unitSize the unitSize
        @returns the python alignment
        """
        if not (unitSize == AbstractType.UNITSIZE_8 or unitSize == AbstractType.UNITSIZE_4):
            raise ValueError("Deserializing with unitSize {0} not yet implemented, only 4 and 8 supported.".format(unitSize))

        align = ""
        for i, c in enumerate(mask):
            if c != '\x02':
                if c == '\x01':
                    if unitSize == AbstractType.UNITSIZE_8:
                        align += "--"
                    elif unitSize == AbstractType.UNITSIZE_4:
                        align += "-"
                else:
                    if unitSize == AbstractType.UNITSIZE_8:
                        align += TypeConverter.convert(regex[i:i + 1], Raw, HexaString)
                    elif unitSize == AbstractType.UNITSIZE_4:
                        align += TypeConverter.convert(regex[i:i + 1], Raw, HexaString)[1:]
        return align

    @property
    def doInternalSlick(self):
        return self.__doInternalSlick

    @doInternalSlick.setter
    @typeCheck(bool)
    def doInternalSlick(self, doInternalSlick):
        if doInternalSlick is None:
            raise TypeError("doInternalSlick cannot be None")
        self.__doInternalSlick = doInternalSlick

    @property
    def unitSize(self):
        return self.__unitSize

    @unitSize.setter
    @typeCheck(str)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("Unitsize cannot be None")
        if unitSize not in AbstractType.supportedUnitSizes():
            raise TypeError("Specified unitsize is not supported, refers to AbstractType.supportedUnitSizes() for the list.")
        self.__unitSize = unitSize
