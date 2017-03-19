# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id$
# =============================================================================
#             $URL$
# $LastChangedDate$
#             $Rev$
#   $LastChangedBy$
# =============================================================================
# Copyright (C) 2006 Ufsoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
#
# Copyright (C) 2007 Unfinished Software, UfSoft.org
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#  3. The name of the author may not be used to endorse or promote
#     products derived from this software without specific prior
#     written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# =============================================================================

from xml.parsers import expat

__all__ = ['extract_glade']

class ParseError(Exception):
    pass

class GladeParser(object):

    def __init__(self, source):
        self.source = source

        parser = expat.ParserCreate()
        parser.buffer_text = True
        parser.returns_unicode = True
        parser.ordered_attributes = True
        parser.StartElementHandler = self._handle_start
        parser.EndElementHandler = self._handle_end
        parser.CharacterDataHandler = self._handle_data

        if not hasattr(parser, 'CurrentLineNumber'):
            self._getpos = self._getpos_unknown

        self.expat = parser
        self._queue = []
        self._comments = []
        self._translate = False
        self._data = []

    def parse(self):
        try:
            bufsize = 4 * 1024 # 4K
            done = False
            while not done and len(self._queue) == 0:
                data = self.source.read(bufsize)
                if data == '': # end of data
                    if hasattr(self, 'expat'):
                        self.expat.Parse('', True)
                        del self.expat # get rid of circular references
                    done = True
                else:
                    if isinstance(data, str):
                        data = data.encode('utf-8')
                    self.expat.Parse(data, False)
                for event in self._queue:
                    yield event
                self._queue = []
                if done:
                    break
        except expat.ExpatError as e:
            raise ParseError(str(e))

    def _handle_start(self, tag, attrib):
        if 'translatable' in attrib:
            if attrib[attrib.index('translatable')+1] == 'yes':
                self._translate = True
                if 'comments' in attrib:
                    self._comments.append(attrib[attrib.index('comments')+1])

    def _handle_end(self, tag):
        if self._translate is True:
            if self._data:
                self._enqueue(tag, self._data, self._comments)
            self._translate = False
            self._data = []
            self._comments = []

    def _handle_data(self, text):
        if self._translate:
            if not text.startswith('gtk-'):
                self._data.append(text)
            else:
                self._translate = False
                self._data = []
                self._comments = []

    def _enqueue(self, kind, data=None, comments=None, pos=None):
        if pos is None:
            pos = self._getpos()
        if kind in ('property', 'property', 'col', 'col', 'item', 'item'):
            if '\n' in data:
                lines = data.splitlines()
                lineno = pos[0] - len(lines) + 1
                offset = -1
            else:
                lineno = pos[0]
                offset = pos[1] - len(data)
            pos = (lineno, offset)
            self._queue.append((data, comments, pos[0]))

    def _getpos(self):
        return (self.expat.CurrentLineNumber,
                self.expat.CurrentColumnNumber)
    def _getpos_unknown(self):
        return (-1, -1)


def extract_glade(fileobj, keywords, comment_tags, options):
    parser = GladeParser(fileobj)
    for message, comments, lineno in parser.parse():
        yield (lineno, None, message, comment_tags and comments or [])
