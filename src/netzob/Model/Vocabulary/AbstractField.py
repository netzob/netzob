#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
import uuid
import abc
import logging
from collections import OrderedDict

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.UndoRedo.AbstractMementoCreator import AbstractMementoCreator
from netzob.Model.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Model.Vocabulary.Functions.VisualizationFunction import VisualizationFunction
from netzob.Model.Vocabulary.Functions.TransformationFunction import TransformationFunction
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Utils.SortedTypedList import SortedTypedList


class InvalidVariableException(Exception):
    """This exception is raised when the variable behing the definition
    a field domain (and structure) is not valid. The variable definition
    is upgraded everytime the domain is modified.
    """
    pass


class AlignmentException(Exception):
    pass


class NoSymbolException(Exception):
    pass


class GenerationException(Exception):
    pass


class AbstractionException(Exception):
    pass


@NetzobLogger
class AbstractField(AbstractMementoCreator, metaclass=abc.ABCMeta):
    """Represents all the different classes which participates in fields definitions of a message format."""

    def __init__(self, name=None, layer=False):
        self.id = uuid.uuid4()
        self.name = name
        self.layer = layer
        self.description = ""

        self.__fields = TypedList(AbstractField)
        self.__parent = None

        self.__encodingFunctions = SortedTypedList(EncodingFunction)
        self.__visualizationFunctions = TypedList(VisualizationFunction)
        self.__transformationFunctions = TypedList(TransformationFunction)

        self._variable = None

    @typeCheck(bool, bool, bool)
    def getCells(self, encoded=True, styled=True, transposed=False):
        """Returns a matrix with a different line for each messages attached to the symbol of the current element.

        The matrix includes a different column for each leaf children of the current element.
        In each cell, the slices of messages once aligned.
        Attached :class:`EncodingFunction` can also be considered if parameter encoded is set to True.
        In addition, visualizationFunctions are also applied if parameter styled is set to True.
        If parameter Transposed is set to True, the matrix is built with rows for fields and columns for messages.

        >>> from netzob.all import *
        >>> messages = [RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['netzob', 'zoby', 'lapy'] for city in ['Paris', 'Berlin', 'New-York']]
        >>> fh1 = Field(ASCII("hello "), name="hello")
        >>> fh2 = Field(Alt([ASCII("netzob"), ASCII("zoby"), ASCII("lapy"), ASCII("sygus")]), name="pseudo")
        >>> fheader = Field(name="header")
        >>> fheader.fields = [fh1, fh2]
        >>> fb1 = Field(ASCII(", what's up in "), name="whatsup")
        >>> fb2 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> fb3 = Field(" ?", name="end")
        >>> fbody = Field(name="body")
        >>> fbody.fields = [fb1, fb2, fb3]
        >>> symbol = Symbol([fheader, fbody], messages=messages)

        >>> print(symbol)
        hello    | pseudo   | whatsup           | city       | end 
        -------- | -------- | ----------------- | ---------- | ----
        'hello ' | 'netzob' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'netzob' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'netzob' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'New-York' | ' ?'
        -------- | -------- | ----------------- | ---------- | ----

        >>> fh1.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> fb2.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol)
        hello          | pseudo   | whatsup           | city               | end 
        -------------- | -------- | ----------------- | ------------------ | ----
        '68656c6c6f20' | 'netzob' | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'netzob' | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'netzob' | ", what's up in " | '4e65772d596f726b' | ' ?'
        '68656c6c6f20' | 'zoby'   | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'zoby'   | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'zoby'   | ", what's up in " | '4e65772d596f726b' | ' ?'
        '68656c6c6f20' | 'lapy'   | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'lapy'   | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'lapy'   | ", what's up in " | '4e65772d596f726b' | ' ?'
        -------------- | -------- | ----------------- | ------------------ | ----

        >>> print(fheader.getCells()) 
        Field          | Field   
        -------------- | --------
        '68656c6c6f20' | 'netzob'
        '68656c6c6f20' | 'netzob'
        '68656c6c6f20' | 'netzob'
        '68656c6c6f20' | 'zoby'  
        '68656c6c6f20' | 'zoby'  
        '68656c6c6f20' | 'zoby'  
        '68656c6c6f20' | 'lapy'  
        '68656c6c6f20' | 'lapy'  
        '68656c6c6f20' | 'lapy'  
        -------------- | --------

        >>> print(fh1.getCells())
        Field         
        --------------
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        '68656c6c6f20'
        --------------

        >>> print(fh2.getCells())
        Field   
        --------
        'netzob'
        'netzob'
        'netzob'
        'zoby'  
        'zoby'  
        'zoby'  
        'lapy'  
        'lapy'  
        'lapy'  
        --------

        >>> print(fbody.getCells())
        Field             | Field              | Field
        ----------------- | ------------------ | -----
        ", what's up in " | '5061726973'       | ' ?' 
        ", what's up in " | '4265726c696e'     | ' ?' 
        ", what's up in " | '4e65772d596f726b' | ' ?' 
        ", what's up in " | '5061726973'       | ' ?' 
        ", what's up in " | '4265726c696e'     | ' ?' 
        ", what's up in " | '4e65772d596f726b' | ' ?' 
        ", what's up in " | '5061726973'       | ' ?' 
        ", what's up in " | '4265726c696e'     | ' ?' 
        ", what's up in " | '4e65772d596f726b' | ' ?' 
        ----------------- | ------------------ | -----

        >>> print(fb1.getCells())
        Field            
        -----------------
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        ", what's up in "
        -----------------

        >>> print(fb2.getCells())
        Field             
        ------------------
        '5061726973'      
        '4265726c696e'    
        '4e65772d596f726b'
        '5061726973'      
        '4265726c696e'    
        '4e65772d596f726b'
        '5061726973'      
        '4265726c696e'    
        '4e65772d596f726b'
        ------------------

        >>> print(fb3.getCells())
        Field
        -----
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        ' ?' 
        -----

        :keyword encoded: if set to True, encoding functions are applied on returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied on returned cells
        :type styled: :class:`bool`
        :keyword transposed: is set to True, the returned matrix is transposed (1 line for each field)
        :type transposed: :class:`bool`

        :return: a matrix representing the aligned messages following fields definitions.
        :rtype: a :class:`netzob.Common.Utils.MatrixList.MatrixList`
        :raises: :class:`netzob.Model.Vocabulary.AbstractField.AlignmentException` if an error occurs while aligning messages
        """

        if len(self.messages) < 1:
            raise ValueError("This symbol does not contain any message.")

        # Fetch all the data to align
        data = [message.data for message in self.messages]

        # [DEBUG] set to false for debug only. A sequential alignment is more simple to debug
        useParallelAlignment = False

        if useParallelAlignment:
            # Execute a parallel alignment
            from netzob.Common.Utils.DataAlignment.ParallelDataAlignment import ParallelDataAlignment
            return ParallelDataAlignment.align(data, self, encoded=encoded)
        else:
            # Execute a sequential alignment
            from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
            return DataAlignment.align(data, self, encoded=encoded)

    @typeCheck(bool, bool)
    def getValues(self, encoded=True, styled=True):
        """Returns all the values the current element can take following messages attached to the symbol of current element.

        Specific encodingFunctions can also be considered if parameter encoded is set to True.
        In addition, visualizationFunctions are also applied if parameter styled is set to True.

        >>> from netzob.all import *
        >>> messages = [RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['netzob', 'zoby', 'lapy'] for city in ['Paris', 'Berlin', 'New-York']]
        >>> f1 = Field("hello ", name="hello")
        >>> f2 = Field(["netzob", "zoby", "lapy", "sygus"], name="pseudo")
        >>> f3 = Field(", what's up in ", name="whatsup")
        >>> f4 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f5 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4, f5], messages=messages)
        >>> print(symbol)
        hello    | pseudo   | whatsup           | city       | end 
        -------- | -------- | ----------------- | ---------- | ----
        'hello ' | 'netzob' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'netzob' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'netzob' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'zoby'   | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'lapy'   | ", what's up in " | 'New-York' | ' ?'
        -------- | -------- | ----------------- | ---------- | ----

        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol)
        hello          | pseudo         | whatsup                          | city               | end   
        -------------- | -------------- | -------------------------------- | ------------------ | ------
        '68656c6c6f20' | '6e65747a6f62' | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '6e65747a6f62' | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '6e65747a6f62' | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        '68656c6c6f20' | '7a6f6279'     | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '7a6f6279'     | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '7a6f6279'     | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        '68656c6c6f20' | '6c617079'     | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '6c617079'     | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '6c617079'     | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        -------------- | -------------- | -------------------------------- | ------------------ | ------

        >>> print(symbol.getValues())
        [b'68656c6c6f206e65747a6f622c2077686174277320757020696e205061726973203f', b'68656c6c6f206e65747a6f622c2077686174277320757020696e204265726c696e203f', b'68656c6c6f206e65747a6f622c2077686174277320757020696e204e65772d596f726b203f', b'68656c6c6f207a6f62792c2077686174277320757020696e205061726973203f', b'68656c6c6f207a6f62792c2077686174277320757020696e204265726c696e203f', b'68656c6c6f207a6f62792c2077686174277320757020696e204e65772d596f726b203f', b'68656c6c6f206c6170792c2077686174277320757020696e205061726973203f', b'68656c6c6f206c6170792c2077686174277320757020696e204265726c696e203f', b'68656c6c6f206c6170792c2077686174277320757020696e204e65772d596f726b203f']
        >>> print(f1.getValues())
        [b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20']
        >>> print(f2.getValues())
        [b'6e65747a6f62', b'6e65747a6f62', b'6e65747a6f62', b'7a6f6279', b'7a6f6279', b'7a6f6279', b'6c617079', b'6c617079', b'6c617079']
        >>> print(f3.getValues())
        [b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20']
        >>> print(f4.getValues())
        [b'5061726973', b'4265726c696e', b'4e65772d596f726b', b'5061726973', b'4265726c696e', b'4e65772d596f726b', b'5061726973', b'4265726c696e', b'4e65772d596f726b']
        >>> print(f5.getValues())
        [b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f']

        :keyword encoded: if set to True, encoding functions are applied on returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied on returned cells
        :type styled: :class:`bool`

        :return: a list detailling all the values current element takes.
        :rtype: a :class:`list` of :class:`str`
        :raises: :class:`netzob.Model.Vocabulary.AbstractField.AlignmentException` if an error occurs while aligning messages
        """
        cells = self.getCells(encoded=encoded, styled=styled)
        values = []
        for line in cells:
            values.append(b''.join(line))
        return values

    @typeCheck(bool, bool)
    def getMessageCells(self, encoded=False, styled=False):
        """Computes and returns the alignment of each message belonging to
        the current field as proposed by getCells() method but indexed
        per message.

        >>> from netzob.all import *
        >>> messages = [RawMessage("{0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['netzob', 'zoby'] for city in ['Paris', 'Berlin']]
        >>> f1 = Field(["netzob", "zoby", "lapy", "sygus"], name="pseudo")
        >>> f2 = Field(", what's up in ", name="whatsup")
        >>> f3 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f4 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> print(symbol)
        pseudo   | whatsup           | city     | end 
        -------- | ----------------- | -------- | ----
        'netzob' | ", what's up in " | 'Paris'  | ' ?'
        'netzob' | ", what's up in " | 'Berlin' | ' ?'
        'zoby'   | ", what's up in " | 'Paris'  | ' ?'
        'zoby'   | ", what's up in " | 'Berlin' | ' ?'
        -------- | ----------------- | -------- | ----

        >>> messageCells = symbol.getMessageCells()
        >>> for message in symbol.messages:
        ...    print(message.data, messageCells[message])
        netzob, what's up in Paris ? [b'netzob', b", what's up in ", b'Paris', b' ?']
        netzob, what's up in Berlin ? [b'netzob', b", what's up in ", b'Berlin', b' ?']
        zoby, what's up in Paris ? [b'zoby', b", what's up in ", b'Paris', b' ?']
        zoby, what's up in Berlin ? [b'zoby', b", what's up in ", b'Berlin', b' ?']

        :keyword encoded: if set to true, values are encoded
        :type encoded: :class:`bool`
        :keyword styled: if set to true, values are styled
        :type styled: :class:`bool`
        :return: a dict indexed by messages that denotes their cells
        :rtype: a :class:`dict`

        """
        if encoded is None:
            raise TypeError("Encoded cannot be None")
        if styled is None:
            raise TypeError("Styled cannot be None")

        result = OrderedDict()
        fieldCells = self.getCells(encoded=encoded, styled=styled)

        for iMessage, message in enumerate(self.messages):
            result[message] = fieldCells[iMessage]

        return result

    @typeCheck(bool, bool)
    def getMessageValues(self, encoded=False, styled=False):
        """Computes and returns the alignment of each message belonging to
        the current field as proposed by getValues() method but indexed
        per message.

        >>> from netzob.all import *
        >>> messages = [RawMessage("{0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['netzob', 'zoby'] for city in ['Paris', 'Berlin']]
        >>> f1 = Field(["netzob", "zoby", "lapy", "sygus"], name="pseudo")
        >>> f2 = Field(", what's up in ", name="whatsup")
        >>> f3 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f4 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> print(symbol)
        pseudo   | whatsup           | city     | end 
        -------- | ----------------- | -------- | ----
        'netzob' | ", what's up in " | 'Paris'  | ' ?'
        'netzob' | ", what's up in " | 'Berlin' | ' ?'
        'zoby'   | ", what's up in " | 'Paris'  | ' ?'
        'zoby'   | ", what's up in " | 'Berlin' | ' ?'
        -------- | ----------------- | -------- | ----

        >>> messageValues = f3.getMessageValues()
        >>> for message in symbol.messages:
        ...    print(message.data, messageValues[message])
        netzob, what's up in Paris ? b'Paris'
        netzob, what's up in Berlin ? b'Berlin'
        zoby, what's up in Paris ? b'Paris'
        zoby, what's up in Berlin ? b'Berlin'

        :keyword encoded: if set to true, values are encoded
        :type encoded: :class:`bool`
        :keyword styled: if set to true, values are styled
        :type styled: :class:`bool`
        :return: a dict indexed by messages that denotes their values
        :rtype: a :class:`dict`

        """
        if encoded is None:
            raise TypeError("Encoded cannot be None")
        if styled is None:
            raise TypeError("Styled cannot be None")

        result = OrderedDict()
        fieldValues = self.getValues(encoded=encoded, styled=styled)

        for iMessage, message in enumerate(self.messages):
            result[message] = fieldValues[iMessage]

        return result

    # def getMessagesWithValue(self, value):
    #     """Computes and returns the messages that have a specified value
    #     in the current field.

    #     >>> from netzob.all import *
    #     >>> messages = [RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['netzob', 'zoby', 'lapy'] for city in ['Paris', 'Berlin', 'New-York']]
    #     >>> f1 = Field("hello ", name="hello")
    #     >>> f2 = Field(["netzob", "zoby", "lapy", "sygus"], name="pseudo")
    #     >>> f3 = Field(", what's up in ", name="whatsup")
    #     >>> f4 = Field(["Paris", "Berlin", "New-York"], name="city")
    #     >>> f5 = Field(" ?", name="end")
    #     >>> symbol = Symbol([f1, f2, f3, f4, f5], messages=messages)
    #     >>> print(symbol.specialize())
    #     >>> print(symbol)
    #     hello  | netzob | , what's up in  | Paris    |  ?
    #     hello  | netzob | , what's up in  | Berlin   |  ?
    #     hello  | netzob | , what's up in  | New-York |  ?
    #     hello  | zoby   | , what's up in  | Paris    |  ?
    #     hello  | zoby   | , what's up in  | Berlin   |  ?
    #     hello  | zoby   | , what's up in  | New-York |  ?
    #     hello  | lapy   | , what's up in  | Paris    |  ?
    #     hello  | lapy   | , what's up in  | Berlin   |  ?
    #     hello  | lapy   | , what's up in  | New-York |  ?
    #     >>> lapySymbol = Symbol(messages=symbol.fields[1].getMessagesWithValue("lapy"))
    #     >>> print(lapySymbol)
    #     hello lapy, what's up in Paris ?   
    #     hello lapy, what's up in Berlin ?  
    #     hello lapy, what's up in New-York ?
    #     >>> Format.splitStatic(lapySymbol)
    #     >>> lapySymbol.encodingFunctions.add(TypeEncodingFunction(HexaString))
    #     >>> print(lapySymbol)
    #     68656c6c6f206c6170792c2077686174277320757020696e20 | 5061726973203f      
    #     68656c6c6f206c6170792c2077686174277320757020696e20 | 4265726c696e203f    
    #     68656c6c6f206c6170792c2077686174277320757020696e20 | 4e65772d596f726b203f

    #     :parameter value: a Raw value
    #     :type value: :class:`object`
    #     :return: a list of messages
    #     :rtype: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`
    #     """

    #     if value is None:
    #         raise TypeError("Value cannot be None")

    #     fieldValues = self.getValues(encoded=False, styled=False)
    #     result = []
    #     for i_message, message in enumerate(self.messages):
    #         if fieldValues[i_message] == value:
    #             result.append(message)
    #     return result

    @abc.abstractmethod
    def specialize(self, mutator=None):
        """Specialize and generate a :class:`netzob.Model.Vocabulary.Messages.RawMessage` which content
        follows the fields definitions attached to current element.

        :keyword mutator: if set, the mutator will be used to mutate the fields definitions
        :type mutator: :class:`netzob.Model.Mutators.AbstractMutator`

        :return: a generated content represented with an hexastring
        :rtype: :class:`str`
        :raises: :class:`netzob.Model.Vocabulary.AbstractField.GenerationException` if an error occurs while generating a message
        """
        return

    @staticmethod
    def abstract(data, fields):
        """Search in the fields/symbols the first one that can abstract the data.

        >>> from netzob.all import *
        >>> messages = ["{0}, what's up in {1} ?".format(pseudo, city) for pseudo in ['netzob', 'zoby'] for city in ['Paris', 'Berlin']]

        >>> f1a = Field("netzob")
        >>> f2a = Field(", what's up in ")
        >>> f3a = Field(Alt(["Paris", "Berlin"]))
        >>> f4a = Field(" ?")
        >>> s1 = Symbol([f1a, f2a, f3a, f4a], name="Symbol-netzob")

        >>> f1b = Field("zoby")
        >>> f2b = Field(", what's up in ")
        >>> f3b = Field(Alt(["Paris", "Berlin"]))
        >>> f4b = Field(" ?")
        >>> s2 = Symbol([f1b, f2b, f3b, f4b], name="Symbol-zoby")

        >>> for m in messages:
        ...    abstractedSymbol = AbstractField.abstract(m, [s1, s2])
        ...    print(abstractedSymbol.name)
        Symbol-netzob
        Symbol-netzob
        Symbol-zoby
        Symbol-zoby

        :parameter data: the data that should be abstracted in symbol
        :type data: :class:`str`
        :parameter fields: a list of fields/symbols targeted during the abstraction process
        :type fields: :class:`list` of :class:`netzob.Model.Vocabulary.AbstractField`

        :return: a field/symbol
        :rtype: :class:`netzob.Model.Vocabulary.AbstractField`
        :raises: :class:`netzob.Model.Vocabulary.AbstractField.AbstractionException` if an error occurs while abstracting the data
        """
        from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
        for field in fields:
            try:                
                DataAlignment.align([data], field, encoded=False)
                return field
            except:
                pass

        from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol
        from netzob.Model.Vocabulary.Messages.RawMessage import RawMessage
        unknown_symbol = UnknownSymbol(RawMessage(data))
        logging.error("Impossible to abstract the message in one of the specified symbols, we create an unknown symbol for it: '%s'", unknown_symbol)

        return unknown_symbol

    def getSymbol(self):
        """Computes the symbol to which this field is attached.

        To retrieve it, this method recursively call the parent of the current object until the root is found.
        If the last root is not a :class:`netzob.Model.Vocabulary.Symbol`, it raises an Exception.

        :returns: the symbol if available
        :type: :class:`netzob.Model.Vocabulary.Symbol`
        :raises: :class:`netzob.Model.Vocabulary.AbstractField.NoSymbolException`
        """
        from netzob.Model.Vocabulary.Symbol import Symbol
        if isinstance(self, Symbol):
            return self
        elif self.hasParent():
            return self.parent.getSymbol()
        else:
            raise NoSymbolException("Impossible to retrieve the symbol attached to this element")

    def _getLeafFields(self, depth=None, currentDepth=0):
        """Extract the leaf fields to consider regarding the specified depth

        >>> from netzob.all import *
        >>> field = Field("hello", name="F0")
        >>> print([f.name for f in field._getLeafFields()])
        ['F0']

        >>> field = Field(name="L0")
        >>> headerField = Field(name="L0_header")
        >>> payloadField = Field(name="L0_payload")
        >>> footerField = Field(name="L0_footer")

        >>> fieldL1 = Field(name="L1")
        >>> fieldL1_header = Field(name="L1_header")
        >>> fieldL1_payload = Field(name="L1_payload")
        >>> fieldL1.fields = [fieldL1_header, fieldL1_payload]

        >>> payloadField.fields = [fieldL1]
        >>> field.fields = [headerField, payloadField, footerField]

        >>> print([f.name for f in field._getLeafFields(depth=None)])
        ['L0_header', 'L1_header', 'L1_payload', 'L0_footer']

        >>> print([f.name for f in field._getLeafFields(depth=0)])
        ['L0']

        >>> print([f.name for f in field._getLeafFields(depth=1)])
        ['L0_header', 'L0_payload', 'L0_footer']

        >>> print([f.name for f in field._getLeafFields(depth=2)])
        ['L0_header', 'L1', 'L0_footer']

        :return: the list of leaf fields
        :rtype: :class:`list` of :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`.
        """
        if currentDepth is None:
            currentDepth = 0

        if len(self.fields) == 0:
            return [self]

        if currentDepth == depth:
            return [self]

        leafFields = []
        for fields in self.fields:
            if fields is not None:
                leafFields.extend(fields._getLeafFields(depth, currentDepth + 1))

        return leafFields

    def hasParent(self):
        """Computes if the current element has a parent.

        :returns: True if current element has a parent.
        :rtype: :class:`bool`
        """
        return self.__parent is not None

    def clearFields(self):
        """Remove all the children attached to the current element"""

        while(len(self.__fields) > 0):
            self.__fields.pop()

    def clearEncodingFunctions(self):
        """Remove all the encoding functions attached to the current element"""
        self.__encodingFunctions.clear()
        for child in self.fields:
            child.clearEncodingFunctions()

    def clearVisualizationFunctions(self):
        """Remove all the visualization functions attached to the current element"""

        while(len(self.__visualizationFunctions) > 0):
            self.__visualizationFunctions.pop()

    def clearTransformationFunctions(self):
        """Remove all the transformation functions attached to the current element"""

        while(len(self.__transformationFunctions) > 0):
            self.__transformationFunctions.pop()

    # Standard methods
    def __str__(self):
        result = self.getCells(encoded=True)
        return str(result)

    @typeCheck(int)
    def _str_debug(self, deepness=0):
        """Returns a string which denotes
        the current field definition using a tree display"""

        tab = ["|--  " for x in range(deepness)]
        tab.append(str(self.name))
        lines = [''.join(tab)]
        from netzob.Model.Vocabulary.Field import Field
        if isinstance(self, Field):
            lines.append(self.domain._str_debug(deepness + 1))
        for f in self.fields:
            lines.append(f._str_debug(deepness + 1))
        return '\n'.join(lines)

    # PROPERTIES

    @property
    def id(self):
        """Unique identifier of the field.

        This value must be a unique UUID instance (generated with uuid.uuid4()).

        :type: :class:`uuid.UUID`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, id):
        if id is None:
            raise ValueError("id is Mandatory.")
        self.__id = id

    @property
    def name(self):
        """Public name (may not be unique), default value is None

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        self.__name = name


    @property
    def layer(self):
        """Flag describing if element is a layer.

        :type: :class:`bool`
        :raises: :class:`TypeError`
        """

        return self.__layer

    @layer.setter
    @typeCheck(bool)
    def layer(self, layer):
        if layer is None:
            layer = False
        self.__layer = layer

    @property
    def description(self):
        """User description of the field. Default value is ''.

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__description

    @description.setter
    @typeCheck(str)
    def description(self, description):
        self.__description = description

    @property
    def encodingFunctions(self):
        """Sorted typed list of encoding function to attach on field.

        .. note:: list implemented as a :class:`netzob.Common.Utils.TypedList.TypedList`

        :type: a list of :class:`netzob.Model.Vocabulary.Functions.EncodingFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """
        return self.__encodingFunctions

    @encodingFunctions.setter
    def encodingFunctions(self, encodingFunctions):
        self.clearEncodingFunctions()
        for encodingFunction in encodingFunctions:
            self.addEncodingFunction(encodingFunction)

    def addEncodingFunction(self, encodingFunction):
        self.encodingFunctions.add(encodingFunction)
        for child in self.fields:
            child.addEncodingFunction(encodingFunction)

    @property
    def visualizationFunctions(self):
        """Sorted list of visualization function to attach on field.

        :type: a list of :class:`netzob.Model.Vocabulary.Functions.VisualizationFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__visualizationFunctions

    @visualizationFunctions.setter
    def visualizationFunctions(self, visualizationFunctions):
        self.clearVisualizationFunctions()
        self.visualizationFunctions.extend(visualizationFunctions)

    @property
    def transformationFunctions(self):
        """Sorted list of transformation function to attach on field.

        :type: a list of :class:`netzob.Model.Vocabulary.Functions.TransformationFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__transformationFunctions

    @transformationFunctions.setter
    def transformationFunctions(self, transformationFunctions):
        self.clearTransformationFunctions()
        self.transformationFunctions.extend(transformationFunctions)

    @property
    def fields(self):
        """Sorted list of field fields."""

        return self.__fields

    @fields.setter
    def fields(self, fields):
        from netzob.Model.Vocabulary.Field import Field
        # First it checks the specified children are abstractfiled
        if fields is not None:
            for c in fields:
                if not isinstance(c, Field):
                    raise TypeError("Cannot edit the fields because at least one specified element is not an AbstractField its a {0}.".format(type(c)))

        self.clearFields()
        if fields is not None:
            for c in fields:
                c.parent = self
                self.__fields.append(c)

    @property
    def parent(self):
        """The parent of this current element.

        If current element has no parent, its value is **None**.

        :type: a :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :raises: :class:`TypeError`
        """

        return self.__parent

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, AbstractField):
            raise TypeError("Specified parent must be an AbstractField and not an {0}".format(type(parent)))
        self.__parent = parent

    def storeInMemento(self):
        pass

    def restoreFromMemento(self, memento):
        pass

