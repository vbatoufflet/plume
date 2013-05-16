# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import codecs
import ConfigParser
import hashlib
import os
import stat
import uuid

from flask import Flask, Response, abort, flash, g, redirect, render_template, request, session, url_for
from flask.ext.babel import Babel, get_locale, get_timezone, _
from jinja2 import Markup
from plume import ACTIONS_PRIVILEGED, ACTIONS_UNPRIVILEGED, CONF_DIR, DEFAULT_LOCALE, DEFAULT_TIMEZONE, \
    PASSWORD_MIN_LENGTH, ROOT_PATH, SETTINGS_LIST, STATIC_DIR, TEMPLATE_DIR
from plume.action import *
from plume.exception import GenericException, PasswordTooShort
from plume.renderer import render_document
from plume.search import search_documents
from plume.user import UserBackend
from plume.utils import get_path, split_path
from pytz import common_timezones


def filter_render(data, toc=False):
    return Markup(render_document(data, toc))


def filter_strong(data):
    return Markup('<strong>%s</strong>' % data)


# Create application
app = Flask('__main__', static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
app.root_path = ROOT_PATH

app.jinja_options['extensions'].append('jinja2.ext.do')

app.jinja_env.filters.update({
    'render': filter_render,
    'strong': filter_strong,
})


# Load secret key
file_path = os.path.join(CONF_DIR, 'plume.secret')

if not os.path.exists(file_path):
    raise Exception('secret file %s is missing\n' % file_path)

mode = os.stat(file_path).st_mode

if mode & stat.S_IRWXU != 384 or mode & stat.S_IRWXG != 0 or mode & stat.S_IRWXO != 0:
    raise Exception('secret file %s permissions should be 600\n' % file_path)

app.secret_key = codecs.open(file_path, 'r', 'utf-8').read().encode('utf-8').strip()

# Load configuration
file_path = os.path.join(CONF_DIR, 'plume.conf')

if os.path.exists(file_path):
    parser = ConfigParser.ConfigParser()
    parser.readfp(codecs.open(file_path, 'r', 'utf-8'))

    # Update application settings
    app.config.update(**dict((x.upper(), y) for x, y in parser.items('main')))


# Initialize i18n support
babel = Babel(app)


@babel.localeselector
def locale_selector():
    if hasattr(g, 'user') and g.user.locale:
        return g.user.locale

    return app.config.get('DEFAULT_LOCALE', DEFAULT_LOCALE)


@babel.timezoneselector
def timezone_selector():
    if hasattr(g, 'user') and g.user.timezone:
        return g.user.timezone

    return app.config.get('DEFAULT_TIMEZONE', DEFAULT_TIMEZONE)


@app.errorhandler(Exception)
def handle_server_exception(e):
    if app.debug:
        print('-' * 80)

        import traceback
        traceback.print_exc()

        if hasattr(e, 'errmsg'):
            print('Error: %s' % e.errmsg)

        print('-' * 80)

    return Response(render_template('error.html', message=str(e) if isinstance(e, GenericException) else None),
        e.status if hasattr(e, 'status') else 500)


@app.context_processor
def context_processor():
    return {
        'config': app.config,
        'user': getattr(g, 'user', None),
        'docpath': getattr(g, 'path', None),
        'split_path': split_path,
    }


@app.before_request
def before_request():
    if session.get('uid'):
        g.user = UserBackend().get(session.get('uid'))

        if not g.user:
            signout()


@app.teardown_request
def teardown_request(e):
    if hasattr(g, 'user'):
        del g.user


@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path='/'):
    g.path = path

    action = request.args.get('do', 'show')

    # Redirect if unknown action
    if action not in ACTIONS_PRIVILEGED + ACTIONS_UNPRIVILEGED:
        return redirect(url_for('index', path=path))

    # Check for required authentication
    if action not in ACTIONS_UNPRIVILEGED and not session.get('uid'):
        return redirect(url_for('signin', next=get_path(request)))

    # Execute requested action
    if request.method == 'POST' and action in ACTIONS_PRIVILEGED or action in ACTIONS_PRIVILEGED + ACTIONS_UNPRIVILEGED:
        return globals()['do_' + action](path)

    abort(405)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user = UserBackend().authenticate(request.form.get('signin-login'), request.form.get('signin-password'))

        if user:
            session.update({
                'id': str(uuid.uuid4()),
                'uid': user.uid,
                'login': user.login,
                'name': user.fullname,
                'avatar': '//gravatar.com/avatar/%s' % hashlib.md5(user.email.lower()).hexdigest(),
            })

            return redirect(request.form.get('next', url_for('index')))
        else:
            flash(_('Authentication failed.'), 'error')
            return redirect(url_for('signin', next=request.args.get('next')))

    return Response(render_template('signin.html'), 401)


@app.route('/signout')
def signout():
    session.clear()
    return redirect(request.args.get('next') if 'next' in request.args else url_for('index'))


@app.route('/settings')
@app.route('/settings/<page>', methods=['GET', 'POST'])
def settings(page=None):
    if not session.get('uid'):
        return redirect(url_for('signin', next=get_path(request)))

    if page not in ('identity', 'regional', 'password'):
        return redirect(url_for('settings', page='identity'))

    if request.method == 'POST':
        if request.form.get('validate'):
            if page == 'password':
                backend = UserBackend()

                if not backend.authenticate(session.get('login'), request.form.get('password-current')):
                    flash(_('Current password is invalid.'), 'error')
                elif request.form.get('password-new') != request.form.get('password-repeat'):
                    flash(_("Passwords don't match."), 'error')
                else:
                    try:
                        backend.set(modify=True, login=session.get('login'), password=request.form.get('password-new'))
                        flash(_('Password successfuly changed.'), 'info')
                    except PasswordTooShort:
                        flash(_('Password is too short. Must be a least %(length)d characters long.',
                            length=PASSWORD_MIN_LENGTH), 'error')
            else:
                settings = dict((x, request.form.get(x)) for x in SETTINGS_LIST if x in request.form)

                if settings:
                    user = UserBackend().set(modify=True, login=session.get('login'), **settings)

                    session.update({
                        'name': user.fullname,
                        'avatar': '//gravatar.com/avatar/%s' % hashlib.md5(user.email.lower()).hexdigest(),
                    })

                    if 'locale' in settings:
                        g.user.locale = settings.get('locale')

                    flash(_('Settings successfuly saved.'), 'info')

        return redirect(url_for('settings', page=page))

    locales = [(x.language, x.display_name.capitalize()) for x in app.babel_instance.list_translations()]

    return render_template('settings.html', page=page, locales=locales, timezones=common_timezones,
        current_locale=get_locale().language, current_timezone=get_timezone().zone)


@app.route('/search')
def search():
    return render_template('wiki/search.html', results=search_documents(request.args.get('q')))
