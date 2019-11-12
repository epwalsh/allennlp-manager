import dash_html_components as html

from mallennlp.services.log_stream import Line


def format_log_line(line: Line):
    return html.Pre(f"{line.number}:  {line.content}")
