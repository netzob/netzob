# -*- coding: utf-8 -*-

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
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Common.Utils.TypedList import TypedList
from netzob.Model.Vocabulary.ApplicativeData import ApplicativeData
from netzob.Model.Vocabulary.AbstractField import AbstractField


@NetzobLogger
class Session(object):
    """A session includes messages exchanged in the same session. Messages
    are automaticaly sorted.
    Applicative data can be attached to sessions.


    >>> import time
    >>> from netzob.all import *
    >>> # we create 3 messages
    >>> msg1 = RawMessage("ACK", source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:45:05", "%d %b %y %H:%M:%S")))
    >>> msg2 = RawMessage("SYN", source="A", destination="B", date=time.mktime(time.strptime("9 Aug 13 10:45:01", "%d %b %y %H:%M:%S")))
    >>> msg3 = RawMessage("SYN/ACK", source="B", destination="A", date=time.mktime(time.strptime("9 Aug 13 10:45:03", "%d %b %y %H:%M:%S")))
    >>> session = Session([msg1, msg2, msg3])
    >>> print(session.messages.values()[0].data)
    SYN
    >>> print(session.messages.values()[1].data)
    SYN/ACK
    >>> print(session.messages.values()[2].data)
    ACK

    """

    def __init__(self, messages=None, _id=None, applicativeData=None, name="Session"):
        """
        :parameter messages: the messages exchanged in the current session
        :type data: a list of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        :parameter _id: the unique identifier of the session
        :type _id: :class:`uuid.UUID`
        :keyword applicativeData: a list of :class:`netzob.Model.Vocabulary.ApplicaticeData.ApplicativeData`
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
        self.name = name

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

        :type: a :class:`netzob.Common.Utils.TypedList.TypedList` of :class:`netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage`
        """
        return self.__messages

    def clearMessages(self):
        """Delete all the messages attached to the current session"""
        for msg in list(self.__messages.values()):
            msg.session = None

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
        for message in messages:
            self.__messages.add(message)
            message.session = self

    @property
    def applicativeData(self):
        """Applicative data attached to the current session.

        >>> from netzob.all import *
        >>> appData = ApplicativeData("test", Integer(20))
        >>> session = Session(applicativeData=[appData])
        >>> print(len(session.applicativeData))
        1
        >>> appData2 = ApplicativeData("test2", ASCII("helloworld"))
        >>> session.applicativeData.append(appData2)
        >>> print(len(session.applicativeData))
        2
        >>> print(session.applicativeData[0])
        Applicative Data: test=Integer=20 ((8, 8)))
        >>> print(session.applicativeData[1])
        Applicative Data: test2=ASCII=helloworld ((0, 80)))

        :type: a list of :class:`netzob.Model.Vocabulary.ApplicativeData.ApplicativeData`.
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

    @property
    def name(self):
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, _name):
        if _name is None:
            raise TypeError("Name cannot be None")
        self.__name = _name

    def getEndpointsList(self):
        """Retrieve all the endpoints couples that are present in the
        session.

        >>> from netzob.all import *
        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="C")
        >>> session = Session([msg1, msg2, msg3])
        >>> print(len(session.getEndpointsList()))
        2
        >>> print(session.getEndpointsList())
        [('A', 'B'), ('A', 'C')]

        :return: a list containing couple of endpoints (src, dst).
        :rtype: a :class:`list`

        """

        endpointsList = []
        for message in list(self.messages.values()):
            src = message.source
            dst = message.destination
            endpoints1 = (src, dst)
            endpoints2 = (dst, src)
            if (not endpoints1 in endpointsList) and (not endpoints2 in endpointsList):
                endpointsList.append(endpoints1)
        return endpointsList

    def getTrueSessions(self):
        """Retrieve the true sessions embedded in the current
        session. A session is here characterized by a uniq endpoints
        couple.

        TODO: a more precise solution would be to use flow
        reconstruction (as in TCP).

        >>> from netzob.all import *
        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="C")
        >>> session = Session([msg1, msg2, msg3])
        >>> print(len(session.getTrueSessions()))
        2
        >>> for trueSession in session.getTrueSessions():
        ...    print(trueSession.name)
        Session: 'A' - 'B'
        Session: 'A' - 'C'

        :return: a list containing true sessions embedded in the current session.
        :rtype: a :class:`list`

        """

        trueSessions = []
        for endpoints in self.getEndpointsList():
            trueSessionMessages = []
            src = None
            dst = None
            for message in list(self.messages.values()):
                if message.source in endpoints and message.destination in endpoints:
                    trueSessionMessages.append(message)
                    if src is None:
                        src = message.source
                    if dst is None:
                        dst = message.destination
            trueSession = Session(messages=trueSessionMessages, applicativeData=self.applicativeData, name="Session: '" + str(src) + "' - '" + str(dst) + "'")
            trueSessions.append(trueSession)
        return trueSessions

    def isTrueSession(self):
        """Tell if the current session is true. A session is said to
        be true if the communication flow pertain to a uniq
        applicative session between a couple of endpoints.

        >>> from netzob.all import *
        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> session = Session([msg1, msg2, msg3])
        >>> print(session.isTrueSession())
        True

        :return: a boolean telling if the current session is a true one (i.e. it corresponds to a uniq applicative session between two endpoints).
        :rtype: a :class:`bool`

        """

        if len(self.getTrueSessions()) == 1:
            return True
        else:
            return False

    @typeCheck(list)
    def abstract(self, symbolList):
        """This method abstract each message of the current session
        into symbols according to a list of symbols given as
        parameter.

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(ASCII("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(ASCII("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(ASCII("ACK"))], name="Symbol_ACK")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")

        >>> session = Session([msg1, msg2, msg3])
        >>> if session.isTrueSession():
        ...    for src, dst, sym in session.abstract(symbolList):
        ...        print(str(src) + " - " + str(dst) + " : " + str(sym.name))
        A - B : Symbol_SYN
        B - A : Symbol_SYNACK
        A - B : Symbol_ACK

        :return: a list of tuples containing the following elements : (source, destination, symbol).
        :rtype: a :class:`list`

        """

        abstractSession = []
        if not self.isTrueSession():
            self._logger.warn("The current session cannot be abstracted as it not a true session (i.e. it may contain inner true sessions).")
            return abstractSession
        for message in list(self.messages.values()):
            symbol = AbstractField.abstract(message.data, symbolList)
            abstractSession.append((message.source, message.destination, symbol))
        return abstractSession

