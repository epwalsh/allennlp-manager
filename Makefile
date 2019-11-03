port = 5000
cmd  = /bin/bash
path = ./example-project
test = mallennlp

DOCKER_IMAGE     = allennlp-manager
DOCKER_TAG       = latest
DOCKER_ARGS     := --rm -p 5000:$(port) -v $(path):/opt/python/app/project
COMMITHASH      := $(shell git rev-parse --verify HEAD)
ALLENNLP_VERSION = stable

.PHONY : build
build :
	docker build \
		--build-arg COMMITHASH=$(COMMITHASH) \
		--build-arg ALLENNLP_VERSION=$(ALLENNLP_VERSION) \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-f Dockerfile \
		.

.PHONY : run
run :
	docker run $(DOCKER_ARGS) $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY : mallennlp
mallennlp : build run

.PHONY : run-it
run-it :
	docker run -it $(DOCKER_ARGS) $(DOCKER_IMAGE):$(DOCKER_TAG) $(cmd)

.PHONY : typecheck
typecheck :
	@echo "Typechecks: mypy"
	@mypy $(test) --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@flake8 $(test)
	@echo "Lint: black"
	@black --check $(test)

.PHONY : unit-test
unit-test :
	@echo "Unit tests: pytest"
	@python -m pytest -v --color=yes $(test)

.PHONY : test
test : typecheck lint unit-test

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
