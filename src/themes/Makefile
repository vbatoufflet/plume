#!/usr/bin/make -f
# -*- Makefile -*-

SUB_DIRS=$(shell find . -mindepth 1 -maxdepth 1 -type d)

all: install

clean install devel:
	@for i in $(SUB_DIRS); do \
		make -C $$i $@; \
	done
