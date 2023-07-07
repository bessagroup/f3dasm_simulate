.DEFAULT_GOAL := help

PACKAGEDIR := dist
COVERAGEREPORTDIR := coverage_html_report

.PHONY: help init test test-html build upload upload-testpypi

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  init                Install the requirements.txt"
	@echo "  test                Run the tests with pytest"
	@echo "  test-html           Run the tests with pytest and open the HTML coverage report"
	@echo "  build               Build the package"
	@echo "  upload              Upload the package to the PyPi index"
	@echo "  upload-testpypi     Upload the package to the PyPi-test index"

init:
	pip install -r requirements.txt

test:
	pytest

test-html:
	pytest
	xdg-open ./$(COVERAGEREPORTDIR)/index.html

build:
	-rm -rf $(PACKAGEDIR)/*
	python -m build

upload-testpypi:
	$(MAKE) build
	twine upload -r testpypi $(PACKAGEDIR)/* --verbose

upload:
	$(MAKE) build
	twine upload $(PACKAGEDIR)/* --verbose
