from logging import Logger
from typing import Any, Dict, List, Optional, Tuple, Callable, Iterable

from allennlp.common.registrable import Registrable
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


PreHookType = Callable[[str, str, List[Any]], None]
PostHookType = Callable[[str, str, List[Any], Any], None]
ErrHookType = Callable[[str, str, List[Any], Exception], None]


class Page(Registrable):
    requires_login = True
    """
    Should the page require that the user be logged in to view it?
    """

    navlink_name: Optional[str] = None
    """
    If set, this page will have a link in the navbar by this name.
    """

    logger: Logger

    @serializable
    class SessionState:
        """
        If the page needs to be stateful within a session, the state class should be defined here.
        The state instance will then be available as `self.s`.
        """

        pass

    @from_url
    @serializable
    class Params:
        """
        If the page needs parameters from the URL they should be defined here.

        An instance of this class will then be passed to `Page.from_params` when
        initializing the page.
        """

        pass

    _store_name: str
    _callback_stores: List[str]
    _callback_error_divs: List[str]

    def __init__(self, state, params):
        self.s = state
        self.p = params

    def render(self) -> Tuple[html.Div, List[html.Div], List[Any]]:
        # Call this before `self.store()` in case `self.get_elements` modifies state.
        elements = self.get_elements()
        notifications = self.get_notifications()
        store = self.to_store()
        return (
            html.Div(
                [dcc.Store(id=self._store_name, data=store)]
                + [dcc.Store(id=s, data=store) for s in self._callback_stores]
                + elements
            ),
            [html.Div(id=e) for e in self._callback_error_divs],
            notifications,
        )

    def get_elements(self) -> List[Any]:
        raise NotImplementedError

    def get_notifications(self) -> List[Any]:
        return []

    @classmethod
    def from_params(cls, params):
        return cls(cls.SessionState(), params)

    @classmethod
    def from_store(cls, data: Dict[str, Any]):
        s = cls.SessionState.deserialize(data["s"])  # type: ignore
        p = cls.Params.deserialize(data["p"])  # type: ignore
        return cls(s, p)

    def to_store(self) -> Dict[str, Any]:
        return {"s": self.s.serialize(), "p": self.p.serialize()}

    @classmethod
    def default_pre_hooks(cls) -> Tuple[PreHookType, ...]:
        def debug(page_name: str, method_name: str, args: List[Any]):
            cls.logger.debug(
                "Page '%s' received callback %s%s", page_name, method_name, args
            )

        return (debug,)

    @classmethod
    def default_post_hooks(cls) -> Tuple[PostHookType, ...]:
        def debug(page_name: str, method_name: str, args: List[Any], retval: Any):
            cls.logger.debug(
                "Page '%s' handled callback %s%s -> %s",
                page_name,
                method_name,
                args,
                retval,
            )

        return (debug,)

    @classmethod
    def default_err_hooks(cls) -> Tuple[ErrHookType, ...]:
        def debug(page_name: str, method_name: str, args: List[Any], e: Exception):
            cls.logger.exception(e)

        return (debug,)

    @classmethod
    def callback(
        cls,
        outputs: List[Output] = None,
        inputs: List[Input] = None,
        states: List[State] = None,
        mutating: bool = True,
        pre_hooks: Iterable[PreHookType] = None,
        post_hooks: Iterable[PostHookType] = None,
        err_hooks: Iterable[ErrHookType] = None,
    ):
        """
        Register a Page callback.

        Parameters
        ----------
        outputs : ``List[Output]``, default = None
            A list (possibly empty) of outputs to update on the return of the callback.
            If given and non-empty, the number of outputs should equal the number of return
            values of the function.

        inputs : ``List[Input]``, default = None
            Input dependencies of the callback. The number of inputs + states is equal
            to the number of argument the callback should accept (ignore ``self`` or ``cls``).

        states : ``List[State]``, default = None
            State dependencies of the callback. The number of inputs + states is equal
            to the number of argument the callback should accept (ignore ``self`` or ``cls``).

        mutating : ``bool``, default = True
            Only relevant to an instance method callback. If ``True``, the ``Page``'s
            session state will be updated after the callback method returns.

        pre_hooks : ``Iterable[PreHookType]``
            Functions to run right before a callback executes.

        post_hooks : ``Iterable[PostHookType]``
            Functions to run right after a callback successfully executes.

        err_hooks : ``Iterable[ErrHookType]``
            Functions to run after a callback fails.

        """
        if not outputs:
            outputs = []
        elif not isinstance(outputs, list):
            outputs = [outputs]
        inputs = inputs or []
        states = states or []

        pre_hooks = cls.default_pre_hooks() if pre_hooks is None else pre_hooks
        post_hooks = cls.default_post_hooks() if post_hooks is None else post_hooks
        err_hooks = cls.default_err_hooks() if err_hooks is None else err_hooks

        def mark_callback(method):
            method.is_callback = True
            method.is_mutating = mutating
            method.callback_parameters = (outputs, inputs, states)
            method.pre_hooks = pre_hooks
            method.post_hooks = post_hooks
            method.err_hooks = err_hooks
            return method

        return mark_callback
