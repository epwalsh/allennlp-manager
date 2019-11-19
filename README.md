# [WORK IN PROGRESS] allennlp-manager

[![CircleCI](https://circleci.com/gh/epwalsh/allennlp-manager.svg?style=svg)](https://circleci.com/gh/epwalsh/allennlp-manager)
[![License](https://img.shields.io/github/license/epwalsh/allennlp-manager)](https://github.com/epwalsh/allennlp-manager/blob/master/LICENSE)

Your manager for [AllenNLP](https://github.com/allenai/allennlp) experiments.

### Table of contents

- [**Road map**](#road-map) :car:
- [**Dependencies**](#dependencies)
- [**Installation**](#installation)
- [**Quick start**](#quick-start) :rocket:
- [**Configuration**](#configuration)
- [**Contributing**](#for-potential-contributors)
- [**Updates**](#updates) :tada: :tada: :tada:

## Road map

The goal of this project is to build a customizable CLI and dashboard for running, queueing, tracking, and comparing experiments.

This was inspired by other open source projects such as the resource manager [**slurm**](https://slurm.schedmd.com/documentation.html) and visualization toolkit [**TensorBoard**](https://www.tensorflow.org/tensorboard), as well as commercial software such as [**Weights & Biases**](https://www.wandb.com/) and [**Foundations Atlas**](https://www.atlas.dessa.com/).

**slurm** and **TensorBoard** are both excellent tools, but they fall short for NLP researchers in a number of ways. For example, **slurm** is difficult to set up and use - especially on your own desktop or server - unless you're an experienced sys admin, and **TensorBoard** has limited functionality for searching, organizing, tagging, and comparing models. This doesn't scale well when you have hundreds or even thousands of experiments. And while the commercial options are fairly easy to use and come with a solid set of features, they were built as generic tools and therefore don't "understand" all of AllenNLP's features. They are also not customizable or extendable.

**allennlp-manager** aims to leverage all of the convenient pieces of AllenNLP to provide you with a dashboard that let's you
- quickly search through all of your experiments based on properties like model type, training / validation set, or arbitrary tags,
- visualize the metrics from training runs of an experiment,
- compare experiments in a number of ways, such as looking at a git diff of configuration files,
- and easily extend it by adding your own interactive pages.

In addition to the dashboard, there is a multi-purpose CLI with commands for serving the dashboard, updating to the latest version, and programmatically submitting training runs.

For the first release I intend to have all of the features implemented except for, possibly, the **slurm**-like resource manager and job queueing system, as that may become quite complex.

## Dependencies

AllenNLP and Python 3.6 or 3.7.

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

## Configuration

A project is customized through the `Project.toml` file in the root directory of the project. There is a section `[project]` for general options such as the log level (which applies to both the CLI and the dashboard) and a `[server]` section for dashboard-specific options such as the host port to bind to.

For convenience, you can open the configuration file quickly with the command `mallennlp edit`.

### Advanced configuration

#### Adding custom pages

Dashboard pages are just registered subclasses of `mallennlp.dashboard.page.Page`, which is an AllenNLP `Registrable`. Therefore you can easily add more pages to the dashboard by registering your own `Page` implementations. The registered name of a page corresponds to its URL route. For example, the home page is registered under the name "/" and the system info page is registered under the name "/sys-info". At a bare minimum, a custom `Page` just needs to implement `Page.get_elements(self)`, which renders the layout of the page. This can return anything that `Dash` can render, such as basic types as well as any `Dash` components (such as [HTML Components](https://dash.plot.ly/dash-html-components) or [Core Components](https://dash.plot.ly/dash-core-components)). For more information check out the [Dash Tutorial](https://dash.plot.ly/).

Here's how you would add a page that just says "Hello, World!" in the body:

```python
# hello_world/__init__.py
from mallennlp.dashboard.page import Page

@Page.register("/hello-world")
class HelloWorld(Page):
    requires_login = True
    navlink_name = "Hello, World!"

    def get_elements(self):
        return ["Hello, World!"]
```

You can put the `hello_world` module in the root of your project directory, or just make sure it's in your `PYTHONPATH`. Then add `imports = ['hello_world']` under the `[server]` section of the `Project.toml` configuration file. Now you should see a link "Hello, World!" to your page in the dropdown menu.

#### Interactive custom pages

`Page` instances have two attributes, an arbitrary `SessionState` object (`self.s`) and a `Params` object (`self.p`) that holds any typed URL parameters for the page, if they have been defined. By default the `SessionState` and `Params` object don't have any attributes. Overriding these with a custom `SessionState` or `Params` object looks like this:

```python
from mallennlp.dashboard.page import Page
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url

@Page.register("/hello-world")
class HelloWorld(Page):

    @serializable
    class SessionState:
        name: str = "World!"

    @from_url
    @serializable
    class Params:
        initial_message: str = "Hello, World!"

    # ... snip ...
```

Both `SessionState` and `Params` need to be serializable, which is ensured by the `@serializable` decorator. The decorator is really just a wrapper around [`attr.s`](https://www.attrs.org/en/stable/index.html) while adding some additional helper methods. The `@from_url` decorator adds a classmethod to the `Params` object that parses the attributes from a URL string.

Your page then becomes interactive when you implement a callback method for any input components that were created in `Page.get_elements`. Page callbacks are defined by decorating a `Page` method with `@Page.callback`. Under the hood, callbacks are just [Dash callbacks](https://dash.plot.ly/getting-started-part-2) with some magic behind the scenes that makes the function into an instance method of your page.

Combining these concepts, we can easily add to our `HelloWorld` to make it interactive:

```python
# hello_world/__init__.py
#
# The page will render a different initial message based on the URL parameter
# 'initial_message' and then update the message when the user types into the text input
# and uses the buttons.

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/hello-world")
class HelloWorld(Page):
    requires_login = True
    navlink_name = "Hello, World!"

    @serializable
    class SessionState:
        name: str = "World!"

    @from_url
    @serializable
    class Params:
        initial_message: str = "Hello, World!"

    def get_elements(self):
        return [
            dbc.Input(
                placeholder="Enter your name", type="text", id="hello-name-input"
            ),
            html.Br(),
            dbc.Button("Save", id="hello-name-save", color="primary"),
            html.Br(),
            dbc.Button("Say hello", id="hello-name-trigger-output", color="primary"),
            html.Br(),
            html.Div(id="hello-name-output", children=self.p.initial_message),
        ]

    @Page.callback(
        [], [Input("hello-name-save", "n_clicks")], [State("hello-name-input", "value")]
    )
    def save_name(self, n_clicks, value):
        if not n_clicks or not value:
            raise PreventUpdate
        self.s.name = value  # update SessionState

    @Page.callback(
        [Output("hello-name-output", "children")],
        [Input("hello-name-trigger-output", "n_clicks")],
        mutating=False,  # callback doesn't change the session state.
    )
    def render_hello_output(self, n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return f"Hello, {self.s.name}!"
```

#### Command completion

Since the CLI is implemented using Click, [setting up completion for Bash or ZSH](https://click.palletsprojects.com/en/7.x/bashcomplete/) is easy. For example,
you can just add

```
eval "$(_MALLENNLP_COMPLETE=source mallennlp)"
```

to your `.bashrc`. Note however that it is better to use the [activation script approach](https://click.palletsprojects.com/en/7.x/bashcomplete/#activation-script) instead, otherwise your shell may take a couple seconds to start.

## For potential contributors

I chose to implement this project entirely in Python to make it as easy possible for anyone to contribute, since if you are using AllenNLP you must already be familiar with Python. The dashboard is built with [plotly Dash](https://plot.ly/dash/), which is kind of like Python's version of [Shiny](https://shiny.rstudio.com/) if you're familiar with R.

The continuous integration for **allennlp-manager** is a lot like that of **AllenNLP**. Unit tests are run with [pytest](https://docs.pytest.org/en/latest/), code is type-checked with [mypy](http://mypy-lang.org/), linted with [flake8](http://flake8.pycqa.org/en/latest/), and formatted with [black](https://pypi.org/project/black/). You can run all of the CI-steps locally with `make test`.

If this is your first time contributing to a project on GitHub, please see [this Gist](https://gist.github.com/epwalsh/9e1b77d46ec232d55e6e344bb649fb19) for an example workflow.

## Updates

**11/19**

Numerous bug fixes and improvements. Added configurable pre/post/error callback hooks.

**11/18**

Added support for static/class method callbacks. Improved index page with notifications and implemented the "Re-build database" button.

**11/15**

Big updates. Implemented home page of dashboard with searchable table of all experiments. Uses server-side paging, caching, filtering, sorting, etc, so should scale well.

**11/12**

Adding customizable typed parameter parsing to `Page` class.

**11/8**

Made dashboard extendable, improved statefulness of `Page` class. Added caching to webserver.

**11/7**

Big improvements to the CLI and dashboard. Added [system info page](https://user-images.githubusercontent.com/8812459/68428301-c01f8200-0160-11ea-871a-7d9a83b21637.png) to dashboard.

**11/6**

Added sqlite database and implemented login / authentication system.

**11/5**

Dashboard skeleton implemented with `Page` abstraction.

**11/4**

CLI implemented (using click). Project can be created with `mallennlp new [PROJECT NAME]` and dashboard can be served with `mallennlp serve` from within the project directory (dashboard just returns 'Hello from AllenNLP manager' at the moment).
