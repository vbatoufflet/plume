# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import codecs
import os.path
import re

from difflib import HtmlDiff
from flask.ext.babel import _
from jinja2 import Markup, escape
from misaka import EXT_AUTOLINK, EXT_FENCED_CODE, EXT_STRIKETHROUGH, EXT_SUPERSCRIPT, EXT_TABLES, HTML_HARD_WRAP, \
    HTML_SKIP_HTML, HTML_TOC, HtmlRenderer, HtmlTocRenderer, Markdown, SmartyPants
from plume import FILE_PREFIX, HTMLDIFF_TAB_SIZE, HTMLDIFF_WRAP_COLUMN
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class PlumeRenderer(HtmlRenderer, SmartyPants):
    def block_code(self, text, lang):
        if not lang:
            return Markup('\n<pre>%s</pre>\n' % escape(text.strip()))

        return highlight(text, get_lexer_by_name(lang, stripall=True), HtmlFormatter())

    def image(self, src, title, alt=''):
        if src.lstrip('/').startswith(FILE_PREFIX):
            new_src = src + ('?' if not '?' in src else '&') + 'do=source'

            return Markup('<a href="%s"><img src="%s" alt="%s"%s /></a>' %
                (src, new_src, alt if alt else '', ' title="%s"' % title if title else ''))
        else:
            return super(PlumeRenderer, self).image(src, title, alt)

    def paragraph(self, text):
        class_name = None

        if text.lstrip().startswith('(?) '):
            class_name = 'msginfo'
        elif text.lstrip().startswith('/!\\ '):
            class_name = 'msgwarn'
        elif text.lstrip().startswith('(!) '):
            class_name = 'msgerror'

        if class_name:
            text = text[4:]

        return Markup('\n<p%s>%s</p>\n' % (' class="%s"' % class_name if class_name else '', text.strip()))


def render_diff(file_from, file_to):
    output = HtmlDiff(tabsize=HTMLDIFF_TAB_SIZE, wrapcolumn=HTMLDIFF_WRAP_COLUMN).make_table(
        codecs.open(file_from, 'r', 'utf-8'),
        codecs.open(file_to, 'r', 'utf-8'),
        _('Revision %d' % int(os.path.basename(file_from))),
        _('Revision %d' % int(os.path.basename(file_to))),
        context=True,
    )

    return re.sub(r'\s*cellspacing="0" cellpadding="0" rules="groups"\s*>', '>', output)


def render_document(data, toc=False):
    # Strip meta if any
    if data.startswith('---'):
        data = data[data.find('---', 3) + 3:]

    # Render Markdown document (removing user-inputted HTML)
    renderer = (HtmlTocRenderer if toc else PlumeRenderer)(flags=HTML_HARD_WRAP | HTML_SKIP_HTML | HTML_TOC)

    markdown = Markdown(renderer, extensions=EXT_AUTOLINK | EXT_FENCED_CODE | EXT_STRIKETHROUGH | EXT_SUPERSCRIPT |
        EXT_TABLES)

    return markdown.render(data)
