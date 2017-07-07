# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2012 AMOSSYS                                                |
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
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
from io import StringIO


class CodeBuffer(StringIO):
    """
    StringIO class with indentation capabilities
    Used to write indent-based blocks of code (Python, LUA...)

    Use like this:
    > buffer = CodeBuffer()
    > buffer << "rabbits eats"
    > with buffer.new_block("carrots, but also"):
    >   buffer << "hay,"
    >   buffer << "vegetables,"
    >   buffer << "and grass."
    > print buffer
    < rabbits eats
    < carrots, but also
    <   hay,
    <   vegetables,
    <   and grass.
    """
    INDENT_SIZE = 2

    def __init__(self, *args, **kwargs):
        StringIO.__init__(self, *args, **kwargs)
        self._stack = [self.new_block()]

    def __lshift__(self, elm):
        self._stack[-1].write(elm)
        return self

    def enter(self, elm):
        self._stack.append(elm)

    def exit(self):
        self._stack.pop()

    def write(self, s):
        indent_s = ' ' * ((len(self._stack) - 1) * self.INDENT_SIZE) + s + '\n'
        StringIO.write(self, indent_s)

    def new_block(self, data=None):
        cb = CodeBlock(self)
        if data is not None:
            self << data
        return cb


class LUACodeBuffer(CodeBuffer):
    def exit(self):
        self << "end"
        CodeBuffer.exit(self)


class CodeBlock(object):
    def __init__(self, buf):
        self._buf = buf

    def __enter__(self):
        return self._buf.enter(self)

    def __exit__(self, exception, data, tb):
        self._buf.exit()

    def write(self, data):
        self._buf.write(data)
