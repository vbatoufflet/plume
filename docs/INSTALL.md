Installation
============

Requirements
------------

Plume requires Python 2.5 or higher and depends on some modules:

 * argparse (if Python < 2.7)
 * Flask
 * Flask-Babel
 * gunicorn
 * misaka
 * Pygments
 * SQLAlchemy
 * Whoosh

(?) Please note that Python 3.x series are not supported.


Building the environment
------------------------

In order to get started with Plume, the automatic setup uses `virtualenv`.

You can either install it by running:

    sudo pip install virtualenv

or on Debian flavored distributions:

    sudo apt-get install python-virtualenv

Once `virtualenv` installed, all requirements and base installation can be performed by simply running:

    make env


Configuring the service
-----------------------

A sample configuration is provided in the `etc/plume.conf` file. In this file you can configure the various options of
the application.

(?) The daemon will need to be restarted to handle configuration changes.

The second file and the most important here is `etc/plume.secret`. It manages the secret key used by the [Flask][0]
framework to handle session cookies. Change it to whatever **secret value** you want or just run by example:

    openssl rand -base64 32 >etc/plume.secret

/!\ Permissions on the `etc/plume.secret` file must be 600.


Managing users
--------------

Before being able to use Plume, you will need to create at least one user account.

Plume comes with a `plumectl` utility able to manage users accounts (see `plumectl --help` for a list of available
commands):

    bin/python scripts/plumectl useradd -m bob@kelso.com -n 'Bob Kelso' -p password bob


Starting the service
--------------------

The recommended way to start the application is by using Gunicorn:

    bin/gunicorn -b localhost:10000 -w 4 --debug plume.app:app

If you encounter some issues and if Gunicorn's debugging is driving you crazy, a simple FCGI launcher is also provided:

    bin/python scripts/plume.fcgi 10000


Indexing documents
------------------

Plume uses [Whoosh][1] in order to perform document indexing and online search.

To build the index, run:

    plumectl index


[0]: http://flask.pocoo.org/
[1]: https://bitbucket.org/mchaput/whoosh/
