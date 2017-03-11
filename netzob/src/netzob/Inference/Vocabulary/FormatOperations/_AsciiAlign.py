# - * - coding: utf-8 - * -

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
#| Global Imports
#+---------------------------------------------------------------------------+
import logging
import uuid
#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Inference.Vocabulary.Alignment.NeedlemanAndWunsch import NeedlemanAndWunsch
from netzob.Common.Symbol import Symbol
from netzob.Common.Field import Field
from netzob.Common.Type.Format import Format
from netzob.Common.Type.TypeConvertor import TypeConvertor


class AsciiAlign():
    def __init__(self,
                 project,
                 symbols,
                 explodeSymbols,
                 doInternalSlick,
                 defaultFormat,
                 unitSize,
                 cb_status=None):
        self.symbols = symbols
        self.project = project
        self.doInternalSlick = doInternalSlick
        self.cb_status = cb_status
        self.defaultFormat = defaultFormat
        self.unitSize = unitSize
        self.log = logging.getLogger(
            'netzob.Inference.Vocabulary.AsciiAlign.py')
        self.server = ""
        if explodeSymbols is False:
            self.symbols = symbols
        else:
            #Create a symbol for each message and reset to constant the tokens
            self.symbols = []
            i_symbol = 1
            for symbol in symbols:
                for m in symbol.getMessages():
                    for t in m.getPattern()[1]:
                        t.setType("constant")
                    tmpSymbol = Symbol(
                        str(uuid.uuid4()), "Symbol " + str(i_symbol), project)
                    tmpSymbol.setPattern(m.getPattern())
                    tmpSymbol.addMessage(m)
                    self.symbols.append(tmpSymbol)
                    i_symbol += 1

    def clusterByTokenization(self, symbols):
        self.ServerInference()
        ################################### Cluster messages according to their tokens
        ll = len(self.symbols) - 1
        i_equ = 0
        while (ll > 0):
            currentPattern = self.symbols[i_equ].getMessages()[0].getPattern()[
                1]
            for j in range(ll):
                jnext = len(self.symbols) - j - 1
                cond = False
                for message in self.symbols[jnext].getMessages():
                    if currentPattern == message.getPattern()[1]:
                        #                        score = sum([p1 == p2 for p1, p2 in zip(currentPattern, message.getPattern()[1])])
                        score2 = self.computeSimilarities(
                            currentPattern, message.getPattern()[1])
                        #                        if score >= min(len(currentPattern), len(message.getPattern()[1])):
                        minilength = min(
                            len(message.getData()),
                            len(self.symbols[i_equ].getMessages()[0]
                                .getData()))
                        if score2 * 2.0 / minilength >= 0.40:
                            cond = True
                        if cond:
                            break

                if (cond):
                    currentDst = self.symbols[i_equ].getPattern()[0]
                    otherDst = self.symbols[jnext].getPattern()[0]
                    if not self.server or (currentDst == otherDst) or (
                            currentDst != self.server and
                            otherDst != self.server):
                        self.mergeEffectiveRowCol(i_equ, jnext)
                        #                        self.log.debug("Merge the equal column/line {0} with the column/line {1}".format(str(i_equ), str(j + 1)))
                        i_equ -= 1
                        break
            ll -= 1
            i_equ += 1

    ################################## Align messages
        alignment = NeedlemanAndWunsch(self.unitSize, self.cb_status)
        for symbol in self.symbols:

            #            alignment.alignSymbols([symbol], self.project)
            #            symbol.getFields()[0].setFormat(Format.STRING)
            #            tmpSymbols.extend(alignment.getLastResult())
            try:
                #                print("l")
                al = self.computeAlignment(symbol)
                symbol.getField().setAlignment(al)
                alignment.buildRegexFromAlignment(symbol, al,
                                                  self.defaultFormat)

