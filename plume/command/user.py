# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import sys

from __main__ import subparsers
from plume.user import UserBackend


def user_add(args):
    if not backend.exists(args.login):
        backend.set(login=args.login, password=args.password, fullname=args.name, email=args.mail)
        sys.stdout.write('OK\n')
    else:
        sys.stderr.write('Error: user %s already exists\n' % args.login)


def user_delete(args):
    if backend.exists(args.login):
        if not args.force:
            sys.stdout.write('You are about to delete %s user account. Are you sure? (y/N) ' % args.login)

            if raw_input().lower().strip() not in ['y', 'yes']:
                return

        backend.unset(login=args.login)
        sys.stdout.write('OK\n')
    else:
        sys.stderr.write("Error: user %s doesn't exist\n" % args.LOGIN)


def user_list(args):
    result = backend.list()

    if not result:
        sys.stdout.write('No user found.\n')
        return

    if not args.raw:
        result.insert(0, {'uid': 'ID', 'login': 'Login', 'fullname': 'Full Name', 'email': 'Email', 'enabled': 'Enabled'})

    row_format = ''
    row_total = 0

    for key in ('uid', 'login', 'fullname', 'email', 'enabled'):
        max_length = max([len(str(x[key])) for x in result])
        row_format += '%%(%s)-%ds  ' % (key, max_length)
        row_total += max_length

    for row in result:
        sys.stdout.write(row_format % row + '\n')

        if not args.raw and row['uid'] == 'Id':
            sys.stdout.write('-' * (row_total + 2 * (len(row.keys()) - 1)) + '\n')


def user_modify(args):
    if backend.exists(args.login):
        kwargs = {}

        if args.disable or args.enable:
            kwargs['enabled'] = False if args.disable else True

        if args.name:
            kwargs['fullname'] = args.name

        if args.mail:
            kwargs['email'] = args.mail

        if args.password:
            kwargs['password'] = args.password

        backend.set(modify=True, login=args.login, **kwargs)
        sys.stdout.write('OK\n')
    else:
        sys.stderr.write("Error: user %s doesn't exist\n" % args.LOGIN)


subparser = subparsers.add_parser('useradd', help='add a new user')
subparser.set_defaults(func=user_add)
subparser.add_argument('-f', '--force', action='store_true', help='do not prompt for confirmation')
subparser.add_argument('-m', '--mail', help='user mail address', required=True)
subparser.add_argument('-n', '--name', help='user full name', required=True)
subparser.add_argument('-p', '--password', help='user login password', required=True)
subparser.add_argument('login', metavar='LOGIN', help='user login name')

subparser = subparsers.add_parser('userdel', help='delete an existing user')
subparser.set_defaults(func=user_delete)
subparser.add_argument('-f', '--force', action='store_true', help='do not prompt for confirmation')
subparser.add_argument('login', metavar='LOGIN', help='user login name')

subparser = subparsers.add_parser('userlist', help='list existing users')
subparser.set_defaults(func=user_list)
subparser.add_argument('-r', '--raw', action='store_true', help='print list in raw format')

subparser = subparsers.add_parser('usermod', help='modify an existing user')
subparser.set_defaults(func=user_modify)

group = subparser.add_mutually_exclusive_group()
group.add_argument('-d', '--disable', action='store_true', help='disable user account')
group.add_argument('-e', '--enable', action='store_true', help='enable user account')

subparser.add_argument('-m', '--mail', help='user mail address')
subparser.add_argument('-n', '--name', help='user full name')
subparser.add_argument('-p', '--password', help='user login password')
subparser.add_argument('login', metavar='LOGIN', help='user login name')

backend = UserBackend()
