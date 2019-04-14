PIPENV=PYTHONPATH=${PYTHONPATH}:${PWD} pipenv

ifdef TESTS
	PYTEST_ARGS = -k $(TESTS)
else
	PYTEST_ARGS = --cov=concrete_settings
endif


test:
	${PIPENV} run pytest -s $(PYTEST_ARGS)

all:
	@echo "Available targets:"
	@echo "test - run tests"

clean:
	python setup.py clean
	rm -r concrete_settings.egg_info
