#!/usr/bin/make -f
# -*- Makefile -*-

SUB_DIRS=js themes

all clean install devel:
	@for i in $(SUB_DIRS); do \
		make -C $$i $@; \
	done
