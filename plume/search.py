# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import codecs
import os
import sys

from plume import DATA_DIR, FILE_PREFIX
from plume.backend import get_document, get_documents_list, get_file_path, get_history
from whoosh import index as Index, query, sorting
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import SchemaClass, DATETIME, ID, KEYWORD, NUMERIC, TEXT
from whoosh.qparser import MultifieldParser


class Schema(SchemaClass):
    path = TEXT(stored=True)
    date = DATETIME(stored=True)
    revision = NUMERIC(stored=True)
    author = ID(stored=True)
    content = TEXT(stored=True, analyzer=StemmingAnalyzer())
    tags = KEYWORD


def index_documents(init=False):
    dir_path = os.path.join(DATA_DIR, 'index')

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        init = True

    if init:
        index = Index.create_in(dir_path, schema=Schema)
    else:
        index = Index.open_dir(dir_path)

    writer = index.writer()

    # Get list of indexed documents
    if not init:
        searcher = index.searcher()
        indexed = set()

        for fields in searcher.all_stored_fields():
            args = (fields['path'], fields['revision'])

            if not os.path.exists(get_file_path(*args)):
                writer.delete_by_query(query.NestedParent(query.Term('path', args[0]), query.Term('revision', args[1])))
            else:
                indexed.add(args)

    # Index new documents
    for path in get_documents_list():
        path = unicode(path)

        try:
            for date, rev, author, desc in get_history(path):
                if not init and (path, rev) in indexed:
                    continue

                if not path.startswith(FILE_PREFIX):
                    meta, content = get_document(path, rev)[2:]
                else:
                    meta, content = None, u''

                writer.add_document(path=path,
                    date=date,
                    author=unicode(author),
                    revision=rev,
                    tags=meta.get('tags', []) if meta else [],
                    content=content,
                )
        except:
            sys.stderr.write("Error: can't index %s\n" % path)

    writer.commit(optimize=True)

    return True


def search_documents(filter):
    results = None

    # Check for existing index
    dir_path = os.path.join(DATA_DIR, 'index')

    if not os.path.exists(dir_path) or not Index.exists_in(dir_path):
        return None

    index = Index.open_dir(dir_path)

    if filter.startswith('tags:'):
        fields = ['tags']
        filter = filter[5:]
    else:
        fields = ['path', 'content']

    parser = MultifieldParser(fields, schema=index.schema)
    search_query = parser.parse(unicode(filter))

    # Try documents search
    try:
        searcher = index.searcher(closereader=False)

        return searcher.search(search_query,
            collapse=[sorting.FieldFacet('path'), sorting.FieldFacet('content')],
            collapse_order=sorting.FieldFacet('revision', reverse=True),
            sortedby=[sorting.FieldFacet('path'), sorting.FieldFacet('date', reverse=True)]
        )
    finally:
        searcher.close()

    return results
