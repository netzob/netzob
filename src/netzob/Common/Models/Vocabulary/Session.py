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
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Common.Utils.TypedList import TypedList
from netzob.Common.Models.Vocabulary.ApplicativeData import ApplicativeData


@NetzobLogger
class Session(object):
    """A session includes messages exchanged in the same session. Messages
    are automaticaly sorted.
    Applicative data can be attached to sessions.


    >>> import time
    >>> from netzob import *
    >>> # we create 3 messages
    >>> msg1 = RawMessage("ACK", source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:45:05", "%d %b %y %H:%M:%S")))
    >>> msg2 = RawMessage("SYN", source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:45:01", "%d %b %y %H:%M:%S")))
    >>> msg3 = RawMessage("SYN/ACK", source="B", destination="A", date=time.mktime(time.strptime("9 Aug 13 10:45:03", "%d %b %y %H:%M:%S")))
    >>> session = Session([msg1, msg2, msg3])
    >>> print session.messages.values()[0]
    1376037901.0 A>>B SYN
    >>> print session.messages.values()[1]
    1376037903.0 B>>A SYN/ACK
    >>> print session.messages.values()[2]
    1376037905.0 A>>B ACK

    """

    def __init__(self, messages=None, _id=None, applicativeData=None):
        """
        :parameter messages: the messages exchanged in the current session
        :type data: a list of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :parameter _id: the unique identifier of the session
        :type _id: :class:`uuid.UUID`
        :keyword applicativeData: a list of :class:`netzob.Common.Models.Vocabulary.ApplicaticeData.ApplicativeData`
        """
        self.__messages = SortedTypedList(AbstractMessage)
        self.__applicativeData = TypedList(ApplicativeData)

        if messages is None:
            messages = []
        self.messages = messages
        if _id is None:
            _id = uuid.uuid4()
        self.id = _id
        if applicativeData is None:
            applicativeData = []
        self.applicativeData = applicativeData

    @property
    def id(self):
        """The unique identifier of the session.

        :type: :class:`uuid.UUID`
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("Id cannot be None")
        self.__id = _id

    @property
    def messages(self):
        """The messages exchanged in the current session.
        Messages are sorted.

        :type: a :class:`netzob.Common.Utils.TypedList.TypedList` of :class:`netzob.Common.Models.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        """
        return self.__messages

    def clearMessages(self):
        """Delete all the messages attached to the current session"""
        self.__messages.clear()

    @messages.setter
    def messages(self, messages):
        if messages is None:
            messages = []

        # First it checks the specified messages are all AbstractMessages
        for msg in messages:
            if not isinstance(msg, AbstractMessage):
                raise TypeError("Cannot add messages of type {0} in the session, only AbstractMessages are allowed.".format(type(msg)))

        self.clearMessages()
        self.__messages.addAll(messages)

    @property
    def applicativeData(self):
        """Applicative data attached to the current session.

        >>> from netzob import *
        >>> appData = ApplicativeData("test", Decimal, 20)
        >>> session = Session(applicativeData=[appData])
        >>> print len(session.applicativeData)
        1
        >>> appData2 = ApplicativeData("test2", ASCII, "helloworld")
        >>> session.applicativeData.append(appData2)
        >>> print len(session.applicativeData)
        2
        >>> print session.applicativeData[0]
        Applicative Data: test=20 (Decimal)
        >>> print session.applicativeData[1]
        Applicative Data: test2=helloworld (ASCII)


        :type: a list of :class:`netzob.Common.Models.Vocabulary.ApplicativeData.ApplicativeData`.
        """
        return self.__applicativeData

    def clearApplicativeData(self):
        while(len(self.__applicativeData) > 0):
            self.__applicativeData.pop()

    @applicativeData.setter
    def applicativeData(self, applicativeData):
        for app in applicativeData:
            if not isinstance(app, ApplicativeData):
                raise TypeError("Cannot add an applicative data with type {0}, only ApplicativeData accepted.".format(type(app)))
        self.clearApplicativeData()
        for app in applicativeData:
            self.applicativeData.append(app)
