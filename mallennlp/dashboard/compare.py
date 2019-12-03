from typing import List

import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.services.serde import serde


@Page.register("/compare")
class ComparePage(Page):
    @serde
    class Params:
        paths: List[str]

    def get_elements(self):
        return [html.H3("Comparing experiments")]
