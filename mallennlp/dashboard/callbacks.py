from uuid import uuid4
import inspect
import time
from typing import Type, Callable, Any, Tuple, Iterable
from dash import Dash
from dash.dependencies import Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from mallennlp.dashboard.page import Page, PreHookType, PostHookType, ErrHookType


def uuid():
    """Generate unique id for a callback call in UUID4 format."""
    return str(uuid4())


def handle_callback_error(
    PageClass: Type[Page],
    method: Callable[..., Any],
    method_name: str,
    n_outputs: int,
    e: Exception,
):
    """
    Handle errors that occur during a callback.
    """
    noti = dbc.Toast(
        str(e),
        header=e.__class__.__name__,
        icon="danger",
        id=f"page-{PageClass.route}-{method_name}-callback-error-noti",
        dismissable=True,
        duration=4000,
    )
    return tuple(None for _ in range(n_outputs)) + (noti,)


def dispatch_pre_hooks(
    PageClass: Type[Page],
    method: Callable[..., Any],
    method_name: str,
    callback_id: str,
    args: Tuple[Any, ...],
):
    hooks: Iterable[PreHookType] = getattr(method, "pre_hooks", None) or []
    for hook in hooks:
        hook(PageClass, method_name, callback_id, args)


def dispatch_post_hooks(
    PageClass: Type[Page],
    method: Callable[..., Any],
    method_name: str,
    callback_id: str,
    args: Tuple[Any, ...],
    elapsed_time: float,
    retval: Any,
):
    hooks: Iterable[PostHookType] = getattr(method, "post_hooks", None) or []
    for hook in hooks:
        hook(PageClass, method_name, callback_id, args, elapsed_time, retval)


def dispatch_err_hooks(
    PageClass: Type[Page],
    method: Callable[..., Any],
    method_name: str,
    callback_id: str,
    args: Tuple[Any, ...],
    e: Exception,
):
    hooks: Iterable[ErrHookType] = getattr(method, "err_hooks", None) or []
    for hook in hooks:
        hook(PageClass, method_name, callback_id, args, e)


def make_static_callback(
    PageClass: Type[Page], method: Callable[..., Any], method_name: str, n_outputs: int
):
    """
    Create a Dash callback from a staticmethod Page callback.
    """

    def callback(*args):
        callback_id = uuid()
        start_time = time.time()
        try:
            dispatch_pre_hooks(PageClass, method, method_name, callback_id, args)
            result = getattr(PageClass, method_name)(*args)
            elapsed_time = time.time() - start_time
            dispatch_post_hooks(
                PageClass, method, method_name, callback_id, args, elapsed_time, result
            )
        except PreventUpdate:
            raise
        except Exception as e:
            dispatch_err_hooks(PageClass, method, method_name, callback_id, args, e)
            return handle_callback_error(PageClass, method, method_name, n_outputs, e)
        if n_outputs == 0:
            return (None,)
        if not isinstance(result, tuple):
            return (result, None)
        return result + (None,)

    return callback


def make_class_callback(
    PageClass: Type[Page], method: Callable[..., Any], method_name: str, n_outputs: int
):
    """
    Create a Dash callback from a classmethod Page callback.
    """

    def callback(*args):
        callback_id = uuid()
        start_time = time.time()
        try:
            dispatch_pre_hooks(PageClass, method, method_name, callback_id, args)
            result = getattr(PageClass, method_name)(*args)
            elapsed_time = time.time() - start_time
            dispatch_post_hooks(
                PageClass, method, method_name, callback_id, args, elapsed_time, result
            )
        except PreventUpdate:
            raise
        except Exception as e:
            dispatch_err_hooks(PageClass, method, method_name, callback_id, args, e)
            return handle_callback_error(PageClass, method, method_name, n_outputs, e)
        if n_outputs == 0:
            return (None,)
        if not isinstance(result, tuple):
            return (result, None)
        return result + (None,)

    return callback


