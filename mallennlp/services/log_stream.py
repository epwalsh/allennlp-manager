from pathlib import Path
from typing import List, Optional

import attr

from mallennlp.services.serialization import Serializable


@attr.s(auto_attribs=True)
class LogStreamService(Serializable):
    path: str
    """
    Path to the log file to stream.
    """

    _lines: List[str] = attr.ib(default=attr.Factory(list))
    """
    Keeps track of current lines.
    """

    _current_line: str = ""
    """
    Keeps track of partial line being read until entire line has been read.
    """

    _position: Optional[int] = None
    """
    Keeps track of current position in the file.
    """

    _at_eof: bool = False
    """
    At EOF or not.
    """

    _last_modified: Optional[float] = None

    max_lines: int = 500
    """
    Maximum number of lines to display.
    """

    max_lines_per_update: int = 50
    """
    Approximate maximum number of lines to read per update. The actual number of lines
    read per update may be greater. How much so depends on the number
    of characters per line and the block size of each read (limited by `max_block_size`).

    To keep the actual number of lines read close to `max_lines_per_update`, keep
    `max_block_size` small and `max_blocks_per_update` large. The trade-off is
    performance (more small reads have to be done).
    """

    max_blocks_per_update: int = 128 * 10
    """
    Maximum number of blocks to read per update.
    """

    max_block_size: int = 8
    """
    Max number of characters to read per block.
    """

    def _should_read(self) -> bool:
        if not self._at_eof:
            return True
        path = Path(self.path)
        if self._last_modified is None:
            self._last_modified = path.stat().st_mtime
            return True
        tmp = self._last_modified
        self._last_modified = path.stat().st_mtime
        return tmp < self._last_modified

    def readlines(self) -> List[str]:
        if not self._should_read():
            return self._lines
        with open(self.path) as f:
            if self._position is not None:
                f.seek(self._position)
            n_lines = 0
            n_blocks = 0
            # Read block-by-block until we reach the end of the file or
            # either `n_lines >= self.max_lines_per_update` or
            # `n_blocks >= self.max_blocks_per_update `.
            for block in iter(lambda: f.read(self.max_block_size), None):
                n_blocks += 1
                if block:
                    for line in (self._current_line + block).splitlines(True):
                        if line.endswith("\n"):
                            # We have a complete line.
                            n_lines += 1
                            self._lines.append(line.strip())
                            self._current_line = ""
                        else:
                            # Incomplete line.
                            self._current_line = line
                    if n_lines >= self.max_lines_per_update:
                        break
                    if n_blocks >= self.max_blocks_per_update:
                        break
                else:
                    break
            self._position = f.tell()
            self._lines = self._lines[-self.max_lines :]
            # Peek one more character to see if we're at EOF.
            self._at_eof = not bool(f.read(1))
        return self._lines
