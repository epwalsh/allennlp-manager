from typing import Any, Dict, List, Union

from allennlp.common.registrable import Registrable
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


class Page(Registrable):
    requires_login = True
    store_name: str

    def render(self) -> html.Div:
        return html.Div(
            [dcc.Store(id=self.store_name, data=self.dump_store())]
            + self.get_elements()
        )

    def get_elements(self) -> List[Any]:
        raise NotImplementedError

    @classmethod
    def from_params(cls, params: Dict[str, Any]):
        return cls()

    @classmethod
    def from_store(cls, store: Dict[str, Any]):
        return cls(**store)

    def dump_store(self) -> Dict[str, Any]:
        return self.__dict__

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
