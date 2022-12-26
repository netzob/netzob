# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField


@NetzobLogger
class FindKeyFields(object):
    """This class provides methods to identify potential key fields in
    symbols/fields.
    """

    @typeCheck(AbstractField)
    def execute(self, field):
        """Try to identify potential key fields in a symbol/field.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = [b"00ff2f000011",	b"000010000000", b"00fe1f000000", b"000020000000", b"00ff1f000000", b"00ff1f000000", b"00ff2f000000", b"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> Format.splitStatic(symbol)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        Field-0 | Field-1 | Field-2 | Field-3
        ------- | ------- | ------- | -------
        '00'    | 'ff2f'  | '0000'  | '11'   
        '00'    | '0010'  | '0000'  | '00'   
        '00'    | 'fe1f'  | '0000'  | '00'   
        '00'    | '0020'  | '0000'  | '00'   
        '00'    | 'ff1f'  | '0000'  | '00'   
        '00'    | 'ff1f'  | '0000'  | '00'   
        '00'    | 'ff2f'  | '0000'  | '00'   
        '00'    | 'fe1f'  | '0000'  | '00'   
        ------- | ------- | ------- | -------

        >>> finder = FindKeyFields()
        >>> results = finder.execute(symbol)
        >>> for result in results:
        ...     print("Field name: " + result["keyField"].name + ", number of clusters: " + str(result["nbClusters"]) + ", distribution: " + str(result["distribution"]))
        Field name: Field-1, number of clusters: 5, distribution: [2, 1, 2, 1, 2]
        Field name: Field-3, number of clusters: 2, distribution: [1, 7]

        :param field: the field in which we want to identify key fields.
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raise Exception if something bad happens
        """

        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if len(field.messages) < 2:
            return []

        results = []
        cells = field.getCells(encoded=False, styled=False, transposed=False)
        columns = list(zip(*cells))

        # Retrieve dynamic fields with fixed size
        for (i, f) in enumerate(field.fields):
            isCandidate = True
            lRef = len(columns[i][1])
            if len(set(columns[i])) <= 1:
                isCandidate = False
                continue
            for val in columns[i][1:]:
                if lRef != len(val):
                    isCandidate = False
                    break
            if isCandidate:
                results.append({"keyField": f})

        # Compute clusters according to each key field found
        from netzob.Inference.Vocabulary.Format import Format
        for result in results:
            tmpClusters = Format.clusterByKeyField(field, result["keyField"])
            result["nbClusters"] = len(tmpClusters)
            distrib = []  # Compute clusters distribution
            for cluster in list(tmpClusters.values()):
                distrib.append(len(cluster.messages))
            result["distribution"] = distrib

        return results
