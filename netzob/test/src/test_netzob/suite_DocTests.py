# !/usr/bin/python
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
# | Standard library imports
# +---------------------------------------------------------------------------+
import unittest
import doctest

# +---------------------------------------------------------------------------+
# | Local application imports
# +---------------------------------------------------------------------------+
from netzob.all import *
from netzob.Common.Utils.DataAlignment import ParallelDataAlignment
from netzob.Common.Utils.DataAlignment import DataAlignment
from netzob.Model.Vocabulary import AbstractField
from netzob.Model.Vocabulary.Domain.Variables import AbstractVariable
from netzob.Model.Vocabulary.Messages import AbstractMessage

from netzob.Inference.Vocabulary.FormatOperations import FieldReseter
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitStatic.FieldSplitStatic import FieldSplitStatic
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitStatic.ParallelFieldSplitStatic import ParallelFieldSplitStatic
from netzob.Inference.Vocabulary.FormatOperations import ClusterByKeyField
from netzob.Inference.Vocabulary.FormatOperations import ClusterByApplicativeData
from netzob.Inference.Vocabulary.FormatOperations import ClusterByAlignment
from netzob.Inference.Vocabulary.FormatOperations import ClusterBySize
from netzob.Inference.Vocabulary.FormatOperations import FindKeyFields
from netzob.Common.Utils import SortedTypedList
from netzob.Common.Utils import MessageCells

from netzob.Inference.Vocabulary.Search import SearchTask
from netzob.Inference.Vocabulary.Search import SearchResult
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitAligned import FieldSplitAligned
from netzob.Inference.Vocabulary.FormatOperations import FieldSplitDelimiter

from netzob.Inference.Vocabulary.FormatOperations import FieldOperations
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Specializer.FieldSpecializer import FieldSpecializer
from netzob.Model.Vocabulary.Domain.Specializer.VariableSpecializer import VariableSpecializer
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS

from netzob.Model.Vocabulary.Domain.Parser.MessageParser import MessageParser
from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
from netzob.Model.Vocabulary.Domain.Parser.FlowParser import FlowParser

from netzob.Simulator.AbstractionLayer import AbstractionLayer

from netzob.Inference.Vocabulary import EntropyMeasurement
# from netzob.Inference.Grammar.Angluin import Angluin
from netzob.Inference.Grammar.AutomataFactories.ChainedStatesAutomataFactory import ChainedStatesAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.PTAAutomataFactory import PTAAutomataFactory

from netzob.Inference.Grammar.ProcessWrappers import ProcessWrapper
from netzob.Inference.Grammar.ProcessWrappers import NetworkProcessWrapper

def getSuite():
    # List of modules to include in the list of tests
    modules = [

        # Modules related to common types and data structures
        # ---------------------------------------------------
        ASCII.__module__,
        Integer.__module__,
        BitArray.__module__,
        Raw.__module__,
        HexaString.__module__,
        IPv4.__module__,
        Timestamp.__module__,

        # Modules related to the vocabulary inference
        # -------------------------------------------
        Protocol.__module__,
        Field.__module__,
        DataAlignment, 
        ParallelDataAlignment,        
        AbstractField,
        Symbol.__module__,
        EmptySymbol.__module__,
        UnknownSymbol.__module__,
        ChannelDownSymbol.__module__,
        DomainFactory.__module__,
        Alt.__module__,
        Agg.__module__,
        Repeat.__module__,        
        Data.__module__,
        FieldSplitStatic.__module__,
        FieldSplitAligned,
        FieldSplitDelimiter,
        ParallelFieldSplitStatic.__module__,
        FindKeyFields,
        FieldReseter,
        AbstractMessage,
        ClusterByKeyField,
        
        RawMessage.__module__,
        L2NetworkMessage.__module__,
        L3NetworkMessage.__module__,
        L4NetworkMessage.__module__,
        FileMessage.__module__,
        FieldOperations,
        CorrelationFinder.__module__,
        RelationFinder.__module__,
        Format.__module__,
        Session.__module__,
        SortedTypedList,
        MessageCells,
        ApplicativeData.__module__,
        DomainEncodingFunction.__module__,
        TypeEncodingFunction.__module__,
        ZLibEncodingFunction.__module__,
        Base64EncodingFunction.__module__,
        SearchEngine.__module__,
        SearchTask,
        SearchResult,
        ClusterByApplicativeData,
        ClusterByAlignment,
        ClusterBySize,
        AbstractType.__module__,
        Memory.__module__,
        TypeConverter.__module__,
        AbstractVariable,
        Size.__module__,
        Value.__module__,        
        InternetChecksum.__module__,
        FieldParser.__module__,
        GenericPath.__module__,
        VariableSpecializer.__module__,
        FieldSpecializer.__module__,
        SVAS.__module__,

        MessageParser.__module__,
        MessageSpecializer.__module__,

        FlowParser.__module__,
        AbstractionLayer.__module__,
        EntropyMeasurement,

        # Modules related to the grammatical inference
        # --------------------------------------------
        # Angluin.__module__,
        State.__module__,
        Transition.__module__,
        AbstractionLayer.__module__,
        Automata.__module__,
        ProcessWrapper,
        NetworkProcessWrapper,
        
        # Modules related to the protocol simulation
        # ------------------------------------------
        Actor.__module__,
        TCPServer.__module__,
        TCPClient.__module__,
        UDPServer.__module__,
        UDPClient.__module__,
        SSLClient.__module__,
        # RawIPClient.__module__,  ## Does not work on Travis CI as raw socket are not supported

        # Modules related to the import
        # -----------------------------
        PCAPImporter.__module__,
        FileImporter.__module__

        # Other
        # -----
        # # JSONSerializator.__module__,
        # # TCPServer.__module__,

    ]

    suite = unittest.TestSuite()
    for mod in modules:
        suite.addTest(doctest.DocTestSuite(mod))
    return suite
