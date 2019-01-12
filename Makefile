PIPENV=PYTHONPATH=${PYTHONPATH}:${PWD} pipenv

ifdef TESTS
	PYTEST_ARGS = -k $(TESTS)
else
	PYTEST_ARGS =
endif


test:
	${PIPENV} run pytest -s $(PYTEST_ARGS)
