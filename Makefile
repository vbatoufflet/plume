#!/usr/bin/make -f
# -*- makefile -*-

VIRTUALENV = virtualenv
PYTHON = bin/python

FIND = find

PREFIX += .

all: install

build: static locale

install: build
	@echo '[Install]'
	$(PYTHON) setup.py install

clean:
	@echo '[Clean environment]'
	$(MAKE) -C src clean
	rm -rf bin build dist include lib local plume.egg-info
	$(FIND) plume -iname '*.pyc' -delete
	$(FIND) translations -iname '*.mo' -delete

env:
	@echo '[Build environment]'
	$(VIRTUALENV) --distribute --no-site-packages $(PREFIX)
	$(PYTHON) setup.py develop

static:
	@echo '[Build static files]'
	$(MAKE) -C src all

update-locale: env
	@echo '[Update locale catalogs]'
	@mkdir -p build
	$(PYTHON) setup.py extract_messages
	$(PYTHON) setup.py update_catalog

locale: env
	@echo '[Compile locale catalogs]'
	$(PYTHON) setup.py compile_catalog

release: static locale
	@echo '[Build release tarball]'
	$(PYTHON) setup.py sdist
