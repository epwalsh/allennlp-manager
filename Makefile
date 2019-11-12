test = mallennlp

MODULE            = mallennlp
INTEGRATION_TESTS = tests
EXAMPLE_PROJECT   = example-project
SRC              := $(MODULE) $(INTEGRATION_TESTS) $(EXAMPLE_PROJECT)
PROJECT           = tmp-project
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
	@rm -rf $(PROJECT)/
	@mallennlp new $(PROJECT) \
		--loglevel=DEBUG \
		--username=epwalsh \
		--password=testing123 \
		--server-imports hello_world
	@mkdir $(PROJECT)/hello_world
	@echo 'from mallennlp.dashboard.page import Page\n\n@Page.register("/hello-world")\nclass HelloWorld(Page):\n    requires_login = True\n    navlink_name = "Hello, World!"\n\n    def get_elements(self):\n        return ["Hello, World!"]' > $(PROJECT)/hello_world/__init__.py

.PHONY : serve
serve : build project
	mallennlp --wd $(PROJECT_PATH) serve

.PHONY : typecheck
typecheck :
	@echo "Typechecks: mypy"
	@python -m mypy $(SRC) --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@python -m flake8 $(SRC)
	@echo "Lint: black"
	@python -m black --check $(SRC)

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
