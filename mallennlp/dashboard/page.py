from typing import Any, Dict, List, Union, Optional

from allennlp.common.registrable import Registrable
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


class Page(Registrable):
    requires_login = True
    """
    Should the page require that the user be logged in to view it?
    """

    navlink_name: Optional[str] = None
    """
    If set, this page will have a link in the navbar by this name.
    """

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

    def __init__(self, state, params):
        self.s = state
        self.p = params

    def render(self) -> html.Div:
        store = self.to_store()
        return html.Div(
            [dcc.Store(id=self._store_name, data=store)]
            + [dcc.Store(id=s, data=store) for s in self._callback_stores]
            + self.get_elements()
        )

    def get_elements(self) -> List[Any]:
        raise NotImplementedError

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

    @staticmethod
    def callback(
        outputs: Union[List[Output], Output],
        inputs: List[Input] = None,
        states: List[State] = None,
    ):
        if not isinstance(outputs, list):
            outputs = [outputs]
        inputs = inputs or []
        states = states or []

        def mark_callback(method):
            method.is_callback = True
            method.callback_parameters = (outputs, inputs, states)
            return method

        return mark_callback
