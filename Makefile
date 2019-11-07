test = mallennlp

MODULE         = mallennlp
PROJECT        = example-project
PROJECT_PATH          := $(realpath $(PROJECT))
INSTALLED_BIN := $(shell which mallennlp)

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
	@mypy $(MODULE) tests --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@flake8 $(MODULE) tests
	@echo "Lint: black"
	@black --check $(MODULE) tests

.PHONY : unit-tests
unit-tests :
	@echo "Unit tests: pytest"
	@python -m pytest -v --color=yes $(test)

.PHONY : integration-tests
integration-tests :
	@echo "Integration tests: pytest"
	@python -m pytest -v --color=yes tests

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
	python setup.py develop --uninstall && rm -f $(INSTALLED_BIN)
