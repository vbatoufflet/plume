#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.stderr.write('Usage: %s PORT\n' % os.path.basename(sys.argv[0]))
        sys.exit(1)

    from plume.app import app
    app.run(port=int(sys.argv[1]), debug=True)

# vim: ft=python
