PIPENV=PYTHONPATH=${PYTHONPATH}:${PWD} pipenv

ifdef TESTS
	PYTEST_ARGS = -k $(TESTS)
else
	PYTEST_ARGS = --cov=concrete_settings
endif


all:
	@echo "Available targets:"
	@echo "test - run tests"


test:
	${PIPENV} run pytest -s $(PYTEST_ARGS)

tox:
	tox

flake8:
	flake8 --config=.flake8rc concrete_settings tests

docs:
	$(MAKE) html -C docs

clean:
	python setup.py clean
	rm -r concrete_settings.egg_info

.PHONY: docs
