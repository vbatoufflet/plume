# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

from __main__ import subparsers
from plume.search import index_documents


def index_update(args):
    print('Indexing documents...')

    if index_documents(init=args.drop):
        print('OK')


subparser = subparsers.add_parser('index', help='update documents index')
subparser.set_defaults(func=index_update)
subparser.add_argument('-d', '--drop', action='store_true', help='drop existing index')
