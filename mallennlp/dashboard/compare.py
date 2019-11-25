from typing import List

import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import url_params


@Page.register("/compare")
class ComparePage(Page):
    @url_params
    @serializable
    class Params:
        paths: List[str]

    def get_elements(self):
        return [html.H3("Comparing experiments")]
