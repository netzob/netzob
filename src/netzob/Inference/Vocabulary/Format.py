#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, UnitSize
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitStatic.FieldSplitStatic import FieldSplitStatic
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitDelimiter import FieldSplitDelimiter
from netzob.Inference.Vocabulary.FormatOperations.FieldReseter import FieldReseter
from netzob.Inference.Vocabulary.FormatOperations.FieldOperations import FieldOperations
from netzob.Inference.Vocabulary.FormatOperations.FieldSplitAligned.FieldSplitAligned import FieldSplitAligned
from netzob.Inference.Vocabulary.FormatOperations.ClusterByAlignment import ClusterByAlignment
from netzob.Inference.Vocabulary.FormatOperations.ClusterByKeyField import ClusterByKeyField
from netzob.Inference.Vocabulary.FormatOperations.ClusterByApplicativeData import ClusterByApplicativeData
from netzob.Inference.Vocabulary.FormatOperations.ClusterBySize import ClusterBySize
from netzob.Inference.Vocabulary.FormatOperations.FindKeyFields import FindKeyFields


class Format(object):
    """This class is a wrapper for all the various tools
    which allow to edit the format of a field.

    """

    @staticmethod
    @typeCheck(AbstractField)
    def splitAligned(field, useSemantic=True, doInternalSlick=False):
        r"""Split the specified field according to the variations of message bytes.
        Relies on a sequence alignment algorithm.

        The following example is an anti-regression test
        for issue https://github.com/netzob/netzob/issues/13 reported by Sergej

        >>> from netzob.all import *
        >>> import binascii
        >>> message1 = binascii.unhexlify(b"01010600823d16c1040000000000000000000000000000000000000000238b34d4c400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501017401013d070100238b34d4c40c05466c616d653c084d53465420352e30370b010f03062c2e2f1f21f92b2b02dc00ff00000000000000000000")
        >>> message2 = binascii.unhexlify(b"02010600823d16c10000000000000000c0a80103c0a801010000000000238b34d4c400000000000000000000646f6d65782e6e70732e6564750000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501023604c0a80101330400000dec0104ffffff000f000304c0a801010604c0a80101ff000000000000000000000000000000000000000000000000")
        >>> messages = [RawMessage(message1), RawMessage(message2)]
        >>> symbol = Symbol(messages=messages)
        >>> Format.splitAligned(symbol, doInternalSlick=True)
        >>> len(symbol.getCells())
        2

        """
        if field is None:
            raise TypeError("Field cannot be None")

        fs = FieldSplitAligned(doInternalSlick=doInternalSlick)
        fs.execute(field, useSemantic)

    @staticmethod
    @typeCheck(AbstractField, str)
    def splitStatic(field,
                    unitSize=UnitSize.SIZE_8,
                    mergeAdjacentStaticFields=True,
                    mergeAdjacentDynamicFields=True):
        """Split the portion of the message matching the specified fields
        following their variations of each unitsize.
        This method returns nothing, it upgrades the field structure
        with the result of the splitting process.

        Its a wrapper for :class:`ParallelFieldSplitStatic <netzob.Inference.Vocabulary.FieldSplitStatic.ParallelFieldSplitStatic.ParallelFieldSplitStatic>`.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000",	"000010000000",	"00fe1f000000",	"000020000000", "00ff1f000000",	"00ff1f000000",	"00ff2f000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        Field         
        --------------
        '00ff2f000000'
        '000010000000'
        '00fe1f000000'
        '000020000000'
        '00ff1f000000'
        '00ff1f000000'
        '00ff2f000000'
        '00fe1f000000'
        --------------
        
        >>> Format.splitStatic(symbol)
        >>> print(symbol.str_data())
        Field-0 | Field-1 | Field-2 
        ------- | ------- | --------
        '00'    | 'ff2f'  | '000000'
        '00'    | '0010'  | '000000'
        '00'    | 'fe1f'  | '000000'
        '00'    | '0020'  | '000000'
        '00'    | 'ff1f'  | '000000'
        '00'    | 'ff1f'  | '000000'
        '00'    | 'ff2f'  | '000000'
        '00'    | 'fe1f'  | '000000'
        ------- | ------- | --------

        >>> from netzob.all import *
        >>> samples = ["0300002502f080320100003a00000e00060501120a10020002006e840000400004001001ab", "0300001602f080320300003a000002000100000501ff", "0300000702f000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> symbol.encodingFunctions.add(TypeEncodingFunction(HexaString))
        >>> Format.splitStatic(symbol)
        >>> print(symbol.str_data())
        Field-0  | Field-1 | Field-2 | Field-3                                                         
        -------- | ------- | ------- | ----------------------------------------------------------------
        '030000' | '25'    | '02f0'  | '80320100003a00000e00060501120a10020002006e840000400004001001ab'
        '030000' | '16'    | '02f0'  | '80320300003a000002000100000501ff'                              
        '030000' | '07'    | '02f0'  | '00'                                                            
        -------- | ------- | ------- | ----------------------------------------------------------------
        
        >>> contents = ["hello lapy, what's up in Paris ?", "hello lapy, what's up in Berlin ?", "hello lapy, what's up in New-York ?"]
        >>> messages = [RawMessage(data=m) for m in contents]
        >>> s = Symbol(messages=messages)
        >>> print(s.str_data())
        Field                                
        -------------------------------------
        "hello lapy, what's up in Paris ?"   
        "hello lapy, what's up in Berlin ?"  
        "hello lapy, what's up in New-York ?"
        -------------------------------------
        >>> Format.splitStatic(s)
        >>> print(s.str_data())
        Field-0                     | Field-1     
        --------------------------- | ------------
        "hello lapy, what's up in " | 'Paris ?'   
        "hello lapy, what's up in " | 'Berlin ?'  
        "hello lapy, what's up in " | 'New-York ?'
        --------------------------- | ------------

        :param field: the field for which we update the format
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :keyword unitSize: the required size of static element to create a static field
        :type unitSize: :class:`int`.
        :keyword mergeAdjacentStaticFields: if set to true, adjacent static fields are merged in a single field
        :type mergeAdjacentStaticFields: :class:`bool`
        :keyword mergeAdjacentDynamicFields: if set to true, adjacent dynamic fields are merged in a single field
        :type mergeAdjacentDynamicFields: :class:`bool`
        :raise Exception if something bad happens
        """

        if field is None:
            raise TypeError("Field cannot be None")

        if unitSize is None:
            raise TypeError("Unitsize cannot be None")

        if len(field.messages) < 1:
            raise ValueError(
                "The associated symbol does not contain any message.")

        FieldSplitStatic.split(field, unitSize, mergeAdjacentStaticFields,
                               mergeAdjacentDynamicFields)

    @staticmethod
    @typeCheck(AbstractField, AbstractType)
    def splitDelimiter(field, delimiter):
        """Split a field (or symbol) with a specific delimiter. The
        delimiter can be passed either as a String, a Raw, an
        HexaString, or any objects that inherit from AbstractType.

        >>> from netzob.all import *
        >>> samples = ["aaaaff000000ff10",	"bbff110010ff00000011",	"ccccccccfffe1f000000ff12"]
        >>> messages = [RawMessage(data=sample) for sample in samples]
        >>> symbol = Symbol(messages=messages[:3])
        >>> Format.splitDelimiter(symbol, String("ff"))
        >>> print(symbol.str_data())
        Field-0    | Field-sep-6666 | Field-2      | Field-sep-6666 | Field-4   
        ---------- | -------------- | ------------ | -------------- | ----------
        'aaaa'     | 'ff'           | '000000'     | 'ff'           | '10'      
        'bb'       | 'ff'           | '110010'     | 'ff'           | '00000011'
        'cccccccc' | 'ff'           | 'fe1f000000' | 'ff'           | '12'      
        ---------- | -------------- | ------------ | -------------- | ----------


        Lets take another example:


        >>> from netzob.all import *
        >>> import binascii
        >>> samples = [b"434d446964656e74696679230400000066726564", b"5245536964656e74696679230000000000000000", b"434d44696e666f2300000000", b"524553696e666f230000000004000000696e666f", b"434d4473746174732300000000", b"52455373746174732300000000050000007374617473", b"434d4461757468656e7469667923090000006d7950617373776421", b"52455361757468656e74696679230000000000000000"]           
        >>> print(len(samples))
        8
        >>> symbol = Symbol(messages=[RawMessage(binascii.unhexlify(sample)) for sample in samples])
        >>> symbol.encodingFunctions.add(TypeEncodingFunction(HexaString))
        >>> Format.splitDelimiter(symbol, String('#'))
        >>> print(symbol.str_data())
        Field-0                      | Field-sep-23 | Field-2                     
        ---------------------------- | ------------ | ----------------------------
        '434d446964656e74696679'     | '#'          | '0400000066726564'          
        '5245536964656e74696679'     | '#'          | '0000000000000000'          
        '434d44696e666f'             | '#'          | '00000000'                  
        '524553696e666f'             | '#'          | '0000000004000000696e666f'  
        '434d447374617473'           | '#'          | '00000000'                  
        '5245537374617473'           | '#'          | '00000000050000007374617473'
        '434d4461757468656e74696679' | '#'          | '090000006d7950617373776421'
        '52455361757468656e74696679' | '#'          | '0000000000000000'          
        ---------------------------- | ------------ | ----------------------------


        :param field : the field to consider when spliting
        :type: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :param delimiter : the delimiter used to split messages of the field
        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        if delimiter is None:
            raise TypeError("Delimiter cannot be None or empty")

        if field is None:
            raise TypeError("Field cannot be None")

        if len(field.messages) < 1:
            raise ValueError(
                "The associated symbol does not contain any message.")

        FieldSplitDelimiter.split(field, delimiter)

    @staticmethod
    @typeCheck(AbstractField)
    def resetFormat(field):
        """Reset the format (field hierarchy and definition domain) of
        the specified field.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000",	"000010000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1))
        >>> f2 = Field(Raw(nbBytes=2))
        >>> f3 = Field(Raw(nbBytes=3))
        >>> symbol = Symbol([f1, f2, f3], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        Field | Field  | Field   
        ----- | ------ | --------
        '00'  | 'ff2f' | '000000'
        '00'  | '0010' | '000000'
        '00'  | 'fe1f' | '000000'
        ----- | ------ | --------
        >>> Format.resetFormat(symbol)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))        
        >>> print(symbol.str_data())
        Field         
        --------------
        '00ff2f000000'
        '000010000000'
        '00fe1f000000'
        --------------

        :param field: the field we want to reset
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raise Exception if something bad happens
        """
        if field is None:
            raise TypeError(
                "The field to reset must be specified and cannot be None")

        fr = FieldReseter()
        fr.reset(field)

    @staticmethod
    @typeCheck(AbstractField, AbstractField)
    def mergeFields(field1, field2):
        """Merge provided fields and their definitions

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000", "000010000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1), name="f1")
        >>> f2 = Field(Raw(nbBytes=2), name="f2")
        >>> f3 = Field(Raw(nbBytes=2), name="f3")
        >>> f4 = Field(Raw(nbBytes=1), name="f4")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        f1   | f2     | f3     | f4  
        ---- | ------ | ------ | ----
        '00' | 'ff2f' | '0000' | '00'
        '00' | '0010' | '0000' | '00'
        '00' | 'fe1f' | '0000' | '00'
        ---- | ------ | ------ | ----
        >>> Format.mergeFields(f2, f3)
        >>> print(symbol.str_data())
        f1   | Merge      | f4  
        ---- | ---------- | ----
        '00' | 'ff2f0000' | '00'
        '00' | '00100000' | '00'
        '00' | 'fe1f0000' | '00'
        ---- | ---------- | ----
        >>> Format.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol.str_data())
        Merge        | f4  
        ------------ | ----
        '00ff2f0000' | '00'
        '0000100000' | '00'
        '00fe1f0000' | '00'
        ------------ | ----
        >>> Format.mergeFields(symbol.fields[0], symbol.fields[1])
        >>> print(symbol.str_data())
        Merge         
        --------------
        '00ff2f000000'
        '000010000000'
        '00fe1f000000'
        --------------


        :param field: the field we want to reset
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raise Exception if something bad happens
        """
        if field1 is None or field2 is None:
            raise TypeError("Fields cannot be None")

        fr = FieldOperations()
        fr.mergeFields(field1, field2)

    @staticmethod
    @typeCheck(list)
    def clusterByAlignment(messages, minEquivalence=50, internalSlick=True):
        """This clustering process regroups messages in groups that maximes
        their alignement. It provides the required methods to compute clustering
        between multiple symbols/messages using UPGMA algorithms (see U{http://en.wikipedia.org/wiki/UPGMA}).
        When processing, the matrix of scores is computed by the C extensions (L{_libScoreComputation}
        and used to regroup messages and symbols into equivalent cluster.
        """
        clustering = ClusterByAlignment(
            minEquivalence=minEquivalence, internalSlick=internalSlick)
        return clustering.cluster(messages)

    @staticmethod
    @typeCheck(list)
    def clusterBySource(messages):
        """Regroup messages sent by the same source

        >>> import operator
        >>> from netzob.all import *
        >>> messages = [RawMessage("hello berlin", source="user"), RawMessage("hello paris", source="master")]
        >>> messages.extend([RawMessage("hello madrid", source="master"), RawMessage("hello world", source="user")])
        >>> symbols = Format.clusterBySource(messages)
        >>> print(len(symbols))
        2
        >>> for symbol in sorted(symbols, key=operator.attrgetter("name")):
        ...     print("{}:".format(symbol.name))
        ...     print(symbol.str_data())
        Symbol-master:
        Field         
        --------------
        'hello paris' 
        'hello madrid'
        --------------
        Symbol-user:
        Field         
        --------------
        'hello berlin'
        'hello world' 
        --------------

        """

        clusters = dict()
        for message in messages:
            if message.source in clusters.keys():
                clusters[message.source].messages.append(message)
            else:
                clusters[message.source] = Symbol(name="Symbol-{}".format(message.source), messages = [message])

        return list(clusters.values())

    @staticmethod
    @typeCheck(list)
    def clusterByDestination(messages):
        """Regroup messages sent to the same destination

        >>> import operator
        >>> from netzob.all import *
        >>> messages = [RawMessage("hello berlin", destination="user"), RawMessage("hello paris", destination="master")]
        >>> messages.extend([RawMessage("hello madrid", destination="master"), RawMessage("hello world", destination="user")])
        >>> symbols = Format.clusterByDestination(messages)
        >>> print(len(symbols))
        2
        >>> for symbol in sorted(symbols, key=operator.attrgetter("name")):
        ...     print("{}:".format(symbol.name))
        ...     print(symbol.str_data())
        Symbol-master:
        Field         
        --------------
        'hello paris' 
        'hello madrid'
        --------------
        Symbol-user:
        Field         
        --------------
        'hello berlin'
        'hello world' 
        --------------

        """

        clusters = dict()
        for message in messages:
            if message.destination in clusters.keys():
                clusters[message.destination].messages.append(message)
            else:
                clusters[message.destination] = Symbol(name="Symbol-{}".format(message.destination), messages = [message])

        return list(clusters.values())


    @staticmethod
    @typeCheck(list)
    def clusterByApplicativeData(messages):
        """Regroup messages having the same applicative data in their content.

        >>> import time
        >>> import random
        >>> import operator
        >>> from netzob.all import *
        >>> # we create 3 types of messages:

        >>> messages = []
        >>> for x in range(5):
        ...     messages.append(RawMessage("ACK {0}".format(random.randint(0, 50)), source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:{0}:01".format(x), "%d %b %y %H:%M:%S"))))
        ...     messages.append(RawMessage("SYN {0}".format(random.randint(0, 50)), source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:{0}:02".format(x), "%d %b %y %H:%M:%S"))))
        ...     messages.append(RawMessage("SYN/ACK {0}".format(random.randint(0, 50)), source="B", destination="A", date=time.mktime(time.strptime("9 Aug 13 10:{0}:03".format(x), "%d %b %y %H:%M:%S"))))
        ...     time.sleep(0.2)
        >>> session = Session(messages=messages)
        >>> appDatas = []
        >>> appDatas.append(ApplicativeData("ACK", String("ack")))
        >>> appDatas.append(ApplicativeData("SYN", String("syn")))
        >>> session.applicativeData = appDatas
        >>> symbols = Format.clusterByApplicativeData(messages)
        >>> for symbol in sorted(symbols, key=operator.attrgetter("name")):
        ...     print("Symbol : {0} = {1} messages.".format(symbol.name, len(symbol.messages)))
        Symbol : ACK = 5 messages.
        Symbol : ACK;SYN = 5 messages.
        Symbol : SYN = 5 messages.

        :param messages: the messages to cluster.
        :type messages: a list of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        :return: a list of symbol representing all the computed clusters
        :rtype: a list of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        :raises: a TypeError if symbol is not valid.
        """
        if (messages is None or len(messages) == 0):
            raise TypeError("At least one message should be specified.")

        # We retrieve all the applicative data
        appDatas = []
        sessions = []
        for message in messages:
            if message.session is not None and message.session not in sessions:
                sessions.append(message.session)

        for session in sessions:
            appDatas.extend(session.applicativeData)

        if len(appDatas) == 0:
            raise ValueError(
                "There are no applicative data attached to the session from which the specified messages come from."
            )

        cluster = ClusterByApplicativeData()
        return cluster.cluster(messages, appDatas)

    @staticmethod
    @typeCheck(AbstractField, AbstractField)
    def clusterByKeyField(field, keyField):
        """Create and return new symbols according to a specific key
        field.

        This method is a wrapper for :class:`ClusterByKeyField <netzob.Inference.Vocabulary.FormatOperations.ClusterByKeyField.ClusterByKeyField>`

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000000",	"000020000000",	"00ff2f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> f1 = Field(Raw(nbBytes=1))
        >>> f2 = Field(Raw(nbBytes=2))
        >>> f3 = Field(Raw(nbBytes=3))
        >>> symbol = Symbol([f1, f2, f3], messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))

        >>> newSymbols = Format.clusterByKeyField(symbol, f2)
        >>> for sym in list(newSymbols.values()):
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print(sym.name + ":")
        ...     print(sym.str_data())
        Symbol_ff2f:
        Field | Field  | Field   
        ----- | ------ | --------
        '00'  | 'ff2f' | '000000'
        '00'  | 'ff2f' | '000000'
        ----- | ------ | --------
        Symbol_0020:
        Field | Field  | Field   
        ----- | ------ | --------
        '00'  | '0020' | '000000'
        ----- | ------ | --------

        :param field: the field we want to split in new symbols
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :param keyField: the field used as a key during the splitting operation
        :type field: :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raise Exception if something bad happens

        """
        # Safe checks
        if field is None:
            raise TypeError("'field' should not be None")
        if keyField is None:
            raise TypeError("'keyField' should not be None")
        if not keyField in field.fields:
            raise TypeError("'keyField' is not a child of 'field'")

        clusterByKeyField = ClusterByKeyField()
        return clusterByKeyField.cluster(field, keyField)

    @staticmethod
    @typeCheck(AbstractField)
    def findKeyFields(field):
        """Try to identify potential key fields in a symbol/field.

        >>> import binascii
        >>> from netzob.all import *
        >>> samples = ["00ff2f000011",	"000010000000",	"00fe1f000000",	"000020000000", "00ff1f000000",	"00ff1f000000",	"00ff2f000000",	"00fe1f000000"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> symbol = Symbol(messages=messages)
        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> Format.splitStatic(symbol)
        >>> results = Format.findKeyFields(symbol)
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

        keyFieldsFinder = FindKeyFields()
        return keyFieldsFinder.execute(field)

    @staticmethod
    @typeCheck(list)
    def clusterBySize(messages):
        """This clustering process regroups messages that have
        equivalent size.

        >>> from netzob.all import *
        >>> import binascii
        >>> samples = ["00ffff1100abcd", "00aaaa1100abcd", "00bbbb1100abcd", "001100abcd", "001100ffff", "00ffffffff1100abcd"]
        >>> messages = [RawMessage(data=binascii.unhexlify(sample)) for sample in samples]
        >>> newSymbols = Format.clusterBySize(messages)
        >>> for sym in newSymbols:
        ...     print("[" + sym.name + "]")
        ...     sym.addEncodingFunction(TypeEncodingFunction(HexaString))
        ...     print(sym.str_data())
        [symbol_7]
        Field           
        ----------------
        '00ffff1100abcd'
        '00aaaa1100abcd'
        '00bbbb1100abcd'
        ----------------
        [symbol_5]
        Field       
        ------------
        '001100abcd'
        '001100ffff'
        ------------
        [symbol_9]
        Field               
        --------------------
        '00ffffffff1100abcd'
        --------------------

        :param messages: the messages to cluster.
        :type messages: a list of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        :return: a list of symbol representing all the computed clusters
        :rtype: a list of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """

        # Safe checks
        if messages is None:
            raise TypeError("'messages' should not be None")

        clustering = ClusterBySize()
        return clustering.cluster(messages)
