#!/usr/bin/make

UGLIFYJS = uglifyjs
UGLIFYJS_ARGS = --compress --mangle

JSHINT = jshint
JSHINT_ARGS = --show-non-errors

JS_FILE = plume.js
JS_FILE_MIN = plume.min.js

DST_DIR = ../../share/static

SRC_FILES = intro.js \
	form.js \
	toolbar.js \
	pane.js \
	upload.js \
	outro.js

EXT_FILES = jquery.min.js \
	jquery.cookie.min.js

EXT_DEVEL = $(EXT_FILES:.min.js=.js)

all: lint install

clean:
	@echo -n 'Cleaning installed files... '
	@(test ! -d $(DST_DIR) || cd $(DST_DIR) && rm -rf $(JS_FILE) $(EXT_FILES)) && echo OK || echo Fail
	@echo -n 'Cleaning temporary files... '
	@rm -f $(JS_FILE) $(JS_FILE_MIN) && echo OK || echo Fail

$(JS_FILE): $(SRC_FILES)
	@echo -n 'Merging source files... '
	@cat $(SRC_FILES) >$(JS_FILE) && echo OK || echo Fail

$(JS_FILE_MIN): $(JS_FILE)
	@echo -n 'Packing $(JS_FILE) file... '
	@cat ../intro.release >$(JS_FILE_MIN) && $(UGLIFYJS) $(UGLIFYJS_ARGS) -- $(JS_FILE) >>$(JS_FILE_MIN) && \
		echo OK || echo Fail

lint: $(JS_FILE)
	@echo -n 'Checking $(JS_FILE) with JSHint... '
	-@$(JSHINT) $(JS_FILE) $(JSHINT_ARGS) && echo OK || echo Fail

install: $(JS_FILE_MIN)
	@echo -n 'Installing files... '
	@install -m 0755 -d $(DST_DIR) && install -m 0644 $(JS_FILE_MIN) $(DST_DIR)/$(JS_FILE) && echo OK || echo Fail
	@echo -n 'Installing third-party files... '
	@cd thirdparty && for FILE in $(EXT_FILES); do cp -r $$FILE ../$(DST_DIR)/`echo $$FILE | sed -e 's;\.min\.js$$;.js;'`; \
		done && echo OK || echo Fail

devel: install
	@echo -n 'Overriding files... '
	@install -m 0644 $(JS_FILE) $(DST_DIR)/$(JS_FILE) && \
		cd thirdparty && cp -r $(EXT_DEVEL) ../$(DST_DIR)/ && echo OK || echo Fail
