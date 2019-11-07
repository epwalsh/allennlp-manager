import dash_html_components as html

from mallennlp.dashboard.page import Page


@Page.register("/")
class IndexPage(Page):
    def get_elements(self):
        return [html.H3("Home")]
