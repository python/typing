# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SOURCEDIR     = .
SOURCES       =
BUILDDIR      = _build
PYTHON       = python3
VENVDIR      = ./venv
SPHINXBUILD  = PATH=$(VENVDIR)/bin:$$PATH sphinx-build

ALLSPHINXOPTS = -b $(BUILDER) -d build/doctrees $(SPHINXOPTS) . build/$(BUILDER) $(SOURCES)

.PHONY: help clean build html text venv Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	-rm -rf build/* $(VENVDIR)/*

build:
	-mkdir -p build
	$(SPHINXBUILD) $(ALLSPHINXOPTS)
	@echo

html: BUILDER = html
html: build
	@echo "Build finished. The HTML pages are in build/html."

text: BUILDER = text
text: build
	@echo "Build finished; the text files are in build/text."

venv:
	$(PYTHON) -m venv $(VENVDIR)
	$(VENVDIR)/bin/python3 -m pip install -U pip setuptools
	$(VENVDIR)/bin/python3 -m pip install -r requirements.txt
	@echo "The venv has been created in the $(VENVDIR) directory"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
