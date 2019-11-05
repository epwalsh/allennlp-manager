import dash_html_components as html

from mallennlp.dashboard.page import Page


@Page.register("/not-found")
class NotFoundPage(Page):
    def get_elements(self):
        return [html.H3("404: The page you were looking doesn't exist")]
