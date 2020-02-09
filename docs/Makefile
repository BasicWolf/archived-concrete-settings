# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -W -n
SPHINXBUILD   = poetry run sphinx-build
SOURCEDIR     = src
BUILDDIR      = _build
STATICDIR     = ${SOURCEDIR}/_static
EXAMPLESDIR   = ${STATICDIR}/examples
DIR           := ${CURDIR}

# Examples sources / data files
django30_template = ${EXAMPLESDIR}/django30_template.yml


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: ${django30_template} Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


${django30_template}: ${EXAMPLESDIR}
	cp ${DIR}/../concrete_settings/contrib/frameworks/django30_template.yml ${EXAMPLESDIR}

${EXAMPLESDIR}:
	mkdir -p ${EXAMPLESDIR}
