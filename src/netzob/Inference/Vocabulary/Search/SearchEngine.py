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
import itertools
import multiprocessing

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger, typeCheck
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Types.AbstractType import AbstractType
from netzob.Model.Types.TypeConverter import TypeConverter
from netzob.Model.Types.Raw import Raw
from netzob.Model.Types.BitArray import BitArray
from netzob.Inference.Vocabulary.Search.SearchTask import SearchTask
from netzob.Inference.Vocabulary.Search.SearchResult import SearchResult, SearchResults
from netzob.Model.Vocabulary.Functions.VisualizationFunctions.HighlightFunction import HighlightFunction


def _executeSearch(arg, **kwargs):
    """Wrapper used to parallelize the search engine using
    a pool of threads.
    """

    data = arg[0]
    message = arg[1]
    addTags = arg[2]
    dataLabels = arg[3]

    se = SearchEngine()
    c = se.searchDataInMessage(data, message, addTags=addTags, dataLabels=dataLabels)
    return c


@NetzobLogger
class SearchEngine(object):
    """This search engine is the entry point for the API of all
    the search processes. It allows to search for any type of data in messages using
    specific transformations to support the identification of hidden data.


    >>> from netzob.all import *
    >>> content = b"Netzob is a tool that helps experts in their reverse engineering processes."
    >>> m = RawMessage(content, date=1383948883.0)
    >>> searchResults = SearchEngine.searchInMessage([b"expert"], m)
    >>> searchResults.extend(SearchEngine.searchInMessage([b"reverse"], m))
    >>> print(searchResults)
    2 occurence(s) found.
    >>> for searchResult in searchResults:
    ...    print(int(searchResult.ranges[0][0]/8), int(searchResult.ranges[0][1]/8))
    28 34
    45 52
    >>> print(content.find(b'expert'), content.find(b'expert')+len(b'expert'))
    28 34
    >>> print(content.find(b'reverse'), content.find(b'reverse')+len(b'reverse'))
    45 52
    
    """

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(AbstractType, AbstractMessage, bool)
    def searchInMessage(data, message, addTags=True):
        """Search in the specified data the given data. This data will be searched as
        it but also under various format.

        :parameter data: the data to search after. This data must be provided with its netzob type.
        :type data: an :class:`netzob.Model.Types.AbstractType.AbstractType`.
        :parameter message: the message in which the search will take place
        :type message: :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        :keyword addTags: if set to True, visualization functions are added to the message to highlights found results.
        :type addTags: :class:`bool`
        :return: a search results detailling where and how occurrences where found. Occurences are also
        identified in the message through dedicated visualization functions automaticaly added to the message.
        :rtype: :class:`netzob.Inference.Vocabulary.SearchEngine.SearchResults.SearchResults`

        """
        if data is None:
            raise TypeError("Data cannot be None")
        if message is None:
            raise TypeError("Message cannot be None")

        searchEngine = SearchEngine()
        return searchEngine.searchDataInMessage(data, message, addTags)

    def __collectResults_cb(self, results):
        """This callback is executed by each thread when it finishes
        to search data. Every thread submit its results using these callback.
        :param results: the result of the search op
        :type results: :class:`list`
        :raise Exception: if the parameter is not valid
        """
        if results is None:
            raise TypeError("Internal Error: Collected None during a parallel search operation.")
        for result in results:
            self.asyncResult.extend(result)

    @typeCheck(list, list, bool, bool)
    def searchDataInMessages(self, datas, messages, addTags=True, inParallel=True, dataLabels=None):
        """Search all the data specified in the given messages. Per default, this operation is executed in parallel.

        Example of a search operation executed in sequential


        >>> from netzob.all import *
        >>> stuff = ["protocols", "communication", "games", "tools", "crypto", "people :)"]
        >>> tools = ["Netzob", "zoby", "toto", "your hand", "a knive"]
        >>> places = ["my office", "school", "your bedroom", "your car", "hell"]
        >>> msgs = [ RawMessage("Reversing {0} with {1} in {2} !".format(s, w, p).encode('utf-8')) for s in stuff for w in tools for p in places]
        >>> sData = [ ASCII("protocol"), ASCII("Reversed"), Integer(10)]
        >>> se = SearchEngine()
        >>> results = se.searchDataInMessages(sData, msgs, inParallel=False)
        >>> print(results)
        25 occurence(s) found.

        Example of a search operation executed in parallel

        >>> from netzob.all import *
        >>> stuff = [b"protocols", b"communication", b"games", b"tools", b"crypto", b"people :)"]
        >>> tools = [b"Netzob", b"zoby", b"toto", b"your hand", b"a knive"]
        >>> places = [b"my office", b"school", b"your bedroom", b"your car", b"hell"]
        >>> msgs = [ RawMessage("Reversing {0} with {1} in {2}!".format(s, w, p)) for s in stuff for w in tools for p in places]
        >>> print(len(msgs))
        150
        >>> sData = [ASCII("protocol"), ASCII("Reversed"), Integer(10)]
        >>> se = SearchEngine()
        >>> results = se.searchDataInMessages(sData, msgs, inParallel=True)
        >>> print(results)
        25 occurence(s) found.

        :parameter data: a list of data to search after. Each data must be provided with its netzob type.
        :type data: a list of :class:`netzob.Model.Types.AbstractType.AbstractType`.
        :parameter messages: the messages in which the search will take place
        :type message: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        :keyword addTags: if set to True, visualization functions are added to the message to highlights found results.
        :type addTags: :class:`bool`
        :keyword inParallel: if set to True, the search will be executed in parallel.
        :type addTags: :class:`bool`
        :keyword dataLabels: an optionnal dict to attach to each data a label to simplify search results identification
        :type dataLabels: dict

        :return: a list of search results detailling where and how occurrences where found. Occurences are also
        identified in the message through dedicated visualization functions automaticaly added to the message.
        :rtype: a list of :class:`netzob.Inference.Vocabulary.SearchEngine.SearchResults.SearchResults`

        """

        if datas is None or len(datas) == 0:
            raise TypeError("There should be at least one data to search after.")
        for data in datas:
            if not isinstance(data, AbstractType):
                raise TypeError("At least one specified data is not an AbstractType.")
        for message in messages:
            if not isinstance(message, AbstractMessage):
                raise TypeError("At least one specified message is not An AbstractMessage.")

        # Remove any duplicate data
        noDuplicateDatas = list(set(datas))

        results = SearchResults()
        if not inParallel:
            # Measure start time
            # start = time.time()

            for message in messages:
                results.extend(self.searchDataInMessage(noDuplicateDatas, message, addTags, dataLabels))
            # Measure end time
            # end = time.time()

        else:
            # Async result hosting search results
            self.asyncResult = []

            # Measure start time
            # start = time.time()

            nbThread = multiprocessing.cpu_count()

            # Create a pool of 'nbThead' threads (process)
            pool = multiprocessing.Pool(nbThread)

            # Execute search operations
            pool.map_async(_executeSearch, list(zip([noDuplicateDatas] * len(messages), messages, [addTags] * len(messages), [dataLabels] * len(messages))), callback=self.__collectResults_cb)

            # Waits all alignment tasks finish
            pool.close()
            pool.join()

            # Measure end time
            # end = time.time()

            results.extend(self.asyncResult)

        return results

    @typeCheck(list, AbstractMessage, bool)
    def searchDataInMessage(self, data, message, addTags=True, dataLabels=None):
        """Search in the specified message any of the given data. These data will be searched as
        it but also under various format.

        >>> from netzob.all import *
        >>> message = RawMessage(b"Reversing protocols with Netzob")
        >>> sData = [ASCII("protocol")]
        >>> se = SearchEngine()
        >>> results = se.searchDataInMessage(sData, message)
        >>> print(results)
        1 occurence(s) found.
        >>> for result in results:
        ...    print(result)
        ...    print(repr(result.searchTask.properties["data"]))
        Found ascii-bits(bigEndian) at [(80, 144)] of bitarray('01010010011001010111011001100101011100100111001101101001011011100110011100100000011100000111001001101111011101000110111101100011011011110110110001110011001000000111011101101001011101000110100000100000010011100110010101110100011110100110111101100010')
        protocol


        :parameter data: the data to search after. Data must be provided with their netzob type.
        :type data: a list of :class:`netzob.Model.Types.AbstractType.AbstractType`.
        :parameter message: the message in which the search will take place
        :type message: :class:`netzob.Model.Vocabulary.Messages.AbstractMessage`
        :keyword addTags: if set to True, visualization functions are added to the message to highlights found results.
        :type addTags: :class:`bool`
        :keyword dataLabels: an optionnal dict to attach to each data a label to simplify search results identification
        :type dataLabels: dict

        :return: a search results detailling where and how occurrences where found. Occurences are also
        identified in the message through dedicated visualization functions automaticaly added to the message.
        :rtype: :class:`netzob.Inference.Vocabulary.SearchEngine.SearchResults.SearchResults`

        """

        if data is None or len(data) == 0:
            raise TypeError("At least one data should be specified.")

        if message is None:
            raise TypeError("Message cannot be None")

        searchTasks = []
        for d in data:
            # normalize the given data
            normedData = AbstractType.normalize(d)

            # build search tasks
            props = dict()
            props['message'] = message
            props['data'] = d
            if dataLabels is not None and d in list(dataLabels.keys()):
                props['label'] = dataLabels[d]

            searchTasks.extend(self.__buildSearchTasks(normedData, props))

        # fetch the content of the message and convert it to bitarray
        target = TypeConverter.convert(message.data, Raw, BitArray)

        # Generate search cases
        searchCases = itertools.product([target], searchTasks)

        searchResults = self.__search(searchCases)

        # If requested, we tag the results in the message using visualization functions
        # if addTags:
        #     for searchResult in searchResults:
        #         for (startPos, endPos) in searchResult.ranges:
        #             self._logger.info("function from {} to {}".format(startPos, endPos))
        #             message.visualizationFunctions.append(HighlightFunction(startPos, endPos))
        return searchResults

    def __search(self, searchCases):
        """Execute the different search cases and build
        search results that will be returned.

        :parameter searchCases: an iterable of tupple (bitarray, :class:`netzob.Inference.Vocabulary.Search.SearchTask.SearchTask`)
        :type searchCases: a list
        :return: the obtained results
        :rtype: a list of :class:`netzob.Inference.Vocabulary.Search.SearchResult.SearchResult`

        """
        if searchCases is None:
            raise TypeError("There should be at least one search case.")

        results = SearchResults()
        for (target, searchTask) in searchCases:
            if target is None or not isinstance(target, bitarray) or searchTask is None or not isinstance(searchTask, SearchTask):
                raise TypeError("Each search case must a tupple made of a bitarray and a SearchTask instance")

            ranges = []
            for startIndex in target.search(searchTask.data):
                self._logger.debug("Search found {}: {}>{}".format(searchTask.data, startIndex, len(searchTask.data)))
                ranges.append((startIndex, startIndex + len(searchTask.data)))

            if len(ranges) > 0:
                results.append(SearchResult(target, searchTask, ranges))

        return results

    @typeCheck(AbstractType, dict)
    def __buildSearchTasks(self, data, properties=None):
        """Builds a search tasks for each possible encoding mutations of the
        specified data.

        :parameter data: the data from wich it must create search tasks
        :type data: :class:`netzob.Model.Types.AbstractType.AbstractType`
        :keyword properties: a dict of properties {name, value} to attach to each built searchTask
        :type properties: a dict
        :return: a list of search tasks
        :rtype: a :class:`list` of :class:`netzob.Inference.Vocabulary.SearchEngine.SearchTask.SearchTask`
        """
        if data is None:
            raise TypeError("The data cannot be None")

        return [SearchTask(mutation, mutationType, properties=properties) for mutationType, mutation in list(data.mutate().items())]

