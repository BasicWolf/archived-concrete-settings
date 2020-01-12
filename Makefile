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


lint: flake8 safety


flake8:
	poetry run flake8 --config=.flake8rc concrete_settings tests

safety:
	poetry run safety check

docs: doctest
	$(MAKE) html -C docs

doctest:
	$(MAKE) doctest -C docs

clean:
	python setup.py clean
	rm -r concrete_settings.egg_info

.PHONY: docs
