test = mallennlp

MODULE            = mallennlp
INTEGRATION_TESTS = tests
PROJECT           = example-project
PROJECT_PATH     := $(realpath $(PROJECT))
INSTALLED_BINARY := $(shell which mallennlp)
PYTEST_COMMAND    = python -m pytest -v --color=yes

.PHONY : clean
clean :
	@rm -rf ./allennlp_manager.egg-info/
	@rm -rf ./.mypy_cache/
	@rm -rf ./.pytest_cache/
	@rm -rf $(PROJECT)

.PHONY : project
project :
	rm -rf $(PROJECT)/
	mallennlp new $(PROJECT) \
		--loglevel=DEBUG \
		--username=epwalsh \
		--password=testing123

.PHONY : serve
serve : build project
	mallennlp --wd $(PROJECT_PATH) serve

.PHONY : typecheck
typecheck :
	@echo "Typechecks: mypy"
	@mypy $(MODULE) $(INTEGRATION_TESTS) --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@flake8 $(MODULE) $(INTEGRATION_TESTS)
	@echo "Lint: black"
	@black --check $(MODULE) $(INTEGRATION_TESTS)

.PHONY : unit-tests
unit-tests :
	@echo "Unit tests: pytest"
	@$(PYTEST_COMMAND) $(test)

.PHONY : integration-tests
integration-tests :
	@echo "Integration tests: pytest"
	@$(PYTEST_COMMAND) $(INTEGRATION_TESTS)

.PHONY : test
test : typecheck lint unit-tests integration-tests

.PHONY: create-branch
create-branch :
ifneq ($(issue),)
	git checkout -b ISSUE-$(issue)
	git push --set-upstream origin ISSUE-$(issue)
else ifneq ($(name),)
	git checkout -b $(name)
	git push --set-upstream origin $(name)
else
	$(error must supply 'issue' or 'name' parameter)
endif

.PHONY : install
install :
	python setup.py develop

.PHONY : uninstall
uninstall :
	python setup.py develop --uninstall && rm -f $(INSTALLED_BINARY)
