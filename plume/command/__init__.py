# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Vincent Batoufflet.
#
# License: BSD, see LICENSE for more details.
#

import os


def get_modules():
    result = []

    for name in os.listdir(os.path.dirname(__file__)):
        if not name.endswith('.py') or name.startswith('.') or name.startswith('_'):
            continue

        result.append(os.path.splitext(name)[0])

    return result


def load_module(name, fromlist=[]):
    return __import__('plume.command.%s' % name, globals(), locals(), fromlist)
