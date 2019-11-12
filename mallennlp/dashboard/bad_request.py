import dash_html_components as html

from mallennlp.dashboard.page import Page
from mallennlp.services.serialization import serializable
from mallennlp.services.url_parse import from_url


@Page.register("/400-bad-request")
class BadRequestPage(Page):
    @from_url
    @serializable
    class Params:
        e: str

    def get_elements(self):
        return [html.H3(f"400: {self.p.e}")]
