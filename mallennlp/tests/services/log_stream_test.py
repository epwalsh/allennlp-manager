from pathlib import Path

from mallennlp.services.log_stream import LogStreamService


def test_stream_stdout_log():
    path = Path("mallennlp/tests/fixtures/test_experiment/stdout.log")
    with open(path) as f:
        all_lines = [l.strip() for l in f]
    s = LogStreamService(
        str(path),
        max_lines=100,
        max_lines_per_update=50,
        max_blocks_per_update=128 * 10,
        max_block_size=8,
    )
    assert s.should_read()

    # Just make sure this was initialized correctly with the attr factory.
    assert isinstance(s._lines, list)

    # First read, lines 1 - 50.
    lines = s.readlines()
    assert len(lines) == s.max_lines_per_update
    assert lines[0].content == all_lines[0]
    assert lines[-1].content == all_lines[49]

    # Second read, lines 1 - 100.
    lines = s.readlines()
    assert len(lines) == s.max_lines
    assert lines[0].content == all_lines[0]
    assert lines[-1].content == all_lines[99]

    # Third read, lines 51 - 150.
    lines = s.readlines()
    assert len(lines) == s.max_lines
    assert lines[0].content == all_lines[50]
    assert lines[-1].content == all_lines[149]

    # Read until the end (415 lines).
    s.readlines()  # lines 101 - 200.
    s.readlines()  # lines 151 - 250.
    s.readlines()  # lines 201 - 300.
    s.readlines()  # lines 251 - 350.
    s.readlines()  # lines 301 - 400.
    lines = s.readlines()  # lines 316 - 415.
    assert len(lines) == s.max_lines
    assert lines[0].content == all_lines[315]
    assert lines[-1].content == all_lines[414]

    # Result should be the same still.
    lines = s.readlines()  # lines 316 - 415.
    assert len(lines) == s.max_lines
    assert lines[0].content == all_lines[315]
    assert lines[-1].content == all_lines[414]

    # Shouldn't have to read again.
    assert s._at_eof
    assert not s.should_read()
    path.touch()
    assert s.should_read()


def test_small_lines_bigger_block_size():
    """
    Ensures files with lines with less bytes than the block size are streamed properly.
    """
    path = "mallennlp/tests/fixtures/test_log_streams/small_line_file.log"
    with open(path) as f:
        all_lines = [l.strip() for l in f]
    s = LogStreamService(
        path,
        max_lines=5,
        max_lines_per_update=1,
        max_blocks_per_update=1,
        max_block_size=4,
    )
    lines = s.readlines()
    assert [l.content for l in lines] == all_lines[0:2]
    lines = s.readlines()
    assert [l.content for l in lines] == all_lines[0:5]


def test_small_lines_block_size_1():
    path = "mallennlp/tests/fixtures/test_log_streams/small_line_file.log"
    with open(path) as f:
        all_lines = [l.strip() for l in f]
    s = LogStreamService(
        path,
        max_lines=5,
        max_lines_per_update=1,
        max_blocks_per_update=1,
        max_block_size=1,
    )
    lines = s.readlines()
    assert lines == []
    lines = s.readlines()
    assert [l.content for l in lines] == all_lines[0:1]
