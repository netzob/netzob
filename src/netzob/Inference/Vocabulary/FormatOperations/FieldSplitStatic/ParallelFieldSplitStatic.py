
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
#| Standard library imports
#+---------------------------------------------------------------------------+
import multiprocessing
import time

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.DataAlignment.DataAlignment import DataAlignment


def _executeDataAlignment(arg, **kwargs):
    """Wrapper used to parallelize the DataAlignment using
    a pool of threads.
    """
    data = arg[0]
    field = arg[1]
    alignedData = DataAlignment.align([data], field)
    return (data, alignedData)


@NetzobLogger
class ParallelFieldSplitStatic(object):
    """Allows to split the content of the specified field following
    its value variation over its messages.
    """

    def __init__(self, field, unitSize=AbstractType.UNITSIZE_4, nbThread=None):
        """Constructor.

        :param field : the field to consider when spliting
        :type: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :keyword unitSize: the required size of static element to create a static field
        :type unitSize: :class:`int`.
        :keyword nbThread: the number of thread to use when spliting
        :type nbThread: :class:`int`.
        """

        self.field = field

        self.unitSize = unitSize
        self.nbThread = nbThread

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
    def execute(self):
        """Execute the parallel splitting
        """
        pass
        # # Create a list of data removed from duplicate entry
        # noDuplicateData = list(set(data))

        # # Measure start time
        # start = time.time()

        # # Create a pool of 'nbThead' threads (process)
        # pool = multiprocessing.Pool(self.nbThread)

        # # Execute Data Alignment
        # pool.map_async(_executeSplitStatic, data, callback=self.__collectResults_cb)

        # # Waits all alignment tasks finish
        # pool.close()
        # pool.join()

        # # Measure end time
        # end = time.time()

    # Static method
    @staticmethod
    def split(field, unitSize=None, nbThread=None):
        """Split the portion of message in the current field
        following the value variation every unitSize

        :param field : the field to consider when spliting
        :type: :class:`netzob.Model.Vocabulary.AbstractField.AbstractField`
        :keyword unitSize: the required size of static element to create a static field
        :type unitSize: :class:`int`.
        :keyword nbThread: the number of thread to use when spliting
        :type nbThread: :class:`int`.
        """
        pSplit = ParallelFieldSplitStatic(field, unitSize, nbThread)
        return pSplit.execute()

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
