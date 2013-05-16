#!/usr/bin/make

THEME_NAME = default

LESSC = lessc
LESSC_ARGS = --no-color

CSS_FILE = styles.css
CSS_FILE_MIN = styles.min.css

CSS_FILE_PRINT = styles.print.css
CSS_FILE_PRINT_MIN = styles.print.min.css

DST_DIR = ../../../share/static/themes/$(THEME_NAME)

SRC_FILES = intro.less \
	define.less \
	fonts.less \
	common.less \
	form.less \
	icons.less \
	login.less \
	header.less \
	toolbar.less \
	pane.less \
	view.less \
	document.less \
	pygments.less

SRC_FILES_PRINT = intro.less \
	define.less \
	fonts.less \
	common.less \
	print.less \
	document.less \
	pygments.less

EXT_FILES = fonts \
	favicon.png \
	logo.png

all: install

clean:
	@echo -n 'Cleaning installed files... '
	@(test ! -d $(DST_DIR) || rm -rf $(DST_DIR)) && echo OK || echo Fail
	@echo -n 'Cleaning temporary files... '
	@rm -f styles*.css $(IMG_DIR).less $(IMG_DIR)*.png $(IMG_PNG) && echo OK || echo Fail

$(CSS_FILE): $(SRC_FILES)
	@echo -n 'Merging source files... '
	@cat $(SRC_FILES) | $(LESSC) $(LESSC_ARGS) - >$(CSS_FILE) && echo OK || echo Fail

$(CSS_FILE_MIN): $(CSS_FILE)
	@echo -n 'Packing $(CSS_FILE) file... '
	@cat ../../intro.release >$(CSS_FILE_MIN) && \
		$(LESSC) $(LESSC_ARGS) --compress $(CSS_FILE) >>$(CSS_FILE_MIN) && echo OK || echo Fail

$(CSS_FILE_PRINT): $(SRC_FILES_PRINT)
	@echo -n 'Merging source files... '
	@cat $(SRC_FILES_PRINT) | $(LESSC) $(LESSC_ARGS) - >$(CSS_FILE_PRINT) && echo OK || echo Fail

$(CSS_FILE_PRINT_MIN): $(CSS_FILE_PRINT)
	@echo -n 'Packing $(CSS_FILE_PRINT) file... '
	@cat ../../intro.release >$(CSS_FILE_PRINT_MIN) && \
		$(LESSC) $(LESSC_ARGS) --compress $(CSS_FILE_PRINT) >>$(CSS_FILE_PRINT_MIN) && echo OK || echo Fail

install: $(CSS_FILE_MIN) $(CSS_FILE_PRINT_MIN)
	@echo -n 'Installing files... '
	@install -m 0755 -d $(DST_DIR) && install -m 0644 $(CSS_FILE_MIN) $(DST_DIR)/$(CSS_FILE) && \
		install -m 0755 -d $(DST_DIR) && install -m 0644 $(CSS_FILE_PRINT_MIN) $(DST_DIR)/$(CSS_FILE_PRINT) && \
		echo OK || echo Fail
	@echo -n 'Installing extra files... '
	@cd extra && cp -r $(EXT_FILES) ../$(DST_DIR)/ && echo OK || echo Fail

devel: install
	@echo -n 'Overriding files... '
	@install -m 0644 $(CSS_FILE) $(DST_DIR)/$(CSS_FILE) && echo OK || echo Fail
	@install -m 0644 $(CSS_FILE_PRINT) $(DST_DIR)/$(CSS_FILE_PRINT) && echo OK || echo Fail
