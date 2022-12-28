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
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import abc
from collections import OrderedDict
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Common.Utils.UndoRedo.AbstractMementoCreator import AbstractMementoCreator
from netzob.Model.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Model.Vocabulary.Functions.VisualizationFunction import VisualizationFunction
from netzob.Model.Vocabulary.Functions.TransformationFunction import TransformationFunction
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Common.Utils.MessageCells import MessageCells


class InvalidVariableException(Exception):
    """This exception is raised when the variable behing the definition
    a field domain (and structure) is not valid. The variable definition
    is upgraded everytime the domain is modified.
    """


class AlignmentException(Exception):
    pass


class NoSymbolException(Exception):
    pass


class GenerationException(Exception):
    pass


@public_api
class AbstractionException(Exception):
    pass


@NetzobLogger
class AbstractField(AbstractMementoCreator, metaclass=abc.ABCMeta):
    """Represents all the different classes which participates in field definitions of a message format."""

    def __init__(self, name=None):
        self.name = name
        self.description = ""

        self.__fields = TypedList(AbstractField)
        self.__parent = None

        self.__encodingFunctions = SortedTypedList(EncodingFunction)
        self.__visualizationFunctions = TypedList(VisualizationFunction)
        self.__transformationFunctions = TypedList(TransformationFunction)

        self._variable = None
        self.__preset = None

    @abc.abstractmethod
    def copy(self, map_objects=None):
        """Copy the current object as well as all its dependencies. This
        method returns a new object of the same type.

        """
        raise NotImplementedError("Method copy() is not implemented")

    @typeCheck(bool, bool, bool)
    def getCells(self, encoded=True, styled=True, transposed=False):
        """Returns a matrix with a different line for each messages attached to the symbol of the current element.

        The matrix includes a different column for each leaf children of the current element.
        In each cell, the slices of messages once aligned.
        Attached :class:`EncodingFunction` can also be considered if parameter encoded is set to True.
        In addition, visualizationFunctions are also applied if parameter styled is set to True.
        If parameter Transposed is set to True, the matrix is built with rows for fields and columns for messages.

        >>> from netzob.all import *
        >>> messages = [RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['john', 'kurt', 'lapy'] for city in ['Paris', 'Berlin', 'New-York']]
        >>> fh1 = Field(String("hello "), name="hello")
        >>> fh2 = Field(Alt([String("john"), String("kurt"), String("lapy"), String("sygus")]), name="pseudo")
        >>> fheader = Field(name="header")
        >>> fheader.fields = [fh1, fh2]
        >>> fb1 = Field(String(", what's up in "), name="whatsup")
        >>> fb2 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> fb3 = Field(" ?", name="end")
        >>> fbody = Field(name="body")
        >>> fbody.fields = [fb1, fb2, fb3]
        >>> symbol = Symbol([fheader, fbody], messages=messages)

        >>> print(symbol.str_data())
        hello    | pseudo | whatsup           | city       | end 
        -------- | ------ | ----------------- | ---------- | ----
        'hello ' | 'john' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'john' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'john' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'New-York' | ' ?'
        -------- | ------ | ----------------- | ---------- | ----

        >>> fh1.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> fb2.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        hello          | pseudo | whatsup           | city               | end 
        -------------- | ------ | ----------------- | ------------------ | ----
        '68656c6c6f20' | 'john' | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'john' | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'john' | ", what's up in " | '4e65772d596f726b' | ' ?'
        '68656c6c6f20' | 'kurt' | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'kurt' | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'kurt' | ", what's up in " | '4e65772d596f726b' | ' ?'
        '68656c6c6f20' | 'lapy' | ", what's up in " | '5061726973'       | ' ?'
        '68656c6c6f20' | 'lapy' | ", what's up in " | '4265726c696e'     | ' ?'
        '68656c6c6f20' | 'lapy' | ", what's up in " | '4e65772d596f726b' | ' ?'
        -------------- | ------ | ----------------- | ------------------ | ----

        >>> print(fheader.getCells()) 
        Field          | Field 
        -------------- | ------
        '68656c6c6f20' | 'john'
        '68656c6c6f20' | 'john'
        '68656c6c6f20' | 'john'
        '68656c6c6f20' | 'kurt'
        '68656c6c6f20' | 'kurt'
        '68656c6c6f20' | 'kurt'
        '68656c6c6f20' | 'lapy'
        '68656c6c6f20' | 'lapy'
        '68656c6c6f20' | 'lapy'
        -------------- | ------

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
        ------
        'john'
        'john'
        'john'
        'kurt'
        'kurt'
        'kurt'
        'lapy'
        'lapy'
        'lapy'
        ------

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

        :keyword encoded: if set to True, encoding functions are applied to returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied to returned cells
        :type styled: :class:`bool`
        :keyword transposed: is set to True, the returned matrix is transposed (1 line for each field)
        :type transposed: :class:`bool`

        :return: a matrix representing the aligned messages following field definitions.
        :rtype: a :class:`MatrixList <netzob.Common.Utils.MatrixList.MatrixList>`
        :raises: :class:`AlignmentException <netzob.Model.Vocabulary.AbstractField.AlignmentException>` if an error occurs while aligning messages
        """

        if len(self.messages) < 1:
            raise ValueError("This symbol/field does not contain any RawMessage, therefore you cannot call __str__() on it to display the messages content.")

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
        >>> messages = [RawMessage("hello {0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['john', 'kurt', 'lapy'] for city in ['Paris', 'Berlin', 'New-York']]
        >>> f1 = Field("hello ", name="hello")
        >>> f2 = Field(["john", "kurt", "lapy", "sygus"], name="pseudo")
        >>> f3 = Field(", what's up in ", name="whatsup")
        >>> f4 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f5 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4, f5], messages=messages)
        >>> print(symbol.str_data())
        hello    | pseudo | whatsup           | city       | end 
        -------- | ------ | ----------------- | ---------- | ----
        'hello ' | 'john' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'john' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'john' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'kurt' | ", what's up in " | 'New-York' | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'Paris'    | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'Berlin'   | ' ?'
        'hello ' | 'lapy' | ", what's up in " | 'New-York' | ' ?'
        -------- | ------ | ----------------- | ---------- | ----

        >>> symbol.addEncodingFunction(TypeEncodingFunction(HexaString))
        >>> print(symbol.str_data())
        hello          | pseudo     | whatsup                          | city               | end   
        -------------- | ---------- | -------------------------------- | ------------------ | ------
        '68656c6c6f20' | '6a6f686e' | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '6a6f686e' | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '6a6f686e' | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        '68656c6c6f20' | '6b757274' | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '6b757274' | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '6b757274' | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        '68656c6c6f20' | '6c617079' | '2c2077686174277320757020696e20' | '5061726973'       | '203f'
        '68656c6c6f20' | '6c617079' | '2c2077686174277320757020696e20' | '4265726c696e'     | '203f'
        '68656c6c6f20' | '6c617079' | '2c2077686174277320757020696e20' | '4e65772d596f726b' | '203f'
        -------------- | ---------- | -------------------------------- | ------------------ | ------

        >>> print(symbol.getValues())
        [b'68656c6c6f206a6f686e2c2077686174277320757020696e205061726973203f', b'68656c6c6f206a6f686e2c2077686174277320757020696e204265726c696e203f', b'68656c6c6f206a6f686e2c2077686174277320757020696e204e65772d596f726b203f', b'68656c6c6f206b7572742c2077686174277320757020696e205061726973203f', b'68656c6c6f206b7572742c2077686174277320757020696e204265726c696e203f', b'68656c6c6f206b7572742c2077686174277320757020696e204e65772d596f726b203f', b'68656c6c6f206c6170792c2077686174277320757020696e205061726973203f', b'68656c6c6f206c6170792c2077686174277320757020696e204265726c696e203f', b'68656c6c6f206c6170792c2077686174277320757020696e204e65772d596f726b203f']
        >>> print(f1.getValues())
        [b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20', b'68656c6c6f20']
        >>> print(f2.getValues())
        [b'6a6f686e', b'6a6f686e', b'6a6f686e', b'6b757274', b'6b757274', b'6b757274', b'6c617079', b'6c617079', b'6c617079']
        >>> print(f3.getValues())
        [b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20', b'2c2077686174277320757020696e20']
        >>> print(f4.getValues())
        [b'5061726973', b'4265726c696e', b'4e65772d596f726b', b'5061726973', b'4265726c696e', b'4e65772d596f726b', b'5061726973', b'4265726c696e', b'4e65772d596f726b']
        >>> print(f5.getValues())
        [b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f', b'203f']

        :keyword encoded: if set to True, encoding functions are applied to returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied to returned cells
        :type styled: :class:`bool`

        :return: a list detailling all the values current element takes.
        :rtype: a :class:`list` of :class:`str`
        :raises: :class:`AlignmentException <netzob.Model.Vocabulary.AbstractField.AlignmentException>` if an error occurs while aligning messages
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
        >>> messages = [RawMessage("{0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['john', 'kurt'] for city in ['Paris', 'Berlin']]
        >>> f1 = Field(["john", "kurt", "lapy", "sygus"], name="pseudo")
        >>> f2 = Field(", what's up in ", name="whatsup")
        >>> f3 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f4 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> print(symbol.str_data())
        pseudo | whatsup           | city     | end 
        ------ | ----------------- | -------- | ----
        'john' | ", what's up in " | 'Paris'  | ' ?'
        'john' | ", what's up in " | 'Berlin' | ' ?'
        'kurt' | ", what's up in " | 'Paris'  | ' ?'
        'kurt' | ", what's up in " | 'Berlin' | ' ?'
        ------ | ----------------- | -------- | ----

        >>> messageCells = symbol.getMessageCells()
        >>> for message in symbol.messages:
        ...    print(message.data, messageCells[message])
        john, what's up in Paris ? [b'john', b", what's up in ", b'Paris', b' ?']
        john, what's up in Berlin ? [b'john', b", what's up in ", b'Berlin', b' ?']
        kurt, what's up in Paris ? [b'kurt', b", what's up in ", b'Paris', b' ?']
        kurt, what's up in Berlin ? [b'kurt', b", what's up in ", b'Berlin', b' ?']

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

        fieldCells = self.getCells(encoded=encoded, styled=styled)
        result = MessageCells()

        leaf_fields = self.getLeafFields()
        result.fields = leaf_fields
        
        for iMessage, message in enumerate(self.messages):
            result[message] = fieldCells[iMessage]
        return result

    @typeCheck(bool, bool)
    def getMessageValues(self, encoded=False, styled=False):
        """Computes and returns the alignment of each message belonging to
        the current field as proposed by getValues() method but indexed
        per message.

        >>> from netzob.all import *
        >>> messages = [RawMessage("{0}, what's up in {1} ?".format(pseudo, city)) for pseudo in ['john', 'kurt'] for city in ['Paris', 'Berlin']]
        >>> f1 = Field(["john", "kurt", "lapy", "sygus"], name="pseudo")
        >>> f2 = Field(", what's up in ", name="whatsup")
        >>> f3 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f4 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> print(symbol.str_data())
        pseudo | whatsup           | city     | end 
        ------ | ----------------- | -------- | ----
        'john' | ", what's up in " | 'Paris'  | ' ?'
        'john' | ", what's up in " | 'Berlin' | ' ?'
        'kurt' | ", what's up in " | 'Paris'  | ' ?'
        'kurt' | ", what's up in " | 'Berlin' | ' ?'
        ------ | ----------------- | -------- | ----

        >>> messageValues = f3.getMessageValues()
        >>> for message in symbol.messages:
        ...    print(message.data, messageValues[message])
        john, what's up in Paris ? b'Paris'
        john, what's up in Berlin ? b'Berlin'
        kurt, what's up in Paris ? b'Paris'
        kurt, what's up in Berlin ? b'Berlin'

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

    @abc.abstractmethod
    def specialize(self):
        """Specialize and generate a :class:`bytes` object which content
        follows the field definitions attached to current element.

        :return: The produced content after the specializion process.
        :rtype: :class:`bytes`
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while generating a message
        """
        return

    @public_api
    def abstract(self, data, preset=None, memory=None):
        """The :meth:`abstract` method is used to abstract the given
        data bytes with the current symbol (or field) model. This method also works on fields, in order to abstract a :class:`bytes` into a field object.

        Similarly to the :meth:`specialize` method, it is possible to
        indicate a Preset configuration that will be used to check
        content parsed for specific fields. However, for the
        :meth:`abstract` method, it is only possible to specify field
        names for keys of the Preset configuration. The reason of this
        restriction is that the :meth:`abstract` method returns an
        :class:`OrderedDict` containing also field names as keys.

        The :meth:`abstract` method expects some parameters:

        :param data: The concrete message to abstract in symbol (or field).
        :param preset: The configuration used to check values in symbol (or field) structure obtained after message parsing.
        :param memory: A memory used to store variable values during
                       specialization and abstraction of sequence of symbols (or fields).
                       The default value is None.
        :type data: :class:`bytes`, required
        :type preset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`, optional
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`, optional
        :return: The structure of the parsed data.
        :rtype: An :class:`OrderedDict` where keys are :class:`str` and values are :class:`bytes`
        :raises: :class:`AbstractionException <netzob.Model.Vocabulary.AbstractField.AbstractionException>` if an error occurs while abstracting the data


        .. note::
           When using the :meth:`abstract` method, it is
           important to explicitly name all the fields with different
           names, because the resulting OrderedDict will use field
           names as its keys.


        **Abstracting data into a field**

        The following code shows an example of abstracting a data
        according to a field definition:

        >>> from netzob.all import *
        >>> messages = ["john, what's up in {} ?".format(city)
        ...             for city in ['Paris', 'Berlin']]
        >>>
        >>> f1a = Field(name="name", domain="john")
        >>> f2a = Field(name="question", domain=", what's up in ")
        >>> f3a = Field(name="city", domain=Alt(["Paris", "Berlin"]))
        >>> f4a = Field(name="mark", domain=" ?")
        >>> f = Field([f1a, f2a, f3a, f4a], name="field-john")
        >>>
        >>> for m in messages:
        ...    structured_data = f.abstract(m)
        ...    print(structured_data)
        OrderedDict([('name', b'john'), ('question', b", what's up in "), ('city', b'Paris'), ('mark', b' ?')])
        OrderedDict([('name', b'john'), ('question', b", what's up in "), ('city', b'Berlin'), ('mark', b' ?')])


        **Abstracting data into a symbol**

        The following code shows an example of abstracting a data
        according to a symbol definition:

        >>> from netzob.all import *
        >>> messages = ["john, what's up in {} ?".format(city)
        ...             for city in ['Paris', 'Berlin']]
        >>>
        >>> f1a = Field(name="name", domain="john")
        >>> f2a = Field(name="question", domain=", what's up in ")
        >>> f3a = Field(name="city", domain=Alt(["Paris", "Berlin"]))
        >>> f4a = Field(name="mark", domain=" ?")
        >>> s = Symbol([f1a, f2a, f3a, f4a], name="Symbol-john")
        >>>
        >>> for m in messages:
        ...    structured_data = s.abstract(m)
        ...    print(structured_data)
        OrderedDict([('name', b'john'), ('question', b", what's up in "), ('city', b'Paris'), ('mark', b' ?')])
        OrderedDict([('name', b'john'), ('question', b", what's up in "), ('city', b'Berlin'), ('mark', b' ?')])


        **Usage of Symbol for traffic generation and parsing**

        A Symbol class may be used to generate concrete messages according
        to its field definition, through the
        :meth:`~netzob.Model.Vocabulary.Symbol.specialize` method, and
        may also be used to abstract a concrete message into its
        associated symbol through the
        :meth:`~netzob.Model.Vocabulary.Symbol.abstract` method:

        >>> from netzob.all import *
        >>> f0 = Field("aaaa", name="f0")
        >>> f1 = Field(" # ", name="f1")
        >>> f2 = Field("bbbbbb", name="f2")
        >>> s = Symbol(fields=[f0, f1, f2])
        >>> concrete_message = next(s.specialize())
        >>> concrete_message
        b'aaaa # bbbbbb'
        >>> s.abstract(concrete_message)
        OrderedDict([('f0', b'aaaa'), ('f1', b' # '), ('f2', b'bbbbbb')])


        **Usage of Preset during message abstraction**

        The following code shows an example of abstracting a data
        according to a symbol definition and a defined Preset configuration:

        >>> from netzob.all import *
        >>>
        >>> f1 = Field(name="name", domain="john")
        >>> f2 = Field(name="question", domain=", what's up in ")
        >>> f3 = Field(name="city", domain=Alt(["Paris", "Berlin"]))
        >>> f4 = Field(name="mark", domain=" ?")
        >>> symbol = Symbol([f1, f2, f3, f4], name="Symbol-john")
        >>>
        >>> # We build a Preset configuration indicating that we expect "Paris" for the field f3
        >>> preset = Preset(symbol)
        >>> preset[f3] = b"Paris"
        >>>
        >>> data = "john, what's up in Berlin ?"
        >>> data_structure = symbol.abstract(data, preset=preset)
        Traceback (most recent call last):
        ...
        netzob.Model.Vocabulary.AbstractField.AbstractionException: With the symbol/field 'Symbol-john', can abstract the data: 'john, what's up in Berlin ?', but some parsed values do not match the expected preset.
        >>>
        >>> data = "john, what's up in Paris ?"
        >>> data_structure = symbol.abstract(data, preset=preset)
        >>>
        >>> data_structure
        OrderedDict([('name', b'john'), ('question', b", what's up in "), ('city', b'Paris'), ('mark', b' ?')])

        """

        from netzob.Model.Vocabulary.Domain.Parser.MessageParser import MessageParser, InvalidParsingPathException

        try:
            # Try to align/parse the data with the current field
            messageParser = MessageParser(memory=memory)
            alignedData = next(messageParser.parseRaw(data, self.getLeafFields()))

            # If it matches, we build a dict that contains, for each field, the associated value that was present in the message
            data_structure = OrderedDict()
            for idx, field in enumerate(self.getLeafFields()):
                data_structure[field.name] = alignedData[idx].tobytes()

            # Check that parsed data are coherent with the given preset configuration
            is_preset_ok = True
            if preset is not None:
                is_preset_ok = self.check_preset(data_structure, preset)

            if is_preset_ok:
                return data_structure
            else:
                raise AbstractionException("With the symbol/field '{}', can abstract the data: '{}', but some parsed values do not match the expected preset.".format(self, data)) from None
        except InvalidParsingPathException as e:
            raise AbstractionException("With the symbol/field '{}', cannot abstract the data: '{}'. Error: '{}'".format(self, data, e)) from None
            #logging.warn(traceback.format_exc())

    def check_preset(self, data_structure, preset):
        self._logger.debug("Checking symbol consistency regarding its expected preset, for symbol '{}'".format(self))

        if preset.symbol != self:
            raise Exception("The preset configuration is linked to the symbol '{}', but we were given the symbol '{}'".format(preset.symbol, self))

        result = True
        from netzob.Fuzzing.Mutators.DomainMutator import FuzzingMode

        for (key, key_preset) in preset.mappingFieldsMutators.items():
            field_name = key.field.name

            if field_name in data_structure.keys():
                key_mutator = key_preset

                if key_mutator.mode == FuzzingMode.FIXED:
                    expected_value = preset[key]
                    if isinstance(expected_value, bitarray):
                        expected_value = expected_value.tobytes()
                    observed_value = data_structure[field_name]

                    self._logger.debug("Checking field consistence, for field '{}'".format(field_name))
                    if expected_value == observed_value:
                        self._logger.debug("Field '{}' consistency is ok: expected value '{}' == observed value '{}'".format(field_name, expected_value, observed_value))
                    else:
                        self._logger.debug("Field '{}' consistency is not ok: expected value '{}' != observed value '{}'".format(field_name, expected_value, observed_value))
                        result = False
                        break

        if result:
            self._logger.debug("Symbol '{}' consistency is ok".format(self))
        else:
            self._logger.debug("Symbol '{}' consistency is not ok".format(self))
        return result

    @public_api
    def getSymbol(self):
        """Return the symbol to which this field is attached.

        :returns: The associated symbol if available.
        :rtype: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        :raises: :class:`NoSymbolException <netzob.Model.Vocabulary.AbstractField.NoSymbolException>`

        To retrieve the associated symbol, this method recursively
        calls the parent of the current object until the root is found.

        If the root is not a :class:`Symbol
        <netzob.Model.Vocabulary.Symbol.Symbol>`, this raises an Exception.

        The following example shows how to retrieve the parent symbol
        from a field object:

        >>> from netzob.all import *
        >>> field = Field("hello", name="F0")
        >>> symbol = Symbol([field], name="S0")
        >>> field.getSymbol()
        S0
        >>> type(field.getSymbol())
        <class 'netzob.Model.Vocabulary.Symbol.Symbol'>

        """
        from netzob.Model.Vocabulary.Symbol import Symbol
        if isinstance(self, Symbol):
            return self
        elif self.hasParent():
            return self.parent.getSymbol()
        else:
            raise NoSymbolException(
                "Impossible to retrieve the symbol attached to this element")

    def getAncestor(self):
        """Return the ancestor of the current field/symbol.
        """
        if self.hasParent():
            return self.parent.getAncestor()
        else:
            return self

    @public_api
    def getField(self, field_name):
        """Retrieve a sub-field based on its name.

        :param field_name: the name of the :class:`Field <netzob.Model.Vocabulary.Field.Field>` object
        :type field_name: :class:`str`, required
        :returns: The sub-field object.
        :rtype: :class:`Field <netzob.Model.Vocabulary.Field>`
        :raise KeyError: when the field has not been found

        The following example shows how to retrieve a sub-field based
        on its name:

        >>> from netzob.all import *
        >>> f1 = Field("hello", name="f1")
        >>> f2 = Field("hello", name="f2")
        >>> f3 = Field("hello", name="f3")
        >>> fheader = Field(name="fheader")  # create a Field named 'fheader'
        >>> fheader.fields = [f1, f2, f3] # this Field is parent of 3 existing Fields
        >>> type(fheader.getField('f2')) # get the sub-field named 'f2'
        <class 'netzob.Model.Vocabulary.Field.Field'>
        >>>
        >>> s = Symbol([f1, f2, f3])
        >>> type(s.getField('f2')) # get the field named 'f2' in the symbol
        <class 'netzob.Model.Vocabulary.Field.Field'>

        """
        for field in self.getLeafFields(includePseudoFields=True):
            if field_name == field.name:
                return field
        raise KeyError("Field '{}' has not been found in '{}'".format(field_name, self))

    def getLeafFields(self, depth=None, currentDepth=0, includePseudoFields=False):
        """Extract the leaf fields to consider, regarding the specified depth.

        >>> from netzob.all import *
        >>> field = Field("hello", name="F0")
        >>> print([f.name for f in field.getLeafFields()])
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

        >>> print([f.name for f in field.getLeafFields(depth=None)])
        ['L0_header', 'L1_header', 'L1_payload', 'L0_footer']

        >>> print([f.name for f in field.getLeafFields(depth=0)])
        ['L0']

        >>> print([f.name for f in field.getLeafFields(depth=1)])
        ['L0_header', 'L0_payload', 'L0_footer']

        >>> print([f.name for f in field.getLeafFields(depth=2)])
        ['L0_header', 'L1', 'L0_footer']

        :return: the list of leaf fields
        :rtype: :class:`list` of :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`.
        """
        if currentDepth is None:
            currentDepth = 0

        if len(self.fields) == 0:
            return [self]

        if currentDepth == depth:
            return [self]

        leafFields = []
        for fields in self.fields:

            # Handle case where the field is pseudo (meaning it does not procude concrete value)
            if fields.isPseudoField:
                if includePseudoFields:
                    pass
                else:
                    continue
            if fields is not None:
                leafFields.extend(fields.getLeafFields(depth, currentDepth + 1, includePseudoFields))

        return leafFields

    def hasParent(self):
        """Computes if the current element has a parent.

        :returns: True if current element has a parent.
        :rtype: :class:`bool`
        """
        return self.__parent is not None

    def clearFields(self):
        """Remove all the children attached to the current element"""

        while (len(self.__fields) > 0):
            self.__fields.pop()

    def clearEncodingFunctions(self):
        """Remove all the encoding functions attached to the current element"""
        self.__encodingFunctions = SortedTypedList(EncodingFunction)
        for child in self.fields:
            child.clearEncodingFunctions()

    def clearVisualizationFunctions(self):
        """Remove all the visualization functions attached to the current element"""

        while (len(self.__visualizationFunctions) > 0):
            self.__visualizationFunctions.pop()

    def clearTransformationFunctions(self):
        """Remove all the transformation functions attached to the current element"""

        while (len(self.__transformationFunctions) > 0):
            self.__transformationFunctions.pop()

    # Standard methods
    def __repr__(self):
        """Return the name of the symbol or field.

        >>> from netzob.all import *
        >>> f = Field(name="test_field")
        >>> repr(f)
        'test_field'

        """
        return self.name

    def __str__(self):
        """Return the name of the symbol or field.

        >>> from netzob.all import *
        >>> f = Field(name="test_field")
        >>> str(f)
        'test_field'

        """
        return repr(self)

    @typeCheck(int)
    def str_data(self, deepness=0):
        """Returns a string which shows the associated messages of the current
        symbol/field, after applying the symbol/field definition.

        :param deepness: Parameter used to specify th number of indentations. The default value is 0.
        :type deepness: :class:`int`, optional

        >>> from netzob.all import *
        >>> messages = []
        >>> messages.append(RawMessage("john, what's up in Paris ?"))
        >>> messages.append(RawMessage("john, what's up in Berlin ?"))
        >>> messages.append(RawMessage("kurt, what's up in Paris ?"))
        >>> messages.append(RawMessage("kurt, what's up in Berlin ?"))
        >>> f1 = Field(["john", "kurt"], name="pseudo")
        >>> f2 = Field(", what's up in ", name="whatsup")
        >>> f3 = Field(["Paris", "Berlin", "New-York"], name="city")
        >>> f4 = Field(" ?", name="end")
        >>> symbol = Symbol([f1, f2, f3, f4], messages=messages)
        >>> print(symbol.str_data())
        pseudo | whatsup           | city     | end 
        ------ | ----------------- | -------- | ----
        'john' | ", what's up in " | 'Paris'  | ' ?'
        'john' | ", what's up in " | 'Berlin' | ' ?'
        'kurt' | ", what's up in " | 'Paris'  | ' ?'
        'kurt' | ", what's up in " | 'Berlin' | ' ?'
        ------ | ----------------- | -------- | ----

        >>> print(f1.str_data())
        Field 
        ------
        'john'
        'john'
        'kurt'
        'kurt'
        ------

        """
        result = self.getCells(encoded=True)
        return str(result)

    # PROPERTIES

    @property
    def name(self):
        """Public name (may not be unique), default value is None

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__name

    @name.setter  # type: ignore
    @typeCheck(str)
    def name(self, name):
        self.__name = name

    @property
    def meta(self):
        """Meta boolean to print metadata,default is False

        :type: :class:`bool`
        :raises: :class:`TypeError`
        """

        return self.__meta

    @meta.setter
    @typeCheck(bool)
    def meta(self, meta):
        self.__meta = meta

    @property
    def description(self):
        """User description of the field. Default value is ''.

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__description

    @description.setter  # type: ignore
    @typeCheck(str)
    def description(self, description):
        self.__description = description

    @property
    def encodingFunctions(self):
        """Sorted typed list of encoding function to attach on field.

        .. note:: list implemented as a :class:`TypedList <netzob.Common.Utils.TypedList.TypedList>`

        :type: a list of :class:`EncodingFunction <netzob.Model.Vocabulary.Functions.EncodingFunction>`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """
        return self.__encodingFunctions

    @encodingFunctions.setter  # type: ignore
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

        :type: a list of :class:`VisualizationFunction <netzob.Model.Vocabulary.Functions.VisualizationFunction>`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__visualizationFunctions

    @visualizationFunctions.setter  # type: ignore
    def visualizationFunctions(self, visualizationFunctions):
        self.clearVisualizationFunctions()
        self.visualizationFunctions.extend(visualizationFunctions)

    @property
    def transformationFunctions(self):
        """Sorted list of transformation function to attach on field.

        :type: a list of :class:`TransformationFunction <netzob.Model.Vocabulary.Functions.TransformationFunction>`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__transformationFunctions

    @transformationFunctions.setter  # type: ignore
    def transformationFunctions(self, transformationFunctions):
        self.clearTransformationFunctions()
        self.transformationFunctions.extend(transformationFunctions)

    @property
    def fields(self):
        """A sorted list of sub-fields."""

        return self.__fields

    @fields.setter  # type: ignore
    def fields(self, fields):
        from netzob.Model.Vocabulary.Field import Field
        # First it checks the specified children are abstractField
        if fields is not None:
            for c in fields:
                if not isinstance(c, Field):
                    raise TypeError(
                        "Cannot edit the fields because at least one specified element is not an AbstractField; it's a {0}.".
                        format(type(c)))

        self.clearFields()
        if fields is not None:
            for c in fields:
                c.parent = self
                self.__fields.append(c)

    @property
    def parent(self):
        """The parent of this current element.

        If current element has no parent, its value is **None**.

        :type: a :class:`AbstractField <netzob.Model.Vocabulary.AbstractField.AbstractField>`
        :raises: :class:`TypeError`
        """

        return self.__parent

    @parent.setter  # type: ignore
    def parent(self, parent):
        if not isinstance(parent, AbstractField):
            raise TypeError(
                "Specified parent must be an AbstractField and not an {0}".
                format(type(parent)))
        self.__parent = parent

    @property
    def preset(self):
        """A preset configuration used for fixing values and fuzzing variables during specialization.

        :type : :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
        """
        return self.__preset

    @preset.setter  # type: ignore
    def preset(self, preset):
        self.__preset = preset

    def storeInMemento(self):
        pass

    def restoreFromMemento(self, memento):
        pass
