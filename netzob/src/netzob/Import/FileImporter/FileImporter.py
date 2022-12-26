# -*- coding: utf-8 -*-

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
#| Standard library imports
#+---------------------------------------------------------------------------+
import errno

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Utils.SortedTypedList import SortedTypedList
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Messages.FileMessage import FileMessage
from netzob.Common.NetzobException import NetzobImportException

@NetzobLogger
class FileImporter(object):
    r"""An Importer than can extracts messages out of files.
    We recommend using static methods such as
    - FileImporter.readFiles(...)
    - Fileimporter.readFile(...)
    refer to their documentation to have an overview of the required parameters.

    >>> from netzob.all import *
    >>> messages = FileImporter.readFile("./test/resources/files/test_import_text_message.txt").values()
    >>> len(messages)
    13
    >>> for m in messages:
    ...    print(repr(m.data))
    b'The life that I have'
    b'Is all that I have'
    b'And the life that I have'
    b'Is yours.'
    b'The love that I have'
    b'Of the life that I have'
    b'Is yours and yours and yours.'
    b'A sleep I shall have'
    b'A rest I shall have'
    b'Yet death will be but a pause.'
    b'For the peace of my years'
    b'In the long green grass'
    b'Will be yours and yours and yours.'

    >>> from netzob.all import *
    >>> file1 = "./test/resources/files/test_import_raw_message1.dat"
    >>> file2 = "./test/resources/files/test_import_raw_message2.dat"
    >>> messages = FileImporter.readFiles([file1, file2], delimitor=b"\x00\x00").values()
    >>> len(messages)
    802
    >>> messages[10].data
    b'\xbdq75\x18'
    >>> messages[797].data
    b'\xfcJ\xd1\xbf\xff\xd90\x98m\xeb'
    >>> messages[797].file_path
    './test/resources/files/test_import_raw_message2.dat'
    >>> messages[707].file_message_number
    353
    """

    def __init__(self):
        pass

    @typeCheck(list, bytes)
    def readMessages(self, filePathList, delimitor=b"\n"):
        """Read all the messages found in the specified filePathList and given a delimitor.

        :param filePathList: paths of the file to parse
        :type filePathList: a list of :class:`str`
        :param delimitor: the delimitor used to find messages in the same file
        :type delimitor: :class:`str`
        :return: a sorted list of messages
        :rtype: a :class:`SortedTypedList <netzob.Common.Utils.SortedTypedList.SortedTypedList>` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """
        # Verify the existence of input files
        errorMessageList = []
        for filePath in filePathList:
            try:
                fp = open(filePath)
                fp.close()
            except IOError as e:
                errorMessage = _("Error while trying to open the " +
                                 "file {0}.").format(filePath)
                if e.errno == errno.EACCES:
                    errorMessage = _("Error while trying to open the file " +
                                     "{0}, more permissions are required for "
                                     + "reading it.").format(filePath)
                errorMessageList.append(errorMessage)
                self._logger.warn(errorMessage)

        if errorMessageList != []:
            raise NetzobImportException("File", "\n".join(errorMessageList))
                
        self.messages = SortedTypedList(AbstractMessage)
        for filePath in filePathList:
            self.__readMessagesFromFile(filePath, delimitor)
        
        return self.messages
    
    @typeCheck(str, bytes)
    def __readMessagesFromFile(self, filePath, delimitor=b'\n'):
        if filePath is None or len(str(filePath).strip()) == 0:
            raise TypeError("Filepath cannot be None or empty")
 
        if delimitor is None or len(str(delimitor)) == 0:
            raise TypeError("Delimitor cannot be None or empty")

        file_content = None
        with open(filePath, 'rb') as fd:
            file_content = fd.read()

        if file_content is None:
            raise Exception("No content found in '{}'".format(filePath))

        for i_data, data in enumerate(file_content.split(delimitor)):
            if len(data) > 0:
                self.messages.add(FileMessage(data, file_path = filePath, file_message_number = i_data))

    @staticmethod
    @typeCheck(list, bytes)
    def readFiles(filePathList, delimitor=b'\n'):
        """Read all messages from a list of files. A delimitor must be specified to delimit messages.

        :param filePathList: a list of files to read
        :type filePathList: a list of :class:`str`
        :param delimitor: the delimitor.
        :type delimitor: :class:`str`
        :return: a list of captured messages
        :rtype: a :class:`SortedTypedList <netzob.Common.Utils.SortedTypedList.SortedTypedList>` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """
        importer = FileImporter()
        return importer.readMessages(filePathList, delimitor = delimitor)
    
    @staticmethod
    @typeCheck(str, bytes)
    def readFile(filePath, delimitor=b'\n'):
        """Read all messages from the specified file. 
        Messages are found based on the specified delimitor. 

        :param filePath: the pcap path
        :type filePath: :class:`str`
        :param delimitor: the delimitor used to find messages in the specified file
        :type delimitor: :class:`str`
        :return: a list of captured messages
        :rtype: a :class:`SortedTypedList <netzob.Common.Utils.SortedTypedList.SortedTypedList>` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage>`
        """
        importer = FileImporter()        
        return importer.readFiles([filePath], delimitor = delimitor)
