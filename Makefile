PIPENV=PYTHONPATH=${PYTHONPATH}:${PWD} pipenv

ifdef TESTS
	PYTEST_ARGS = -k $(TESTS)
else
	PYTEST_ARGS = --cov=concrete_settings
endif


test:
	${PIPENV} run pytest -s $(PYTEST_ARGS)

tox:
	tox

all:
	@echo "Available targets:"
	@echo "test - run tests"

docs:
	$(MAKE) html -C docs

clean:
	python setup.py clean
	rm -r concrete_settings.egg_info

.PHONY: docs
