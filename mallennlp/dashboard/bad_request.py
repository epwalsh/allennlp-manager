from typing import List, Dict

import attr
import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.domain.page_state import PageSessionState


@Page.register("/400-bad-request")
class BadRequestPage(Page):
    @attr.s(auto_attribs=True)
    class SessionState(PageSessionState):
        e: str

        @classmethod
        def from_params(cls, params: Dict[str, List[str]]):
            return cls(params["e"][0])

    def get_elements(self):
        return [html.H3(f"400: {self.s.e}")]
