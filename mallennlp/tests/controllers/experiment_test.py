import pytest

from mallennlp.controllers.experiment import parse_filters


@pytest.mark.parametrize(
    "filter_expression, result",
    [
        ("{path} contains greetings/*", ("path GLOB ?", ["greetings/*"])),
        ("{path} contains greetings/* ", ("path GLOB ?", ["greetings/*"])),
        (
            "{path} contains greetings/* && {tags} contains copynet seq2seq",
            (
                "path GLOB ? AND HasAllTags(tags, ?, ?)",
                ["greetings/*", "copynet", "seq2seq"],
            ),
        ),
    ],
)
def test_parse_filters(filter_expression, result):
    assert parse_filters(filter_expression) == result
