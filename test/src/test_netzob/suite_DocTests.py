#!/usr/bin/python
# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
import doctest

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.all import *
from netzob.Common.Utils import NetzobRegex
from netzob.Common.Utils.DataAlignment import ParallelDataAlignment
from netzob.Common.Utils.DataAlignment import DataAlignment
from netzob.Common.Models.Vocabulary import AbstractField
from netzob.Common.Models.Vocabulary.Domain.Variables import AbstractVariable
from netzob.Common.Models.Vocabulary.Messages import AbstractMessage

from netzob.Inference.Vocabulary.FormatEditorOperations import FieldReseter
from netzob.Inference.Vocabulary.FormatEditorOperations.FieldSplitStatic import FieldSplitStatic
from netzob.Inference.Vocabulary.FormatIdentifierOperations import ClusterByKeyField
from netzob.Common.Utils import SortedTypedList

from netzob.Inference.Vocabulary.Search import SearchTask
from netzob.Inference.Vocabulary.Search import SearchResult


def getSuite():
    # List of modules to include in the list of tests
    modules = [
        Protocol.__module__,
        Field.__module__,
        AbstractField,
        Symbol.__module__,
        RawMessage.__module__,
        DomainFactory.__module__,
        Alt.__module__,
        Agg.__module__,
        Data.__module__,
        ASCII.__module__,
        Decimal.__module__,
        BitArray.__module__,
        Raw.__module__,
        HexaString.__module__,
        AbstractType.__module__,
        Memory.__module__,
        TypeConverter.__module__,
        AbstractVariable,
        VariableReadingToken.__module__,
        # # JSONSerializator.__module__,
        # # TCPServer.__module__,
        # # Actor.__module__,
        # # Angluin.__module__,
        State.__module__,
        Transition.__module__,
        NetzobRegex,
        RawMessage.__module__,
        ParallelDataAlignment,
        DataAlignment,
        FormatEditor.__module__,
        FieldSplitStatic,
        FormatIdentifier.__module__,
        FieldReseter,
        AbstractMessage,
        ClusterByKeyField,
        Session.__module__,
        SortedTypedList,
        ApplicativeData.__module__,
        DomainEncodingFunction.__module__,
        TypeEncodingFunction.__module__,
        SearchEngine.__module__,
        SearchTask,
        SearchResult,
        
    ]

    suite = unittest.TestSuite()
    for mod in modules:
        suite.addTest(doctest.DocTestSuite(mod))
    return suite
