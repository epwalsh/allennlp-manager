# [WORK IN PROGRESS] allennlp-manager

[![CircleCI](https://circleci.com/gh/epwalsh/allennlp-manager.svg?style=svg)](https://circleci.com/gh/epwalsh/allennlp-manager)
[![Docker Hub](https://img.shields.io/docker/pulls/epwalsh/allennlp-manager)](https://cloud.docker.com/repository/docker/epwalsh/allennlp-manager)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/w/epwalsh/allennlp-manager)](https://github.com/epwalsh/allennlp-manager/graphs/commit-activity)
[![License](https://img.shields.io/github/license/epwalsh/allennlp-manager)](https://github.com/epwalsh/allennlp-manager/blob/master/LICENSE)

Your manager for AllenNLP experiments.

## Dependencies

AllenNLP, Python 3.6, and Docker are required.

## Road map

The goal of this project is to build a CLI and dashboard for running, queueing, tracking, and comparing experiments.

This was inspired by other open source projects such as the resource manager [**slurm**](https://slurm.schedmd.com/documentation.html) and visualization toolkit [**TensorBoard**](https://www.tensorflow.org/tensorboard), as well as commercial software such as [**Weights & Biases**](https://www.wandb.com/) and [**Foundations Atlas**](https://www.atlas.dessa.com/).

**slurm** and **TensorBoard** are both excellent tools, but they fall short for NLP researchers in a number of ways. For example, **slurm** is difficult to set up and use - especially on your own desktop or server - unless you're an experienced sys admin, and **TensorBoard** has limited functionality for searching, organizing, tagging, and comparing models. And while the commercial options are fairly easy to use and come with a solid set of features, they were built as generic tools and therefore don't "understand" all of AllenNLP's features.

**allennlp-manager** aims to leverage all of the convenient pieces of AllenNLP to provide you with a dashboard that let's you
- quickly search through all of your experiments based on properties like model type, training / validation set, or arbitrary tags,
- visualize the metrics from training runs of an experiment, and
- compare experiments in a number of ways, such as looking at a git diff of configuration files.

In addition to the dashboard, there will be a multi-purpose CLI with commands for serving the dashboard, updating to the latest version, and programmatically submitting training runs.

For the first release I intend to have all of the features implemented except for, possibly, the **slurm**-like resource manager and job queueing system, as that may become quite complex.

## Updates

**11/5**

Dashboard skeleton implemented with `Page` abstraction.

**11/4**

CLI implemented (using click). Project can be created with `mallennlp new [PROJECT NAME]` and dashboard can be served with `mallennlp serve` from within the project directory (dashboard just returns 'Hello from AllenNLP manager' at the moment).

## For potential contributors

I chose to implement this project entirely in Python to make it as easy possible for anyone to contribute, since if you are using AllenNLP you must already be familiar with Python. The dashboard is built with [plotly Dash](https://plot.ly/dash/), which is kind of like Python's version of [Shiny](https://shiny.rstudio.com/) if you're familiar with R.

The continuous integration for **allennlp-manager** is a lot like that of **AllenNLP**. Unit tests are run with [pytest](https://docs.pytest.org/en/latest/), code is type-checked with [mypy](http://mypy-lang.org/), linted with [flake8](http://flake8.pycqa.org/en/latest/), and formatted with [black](https://pypi.org/project/black/). You can run all of the CI-steps locally with `make test`.

If this is your first time contributing to a project on GitHub, please see [this Gist](https://gist.github.com/epwalsh/9e1b77d46ec232d55e6e344bb649fb19) for an example workflow.

<!-- ## Installation -->

<!-- ```bash -->
<!-- pip install 'git+git://github.com/epwalsh/allennlp-manager.git#egg=mallennlp' -->
<!-- ``` -->

<!-- ## Quick start -->

<!-- Create a new project named `my-project`: -->

<!-- ```bash -->
<!-- mallennlp new my-project && cd my-project -->
<!-- ``` -->

<!-- Then edit the `Project.toml` file to your liking and start the server: -->

<!-- ```bash -->
<!-- mallennlp serve -->
<!-- ``` -->
