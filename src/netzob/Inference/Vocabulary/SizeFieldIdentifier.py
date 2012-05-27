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

#+----------------------------------------------
#| Global Imports
#+----------------------------------------------
import logging
import struct

#+----------------------------------------------
#| Local Imports
#+----------------------------------------------
from netzob.Common.Type.TypeConvertor import TypeConvertor


#+----------------------------------------------
#| SizeFieldIdentifier:
#|     Search for size fields among provided symbols
#+----------------------------------------------
class SizeFieldIdentifier(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self):
        self.inProgress = False

    def estimateDurationOfSearch(self, symbols):
        duration = 0
        # len(symbol.getFields())

        return duration

    def updateProgressBar(self, message, increase):
        if increase:
            pass
        else:
            pass
        logging.debug("message : {0}".format(message))

    def search(self, symbols):
        self.results = []
        self.inProgress = True
        logging.debug("Start the identification of size fields among {0} symbols".format(str(len(symbols))))
        # Search in each symbol
        for symbol in symbols:
            self.updateProgressBar("Working on symbol {0}".format(symbol.getName()), False)
            self.searchInSymbol(symbol)
            self.updateProgressBar(None, True)

    def searchInSymbol(self, symbol):
        # First we verify there are at least 2 fields :)
        if len(symbol.getFields()) <= 1:
            return

        iField = 0
        # We cover each field for a potential size field
        for field in symbol.getFields():
            if field.isStatic():  # Means the element is static, so we assume it's not a good candidate
                iField += 1
                continue
            cellsSize = symbol.getCellsByField(field)
            j = 0
            # We cover each field and aggregate them for a potential payload
            while j < len(symbol.getFields()):
                # Initialize the aggregate of messages from fieldJ to fieldK
                aggregateCellsData = []
                for l in range(len(cellsSize)):
                    aggregateCellsData.append("")

                # Fill the aggregate of messages and try to compare its length with the current expected length
                k = j
                while k < len(symbol.getFields()):
                    if k != j:
                        for l in range(len(cellsSize)):
                            aggregateCellsData[l] += symbol.getCellsByField(symbol.getFieldByIndex(k))[l]

                    # We try to aggregate the successive right sub-parts of j if it's a static column (TODO: handle dynamic column / TODO: handle left subparts of the K column)
                    if symbol.getFieldByIndex(j).isStatic():
                        lenJ = len(symbol.getFieldByIndex(j).getRegex())
                        stop = 0
                    else:
                        lenJ = 2
                        stop = 0

                    for m in range(lenJ, stop, -2):
                        for n in [4, 2, 1]:  # loop over different possible encoding of size field
                            res = True
                            for nbMsg in range(len(cellsSize)):
                                if symbol.getFieldByIndex(j).isStatic():
                                    targetData = symbol.getFieldByIndex(j).getRegex()[lenJ - m:] + aggregateCellsData[nbMsg]
                                else:
                                    targetData = symbol.getCellsByField(symbol.getFieldByIndex(j))[nbMsg] + aggregateCellsData[nbMsg]

                                # Handle big and little endian for size field of 1, 2 and 4 octets length
                                rawMsgSize = TypeConvertor.netzobRawToPythonRaw(cellsSize[nbMsg][:n * 2])
                                if len(rawMsgSize) == 1:
                                    expectedSizeType = "B"
                                elif len(rawMsgSize) == 2:
                                    expectedSizeType = "H"
                                elif len(rawMsgSize) == 4:
                                    expectedSizeType = "I"
                                else:  # Do not consider size field with len > 4
                                    res = False
                                    break
                                (expectedSizeLE,) = struct.unpack("<" + expectedSizeType, rawMsgSize)
                                (expectedSizeBE,) = struct.unpack(">" + expectedSizeType, rawMsgSize)
                                if (expectedSizeLE != len(targetData) / 2) and (expectedSizeBE != len(targetData) / 2):
                                    res = False
                                    break
                            if res:
                                if symbol.getFieldByIndex(j).isStatic():  # Means the regex j element is static and a sub-part is concerned
                                    self.results.append([iField, n * 2, j, lenJ - m, k, -1, "Found potential size field (col " + str(iField) + "[:" + str(n * 2) + "]) for an aggregation of data field (col " + str(j) + "[" + str(lenJ - m) + ":] to col " + str(k) + ")"])
                                else:
                                    self.results.append([iField, n * 2, j, -1, k, -1, "Found potential size field (col " + str(iField) + "[:" + str(n * 2) + "]) for an aggregation of data field (col " + str(j) + " to col " + str(k) + ")"])
                                break
                    k += 1
                j += 1
            iField += 1

    def getResults(self):
        return self.results

    def cancel(self):
        self.inProgress = True