def make_non_mutating_callback(
    PageClass: Type[Page], method: Callable[..., Any], method_name: str, n_outputs: int
):
    """
    Create a Dash callback from a non-mutating Page callback.
    """

    def callback(*args):
        args, store = args[:-1], args[-1]
        callback_id = uuid()
        start_time = time.time()
        try:
            dispatch_pre_hooks(PageClass, method, method_name, callback_id, args)
            page = PageClass.from_store(store)
            result = getattr(page, method_name)(*args)
            elapsed_time = time.time() - start_time
            dispatch_post_hooks(
                PageClass, method, method_name, callback_id, args, elapsed_time, result
            )
        except PreventUpdate:
            raise
        except Exception as e:
            dispatch_err_hooks(PageClass, method, method_name, callback_id, args, e)
            return handle_callback_error(PageClass, method, method_name, n_outputs, e)
        if n_outputs == 0:
            return (None,)
        if not isinstance(result, tuple):
            return (result, None)
        return result + (None,)

    return callback


def make_mutating_callback(
    PageClass: Type[Page], method: Callable[..., Any], method_name: str, n_outputs: int
):
    """
    Create a Dash callback from a mutating Page callback.
    """

    def callback(*args):
        args, store = args[:-1], args[-1]
        callback_id = uuid()
        start_time = time.time()
        try:
            dispatch_pre_hooks(PageClass, method, method_name, callback_id, args)
            page = PageClass.from_store(store)
            result = getattr(page, method_name)(*args)
            new_store = page.to_store()
            if new_store == store:
                # Callback did not mutate the session state, no need to update the store.
                new_store = None
            elapsed_time = time.time() - start_time
            dispatch_post_hooks(
                PageClass, method, method_name, callback_id, args, elapsed_time, result
            )
        except PreventUpdate:
            raise
        except Exception as e:
            dispatch_err_hooks(PageClass, method, method_name, callback_id, args, e)
            return handle_callback_error(PageClass, method, method_name, n_outputs, e)
        if n_outputs == 0:
            return (new_store, None)
        if not isinstance(result, tuple):
            return (result, new_store, None)
        return result + (new_store, None)

    return callback


def store_callback(*args):
    """
    Update the Page store from the latest Page callback store.
    """
    half = len(args) // 2
    timestamps, datas = args[:half], args[half:]
    latest_index = max(range(len(datas)), key=lambda i: timestamps[i] or -1)
    latest = datas[latest_index]
    if latest is None:
        raise PreventUpdate
    return latest


def register_callbacks(dash: Dash, PageClass: Type[Page], method: Callable[..., Any]):
    outputs, inputs, states = method.callback_parameters  # type: ignore
    n_outputs = len(outputs)
    method_name = method.__name__
    Page.logger.debug(
        "registering callback %s.%s (%s, %s) -> %s",
        PageClass.__name__,
        method_name,
        inputs,
        states,
        outputs,
    )
    if isinstance(inspect.getattr_static(PageClass, method_name), staticmethod):
        # Callback is staticmethod.
        callback = make_static_callback(PageClass, method, method_name, n_outputs)
    elif isinstance(inspect.getattr_static(PageClass, method_name), classmethod):
        # Callback is classmethod.
        callback = make_class_callback(PageClass, method, method_name, n_outputs)
    elif not method.is_mutating:  # type: ignore
        # Callback is non-mutating instance method.
        callback = make_non_mutating_callback(PageClass, method, method_name, n_outputs)
        # Add session store to states.
        states.append(State(PageClass._store_name, "data"))
    else:
        # Callback is mutating instance method.
        callback = make_mutating_callback(PageClass, method, method_name, n_outputs)
        # Collect callback store and add to outputs.
        callback_store_name = PageClass._store_name + f"-callback-{method_name}"
        PageClass._callback_stores.append(callback_store_name)
        outputs.append(Output(callback_store_name, "data"))
        # Add session store to states.
        states.append(State(PageClass._store_name, "data"))

    # Collect callback's error div and add to the output.
    error_div_name = f"page-{PageClass.route}-error-div-{method_name}"
    PageClass._callback_error_divs.append(error_div_name)
    outputs.append(Output(error_div_name, "children"))

    # Register callback.
    dash.callback(outputs, inputs, states)(callback)
