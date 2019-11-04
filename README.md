# allennlp-manager

[![CircleCI](https://circleci.com/gh/epwalsh/allennlp-manager.svg?style=svg)](https://circleci.com/gh/epwalsh/allennlp-manager)
![Docker Hub](https://img.shields.io/docker/pulls/epwalsh/allennlp-manager)
![GitHub](https://img.shields.io/github/license/epwalsh/allennlp-manager)

Your manager for AllenNLP experiments.

## Features

A CLI and dashboard for running, tracking, and comparing experiments.

## Installation

```bash
pip install 'git+git://github.com/epwalsh/allennlp-manager.git#egg=mallennlp'
```

## Quick start

Create a new project named `my-project`:

```bash
mallennlp new my-project && cd my-project
```

Then edit the `Project.toml` file to your liking and start the server:

```bash
mallennlp serve
```
