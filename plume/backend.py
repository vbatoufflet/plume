# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import codecs
import os
import time

from datetime import datetime
from mimetypes import guess_type
from numbers import Number
from plume import DOCUMENT_DIR, FILE_PREFIX, HELP_DIR
from plume.exception import *
from plume.utils import decode_path, encode_path, stream_file


def append_history(path, *args):
    if not path:
        raise EmptyDocumentPath()

    # Get document directory path
    dir_path = os.path.join(DOCUMENT_DIR, encode_path(path))

    # Write new history entry
    args = list(args)
    args.insert(0, int(time.time()))

    codecs.open(os.path.join(dir_path, 'meta'), 'a', 'utf-8').write('\x00'.join([str(x) for x in args]) + '\n')


def check_mimetype(path, file_name):
    return path.startswith(FILE_PREFIX) and guess_type(path)[0] == guess_type(file_name)[0]


def get_document(path, rev=None, preview=False):
    if not path:
        raise EmptyDocumentPath()
    elif rev and not isinstance(rev, Number) and not rev.isdigit():
        raise InvalidRevisionNumber(errmsg="expected digits and value is '%s'" % rev)

    file_path = get_file_path(path, rev=rev)

    # Return document data
    if not os.path.exists(file_path):
        raise DocumentNotFound()

    if path.startswith(FILE_PREFIX):
        mimetype = guess_type(path)[0]
        result = [mimetype if mimetype else 'application/octet-stream', stream_file(file_path) if not preview else True]
    else:
        result = ['text/plain', codecs.open(file_path, 'r', 'utf-8').read()]

    result.insert(1, os.path.getsize(file_path))

    return tuple(result)


def get_documents_list(filter=None):
    return [decode_path(x) for x in os.listdir(DOCUMENT_DIR)
        if os.path.isdir(os.path.join(DOCUMENT_DIR, x)) and (not filter or filter.lower() in x.lower())]


def get_help(path):
    # Get help file path
    file_path = os.path.join(HELP_DIR, path + '.md')

    if os.path.exists(file_path):
        content = codecs.open(file_path, 'r', 'utf-8').read()
    else:
        content = None

    return 'text/plain', len(content), content


def get_last_revision(path):
    if not path:
        raise EmptyDocumentPath()

    # Get document directory path
    dir_path = os.path.join(DOCUMENT_DIR, encode_path(path), 'rev')

    if not os.path.exists(dir_path):
        return 0

    return max([int(x) for x in os.listdir(dir_path) if x.isdigit()])


def get_file_path(path, rev=None):
    if not path:
        raise EmptyDocumentPath()
    elif rev and not isinstance(rev, Number) and not rev.isdigit():
        raise InvalidRevisionNumber(errmsg="expected digits and value is '%s'" % rev)

    # Get document directory path
    dir_path = os.path.join(DOCUMENT_DIR, encode_path(path))

    # Set revision to document's last if not specified
    if not rev:
        rev = get_last_revision(path)

    return os.path.join(dir_path, 'rev', str(rev))


def get_history(path, rev=None):
    if not path:
        raise EmptyDocumentPath()
    elif rev and not isinstance(rev, Number) and not rev.isdigit():
        raise InvalidRevisionNumber(errmsg="expected digits and value is '%s'" % rev)

    if rev:
        rev = int(rev)

    # Get document directory path
    dir_path = os.path.join(DOCUMENT_DIR, encode_path(path))

    if not os.path.exists(dir_path):
        raise DocumentNotFound()

    # Get revision history
    history = []

    for line in codecs.open(os.path.join(dir_path, 'meta'), 'r', 'utf-8'):
        chunks = line.strip().split('\x00')
        chunks[0] = datetime.utcfromtimestamp(float(chunks[0]))
        chunks[1] = int(chunks[1])

        if rev is None or rev == -1:
            history.append(chunks)
        elif chunks[1] == rev:
            return chunks

    history.reverse()

    return history[0] if rev == -1 else history


def lock_document(path, lock_info, unlock=False, force=False):
    if not path:
        raise EmptyDocumentPath()
    elif not lock_info[0]:
        raise EmptyUserName()

    # Get document directory path
    dir_path = os.path.join(DOCUMENT_DIR, encode_path(path))

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Get document lock path
    lock_path = os.path.join(dir_path, 'lock')

    if os.path.lexists(lock_path):
        current = os.readlink(lock_path).split('@')

        if not force and (current[0] != lock_info[0] or current[1] != lock_info[1]):
            return (current[0], datetime.utcfromtimestamp(os.lstat(lock_path).st_ctime))

        os.unlink(lock_path)

        # Remove directory if empty (creation aborted)
        if unlock and not os.path.exists(os.path.join(dir_path, 'rev')):
            os.rmdir(dir_path)

    if not unlock:
        os.symlink('%s@%s' % lock_info, lock_path)

    return None


def move_document(path_from, path_to):
    if not path_from or not path_to:
        raise EmptyDocumentPath()

    # Get documents paths
    dir_from = os.path.join(DOCUMENT_DIR, encode_path(path_from))
    dir_to = os.path.join(DOCUMENT_DIR, encode_path(path_to))

    if os.path.exists(dir_to):
        raise DocumentAlreadyExists()

    os.rename(dir_from, dir_to)


def save_document(path, data, **kwargs):
    if not kwargs.get('user'):
        raise EmptyUserName()

    rev_new = get_last_revision(path) + 1

    file_path = get_file_path(path, rev_new)

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # Append history entry
    append_history(path, *(rev_new, kwargs.get('user'), kwargs.get('desc', '-')))

    # Save document data
    if path.startswith(FILE_PREFIX):
        open(file_path, 'wb').write(data)
    else:
        codecs.open(file_path, 'w', 'utf-8').write(data)
