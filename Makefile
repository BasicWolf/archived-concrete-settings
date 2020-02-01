ifdef TESTS
	PYTEST_ARGS = -k $(TESTS)
else
	PYTEST_ARGS = --cov=concrete_settings
endif


all:
	@echo "Available targets:"
	@echo "test [TESTS=TEST1,TEST2,...] - run tests"
	@echo "lint ....................... - run linterns"

test:
	poetry run pytest -s $(PYTEST_ARGS)

tox:
	tox


lint: flake8 mypy safety


flake8:
	poetry run flake8 --config=.flake8rc concrete_settings tests

mypy:
	poetry run mypy concrete_settings

safety:
	poetry run safety check

docs: doctest
	$(MAKE) html -C docs

doctest:
	$(MAKE) doctest -C docs

clean:
	rm -r concrete_settings.egg-info pip-wheel-metadata .pytest_cache

.PHONY: docs
