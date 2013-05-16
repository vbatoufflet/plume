# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

from flask.ext.babel import _


class GenericException(Exception):
    message = None

    def __init__(self, **kwargs):
        Exception.__init__(self)
        [setattr(self, x, y) for x, y in kwargs.iteritems()]

    def __str__(self):
        return self.message


class BackendException(GenericException):
    pass


# 4XX

class InvalidRequest(BackendException):
    status = 400
    message = _('Invalid request')


class InvalidRevisionNumber(BackendException):
    status = 400
    message = _('Invalid revision number')


class DocumentAlreadyExists(BackendException):
    status = 404
    message = _('Document already exists')


class DocumentNotFound(BackendException):
    status = 404
    message = _('No such document')


class PasswordTooShort(BackendException):
    status = 400
    message = _('Password is too short')


# 5XX

class EmptyDocumentPath(BackendException):
    status = 500
    message = _('Empty document path')


class EmptyUserName(BackendException):
    status = 500
    message = _('Empty user name')
