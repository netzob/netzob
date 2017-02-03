# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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
# | Standard library imports
# +---------------------------------------------------------------------------+
import multiprocessing
import time
from collections import OrderedDict

# +---------------------------------------------------------------------------+
# | Local application imports
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment
from netzob.Common.Utils.MatrixList import MatrixList


def _executeDataAlignment(arg, **kwargs):
    """Wrapper used to parallelize the DataAlignment using
    a pool of threads.
    """
    data = arg[0]
    field = arg[1]
    encoded = arg[2]
    alignedData = DataAlignment.align([data], field, encoded=encoded)
    return (data, alignedData)


@NetzobLogger
class ParallelDataAlignment(object):
    """Allows to align specified datas given a common field definition
    in parallel way.

    >>> from netzob.all import *
    >>> import random
    >>> import time
    >>> import logging

    >>> # Temporary raise log level of certain impacting loggers on alignment process
    >>> old_logging_level = logging.getLogger(Symbol.__name__).level
    >>> logging.getLogger(Data.__name__).setLevel(logging.INFO)
    >>> logging.getLogger(DataAlignment.__name__).setLevel(logging.INFO)

    >>> # Create 1000 data which follows format : 'hello '+random number of 5 to 10 digits+', welcome'.
    >>> # Compare the duration of their alignment with 1 and automatic threads computation
    >>> data = ['hello {0}, welcome to {1}'.format(''.join([str(random.randint(0,9)) for y in range(0, random.randint(5,10))]),''.join([str(random.randint(0,9)) for y in range(0, random.randint(10,20))])) for x in range(0, 1000)]
    >>> # Now we create a symbol with its field structure to represent this type of message
    >>> fields = [Field('hello '), Field(ASCII(nbChars=(5,10))), Field(', welcome to '), Field(ASCII(nbChars=(10,20)))]
    >>> symbol = Symbol(fields=fields)
    >>> # apply the symbol on the data using the ParallelDataAligment (single thread)
    >>> pAlignment = ParallelDataAlignment(field=symbol, depth=None, nbThread=1)
    >>> start = time.time()
    >>> alignedData = pAlignment.execute(data)
    >>> end = time.time()
    >>> oneThreadDuration = end-start
    >>> print(len(alignedData))
    1000
    >>> pAlignment = ParallelDataAlignment(field=symbol, depth=None)
    >>> start = time.time()
    >>> alignedData = pAlignment.execute(data)
    >>> end = time.time()
    >>> autoThreadDuration = end-start
    >>> print(len(alignedData))
    1000
    >>> autoThreadDuration <= oneThreadDuration
    True

    >>> # Reset log level of certain impacting loggers on alignment process
    >>> logging.getLogger(Data.__name__).setLevel(old_logging_level)
    >>> logging.getLogger(DataAlignment.__name__).setLevel(old_logging_level)


    """

    def __init__(self, field, depth=None, nbThread=None, encoded=False, styled=False):
        """Constructor.

        :param field: the format definition that will be user
        :type field: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :keyword depth: the limit in depth in the format (use None for not limit)
        :type depth: :class:`int`
        :keyword nbThread: the maximum number of thread that will be used.
        :type nbThread: :class:`int`
        :keyword encoded: indicates if the result should be encoded following field definition
        :type encoded: :class:`bool`
        :keyword styled: indicated if the result visualization filter should be applied
        :type styled: :class:`bool`

        """

        self.field = field

        self.depth = depth
        self.nbThread = nbThread
        self.encoded = encoded
        self.styled = styled

    def __collectResults_cb(self, tupple_result):
        """This callback is executed by each thread when it finishes
        to align data. Every thread submit its results using these callback.
        :param data: the data to align
        :type data: :class:`str`
        :param result: the result of an alignment
        :type result: :class:`list`
        :raise Exception: if the parameter is not valid
        """
        if tupple_result is None:
            raise TypeError("parameter cannot be none")

        for (data, result) in tupple_result:
            if data is None:
                raise TypeError("data cannot be None")

            if result is None:
                raise TypeError("result cannot be none")

            self.asyncResult[data] = result

    @typeCheck(list)
    def execute(self, data):
        """Execute the parallel alignment on the specified list of data

        :param data: the list of data that will be aligned
        :type data: a :class:`list` of data to align
        :return: a list of aligned data sorted in order to respect the provided order of data.
        :rtype: a :class:`netzob.Common.Utils.MatrixList.MatrixList`
        """

        # Create a list of data removed from duplicate entry
        noDuplicateData = list(set(data))

        # Async result host just aligned data under form [(data, alignedData)]
        self.asyncResult = OrderedDict()

        # Measure start time
        start = time.time()

        # Create a pool of 'nbThead' threads (process)
        pool = multiprocessing.Pool(self.nbThread)

        # Execute Data Alignment
        pool.map_async(_executeDataAlignment, list(zip(noDuplicateData, [self.field] * len(noDuplicateData), [self.encoded] * len(noDuplicateData), [self.styled] * len(noDuplicateData))), callback=self.__collectResults_cb)

        # Waits all alignment tasks finish
        pool.close()
        pool.join()

        # Measure end time
        end = time.time()

        # create a Matrix List based on aligned data and requested data
        result = MatrixList()
        if len(data) > 0:
            result.headers = self.asyncResult[data[0]].headers

    
        for d in data:
            if d not in list(self.asyncResult.keys()):
                raise Exception("At least one data ({0}) has not been successfully computed by the alignment".format(repr(d)))
            result.extend(self.asyncResult[d])

        # check the number of computed alignment
        if len(result) != len(data):
            raise Exception("There are not the same number of alignment ({0}) than the number of data ({1})".format(len(result), len(data)))

        self._logger.debug("Alignment of {0} data took {1}s with {2} threads.".format(len(data), end - start, self.nbThread))
        return result

    # Static method
    @staticmethod
    def align(data, field, depth=None, nbThread=None, encoded=False, styled=False):
        """Execute an alignment of specified data with provided field.
        The alignment will be perfomed in parallel
        Data must be provided as a list of hexastring.

        :param data: the data to align as a list of hexastring
        :type data: :class:`list`
        :param field : the field to consider when aligning
        :type: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :keyword depth: maximum field depth to consider (similar to layer depth)
        :type depth: :class:`int`.
        :keyword nbThread: the number of thread to use when parallelizing
        :type nbThread: :class:`int`.
        :keyword encoded: indicates if the result should be encoded following field definition
        :type encoded: :class:`bool`
        :keyword styled: indicated if the result visualization filter should be applied
        :type styled: :class:`bool`

        :return: the aligned data
        :rtype: :class:`netzob.Common.Utils.MatrixList.MatrixList`
        """
        pAlignment = ParallelDataAlignment(field, depth, nbThread, encoded, styled)
        return pAlignment.execute(data)

    # Properties

    @property
    def field(self):
        """The field that contains the definition domain used
        to align data

        :type: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        """
        return self.__field

    @field.setter
    @typeCheck(AbstractField)
    def field(self, field):
        if field is None:
            raise TypeError("Field cannot be None")
        self.__field = field

    @property
    def depth(self):
        """The depth represents the maximum deepness in the fields definition
        that will be considered when aligning messages.

        If set to None, its no limit.

        :type: :class:`int`
        """
        return self.__depth

    @depth.setter
    @typeCheck(int)
    def depth(self, depth):
        if depth is not None and depth < 0:
            raise ValueError("Depth cannot be <0, use None to specify unlimited depth")

        self.__depth = depth

    @property
    def nbThread(self):
        """The nbThread represents the maximum number of trhead that will be started
        in the same time to compute the alignment.

        If set to None, the number of thread will be automaticaly set to 2 times the number
        of available cpu.

        :type: :class:`int`
        """
        return self.__nbThread

    @nbThread.setter
    @typeCheck(int)
    def nbThread(self, nbThread):
        if nbThread is None:
            nbThread = multiprocessing.cpu_count()

        if nbThread < 0:
            raise ValueError("NbThread cannot be <0, use None to specify you don't know.")

        self.__nbThread = nbThread

    @property
    def encoded(self):
        """The encoded defines if it applies the encoding filters on aligned data

        :type: :class:`bool`
        """
        return self.__encoded

    @encoded.setter
    @typeCheck(bool)
    def encoded(self, encoded):
        if encoded is None:
            raise ValueError("Encoded cannot be None")

        self.__encoded = encoded

    @property
    def styled(self):
        """The styled defines if it applies the visu filters on aligned data

        :type: :class:`bool`
        """
        return self.__styled

    @styled.setter
    @typeCheck(bool)
    def styled(self, styled):
        if styled is None:
            raise ValueError("Styled cannot be None")

        self.__styled = styled

