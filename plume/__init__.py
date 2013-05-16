# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import os.path


__version__ = '0.1'

ROOT_PATH = ''

BIN_DIR = 'bin'
CONF_DIR = 'etc'
DATA_DIR = 'var'
SHARE_DIR = 'share'

STATIC_DIR = os.path.join(SHARE_DIR, 'static')
TEMPLATE_DIR = os.path.join(SHARE_DIR, 'templates')

HELP_DIR = os.path.join(SHARE_DIR, 'documents', 'help')

DOCUMENT_DIR = os.path.join(DATA_DIR, 'documents')

DEFAULT_LOCALE = 'en'
DEFAULT_TIMEZONE = 'UTC'

HTMLDIFF_TAB_SIZE = 4
HTMLDIFF_WRAP_COLUMN = 80

ATOM_LIMIT = 15

ACTIONS_PRIVILEGED = ('delete', 'edit', 'move')
ACTIONS_UNPRIVILEGED = ('atom', 'compare', 'history', 'render', 'show', 'source')

SETTINGS_LIST = (
    'email',
    'fullname',
    'locale',
    'timezone',
)

PASSWORD_MIN_LENGTH = 8

FILE_PREFIX = 'file:'
HELP_PREFIX = 'help:'
