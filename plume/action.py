# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

from flask import Response, flash, redirect, render_template, request, session, url_for
from flask.ext.babel import _
from plume import ATOM_LIMIT, FILE_PREFIX, HELP_PREFIX
from plume.backend import *
from plume.exception import *
from plume.renderer import render_diff, render_document
from werkzeug.contrib.atom import AtomFeed
from werkzeug.http import http_date


def do_atom(path=None):
    feed = AtomFeed('Changes' + (' - %s' % path if path != '/' else ''), feed_url=request.url, url=request.url_root)

    history = []

    if path != '/':
        for entry in get_history(path):
            entry.insert(1, path)
            history.append(entry)

            if len(history) == ATOM_LIMIT:
                break
    else:
        for path in get_documents_list():
            for entry in get_history(path):
                entry.insert(1, path)
                history.append(entry)

        history = sorted(history, key=lambda x: x[0], reverse=True)[:ATOM_LIMIT]

    for date, path, rev, author, desc in history:
        feed.add(path, desc if desc != '-' else 'No summary available',
            url=url_for('index', path=path, do='compare', to=rev),
            author=author,
            updated=date)

    return feed.get_response()


def do_compare(path):
    if path.startswith(FILE_PREFIX):
        raise InvalidRequest()

    rev_to = int(request.args.get('to', get_last_revision(path)))
    rev_from = int(request.args.get('from', rev_to - 1))

    # Render document diff
    content = render_diff(get_file_path(path, rev=rev_from), get_file_path(path, rev=rev_to))
    return render_template('wiki/compare.html', content=content)


def do_delete(path):
    if request.method == 'POST':
        if request.form.get('validate'):
            # Save empty document
            save_document(path, '', user=session.get('login'))

        return redirect(url_for('index', path=path))

    return render_template('wiki/delete.html')


def do_edit(path):
    if request.method == 'POST':
        if 'save' in request.form:
            # Save new document revision
            if path.startswith(FILE_PREFIX):
                attachment = request.files.get('attachment')

                if not path[len(FILE_PREFIX):]:
                    unnamed = True
                    path = FILE_PREFIX + attachment.filename
                else:
                    unnamed = False

                if unnamed or check_mimetype(path, attachment.filename):
                    save_document(path, attachment.stream.read(), user=session.get('login'))
                else:
                    flash(_('Document type differs from the previous one.'), 'error')
                    return redirect(url_for('index', path=path, do='edit'))
            else:
                save_document(path, request.form.get('data'), user=session.get('login'))

            # Unlock document
            lock_document(path, (session.get('login'), session.get('id')), unlock=True)

            return redirect(url_for('index', path=path))

    return do_show(path, action='edit')


def do_history(path):
    return render_template('wiki/history.html', history=get_history(path), is_file=path.startswith(FILE_PREFIX))


def do_move(path):
    if request.method == 'POST':
        if request.form.get('validate'):
            try:
                move_document(path, request.form.get('path'))
                path = request.form.get('path')
            except DocumentAlreadyExists:
                flash(_('A document with the same path already exists.'), 'error')
                return redirect(url_for('index', path=path, do='move'))

        return redirect(url_for('index', path=path))

    return render_template('wiki/move.html')


def do_render(path, toc=False):
    if path.startswith(FILE_PREFIX):
        raise InvalidRequest()

    return do_show(path, action='render')


def do_show(path, action='show'):
    content = None
    rev_info = None
    lock_info = None

    # Handle help document
    if path.startswith(HELP_PREFIX):
        if action not in ('render', 'show'):
            raise InvalidRequest()

        # Get document data
        try:
            mimetype, size, content = get_help(path[len(HELP_PREFIX):])
        except:
            mimetype, size, content = None

        if action == 'render':
            return render_document(content)
        else:
            return Response(render_template('wiki/show.html', content=content, immutable=True),
                404 if content is None else 200)

    # Check for file document
    is_file = path.startswith(FILE_PREFIX)

    # Unlock document if needed
    if request.args.get('discard'):
        lock_document(path, (session.get('login'), session.get('id')), unlock=True)
        return redirect(url_for('index', path=path))
    elif action == 'edit' and request.args.get('force'):
        lock_document(path, (session.get('login'), session.get('id')), unlock=True, force=True)
        return redirect(url_for('index', path=path, do='edit'))

    # Lock document for edition
    if action == 'edit':
        lock_info = lock_document(path, (session.get('login'), session.get('id')))

    # Get document data
    try:
        mimetype, size, meta, content = get_document(path, request.args.get('rev'),
            meta=(action == 'edit'), preview=is_file)
    except DocumentNotFound:
        mimetype, size, meta, content = None, 0, None, None

    if action == 'edit':
        meta = None

    # Handle normal documents
    if action == 'edit' and 'data' in request.form:
        content = request.form.get('data')
    else:
        if content is not None:
            # Get last revision information
            rev_info = get_history(path, rev=request.args.get('rev', -1))
        elif is_file and not path[len(FILE_PREFIX):]:
            # Force edition if unnamed file
            action = 'edit'

    # Render document and exit if needed
    if action == 'render':
        return render_document(content)

    response = Response(render_template('wiki/%s.html' % action, is_file=is_file, mimetype=mimetype,
        meta=meta, content=content, rev_info=rev_info, lock_info=lock_info), 404 if content is None else 200)

    if action == 'edit':
        response.cache_control.no_cache = True

    return response


def do_source(path):
    file_path = get_file_path(path, request.args.get('rev'))

    if request.if_modified_since and \
            datetime.utcfromtimestamp(int(os.path.getmtime(file_path))) <= request.if_modified_since:
        return Response(status=304)

    # Show document source
    mimetype, size, meta, content = get_document(path, request.args.get('rev'), meta=True)

    response = Response(content, direct_passthrough=True)
    response.headers.add('Content-Length', size)
    response.headers.add('Content-Type', mimetype if path.startswith(FILE_PREFIX) else 'text/plain; charset=utf-8')

    if request.args.get('download'):
        response.headers.add('Content-Disposition', 'attachment; filename=' + path[len(FILE_PREFIX):])

    response.headers.add('Last-Modified', http_date(os.path.getmtime(file_path)))

    return response
