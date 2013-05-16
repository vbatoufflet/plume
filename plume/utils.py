# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import os
import re
import urllib


def decode_path(path):
    return urllib.unquote_plus(re.sub(r'\(([0-9A-F]{2})\)', '%\\1', path))


def encode_path(path):
    return re.sub(r'%([0-9A-F]{2})', '(\\1)', urllib.quote_plus(path.lstrip('/') if path != '/' else path))


def get_path(request):
    return '/' + urllib.unquote_plus(request.url[len(request.url_root):])


def split_path(path):
    parts = []

    for chunk in path.split('/'):
        if not chunk:
            continue

        parts.append((chunk, os.path.join(parts[-1][1], chunk) if parts else chunk))

    return parts


def stream_file(path):
    f = open(path, 'rb')

    while True:
        block = f.read(65536)

        if not block:
            break

        yield block

    f.close()
