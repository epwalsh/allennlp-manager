from typing import Any, Dict, List, Union, Optional, Type

from allennlp.common.registrable import Registrable
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from mallennlp.services.serialization import Serializable


class Page(Registrable):
    requires_login = True
    """
    Should the page require that the user be logged in to view it?
    """

    navlink_name: Optional[str] = None
    """
    If set, this page will have a link in the navbar by this name.
    """

    SessionState: Type[Serializable] = Serializable
    """
    If the page needs to be stateful within a session, the state class should be defined here.
    The state instance will then be available as `self.s`.
    """

    _store_name: str
    _callback_stores: List[str]

    def __init__(self, state):
        self.s = state

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
    def from_params(cls, params: Dict[str, List[str]]):
        return cls(cls.SessionState())

    @classmethod
    def from_store(cls, data: Dict[str, Any]):
        s = cls.SessionState.decode(data["s"])
        return cls(s)

    def to_store(self) -> Dict[str, Any]:
        return {"s": self.s.encode()}

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
