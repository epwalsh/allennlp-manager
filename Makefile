port = 5000
cmd = /bin/bash

DOCKER_IMAGE = mallennlp
DOCKER_TAG   = latest
DOCKER_ARGS := --rm -p 5000:$(port)

.PHONY : build
build :
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) -f Dockerfile .

.PHONY : run
run :
	docker run $(DOCKER_ARGS) $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY : mallennlp
mallennlp : build run

.PHONY : run-it
run-it :
	docker run -it $(DOCKER_ARGS) $(DOCKER_IMAGE):$(DOCKER_TAG) $(cmd)