#                for (p, fields) in zip(symbol.getPattern()[1], symbol.getFields()):
#                    field.setFormat(p.getFormat())
            except:
                logging.warn(
                    "Partitionnement error: too much fields ( > 100) for the symbol '"
                    + symbol.getName() + "' len=" + str(
                        len(symbol.getExtendedFields())) + "len " + str(
                            len(symbol.getPattern()[1])))
                symbol.getField().removeLocalFields()
                field = Field("Field 0", "(.{, })", symbol)
                symbol.addLocalField(field)
                # Use the default protocol type for representation
                field.setFormat(self.defaultFormat)

        alignment.alignSymbols(self.symbols, self.project)
        self.symbols = alignment.getLastResult()

    def computeSimilarities(self, tl1, tl2):
        temp = 0
        for t1, t2 in zip(tl1, tl2):
            for s1, s2 in zip(t1.getValue(), t2.getValue()):
                temp += (s1 == s2)
        return temp

    def mergeEffectiveRowCol(self, i_maximum, j_maximum):
        # Extract symbols i and j
        if i_maximum > j_maximum:
            symbol1 = self.symbols.pop(i_maximum)
            symbol2 = self.symbols.pop(j_maximum)
        else:
            symbol1 = self.symbols.pop(j_maximum)
            symbol2 = self.symbols.pop(i_maximum)

        # Merge the symbols i and j
        messages = []
        messages.extend(symbol1.getMessages())
        messages.extend(symbol2.getMessages())

        newSymbol = Symbol(str(uuid.uuid4()), symbol1.getName(), self.project)
        newSymbol.setPattern(
            self.mergePattern(symbol1.getPattern(), symbol2.getPattern()))
        #        self.log.debug("Patterns to merge: {0} with {1}: Give Result {2}".format(symbol1.getPatternString(), symbol2.getPatternString(), newSymbol.getPatternString()))
        for message in messages:
            newSymbol.addMessage(message)

        # Append th new symbol to the "symbols" structure
        self.symbols.append(newSymbol)

    def mergePattern(self, p1, p2):
        patTemp = []
        patTemp.append(p1[0])
        patTemp2 = []
        for t1, t2 in zip(p1[1], p2[1]):

            if t1.getLength() == t2.getLength() and t1.getValue(
            ) != t2.getValue():
                t1.setType("variable")
                patTemp2.append(t1)
            elif t1.getLength() > t2.getLength():
                t1.setType("variable")
                patTemp2.append(t1)
            elif t2.getLength() > t1.getLength():
                t2.setType("variable")
                patTemp2.append(t2)
            else:
                if (t2.getType() == "variable"):
                    patTemp2.append(t2)
                else:
                    patTemp2.append(t1)

        patTemp.append(patTemp2)
        return patTemp

    def computeAlignment(self, symbol):
        #        self.log.debug("Patterns to align: {0} ".format(str(symbol.getPattern())))
        pat1 = symbol.getPattern()[1]
        align = ""
        mess = str(symbol.getMessages()[0].getData())
        pat2 = symbol.getMessages()[0].getPattern()[1]
        currentPos = 0
        for t1, t2 in zip(pat1, pat2):
            if (t1.getType() == "constant"):
                align += mess[currentPos:currentPos + t1.getLength() * 2]
            else:
                align += "-" * (t1.getLength() * 2)
            currentPos += t2.getLength() * 2
#        self.log.debug("Alignment= {0} ".format(align))
        return align

    def ServerInference(self):
        candidates = []
        score = []
        for symbol in self.symbols:
            for m in symbol.getMessages():
                dst = m.getPattern()[0]
                if dst in candidates:
                    score[candidates.index(dst)] += 1
                else:
                    candidates.append(dst)
                    score.append(1)
        print(candidates)
        if score.count(max(score)) == 1 and len(candidates) > 2:
            self.server = candidates[score.index(max(score))]

#+---------------------------------------------------------------------------+
#| Getters
#+---------------------------------------------------------------------------+

    def getLastResult(self):
        return self.symbols
