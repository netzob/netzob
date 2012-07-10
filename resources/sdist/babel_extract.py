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
                    if isinstance(data, unicode):
                        data = data.encode('utf-8')
                    self.expat.Parse(data, False)
                for event in self._queue:
                    yield event
                self._queue = []
                if done:
                    break
        except expat.ExpatError, e:
            raise ParseError(str(e))

    def _handle_start(self, tag, attrib):
        if u'translatable' in attrib:
            if attrib[attrib.index(u'translatable')+1] == u'yes':
                self._translate = True
                if u'comments' in attrib:
                    self._comments.append(attrib[attrib.index(u'comments')+1])

    def _handle_end(self, tag):
        if self._translate is True:
            if self._data:
                self._enqueue(tag, self._data, self._comments)
            self._translate = False
            self._data = []
            self._comments = []

    def _handle_data(self, text):
        if self._translate:
            if not text.startswith(u'gtk-'):
                self._data.append(text)
            else:
                self._translate = False
                self._data = []
                self._comments = []

    def _enqueue(self, kind, data=None, comments=None, pos=None):
        if pos is None:
            pos = self._getpos()
        if kind in (u'property', 'property'):
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
