"""Small, explicit VT state reader for the first terminal-channel slice.

This is a state reader, not a claim of complete terminal emulation.  It keeps
transport bytes separate from the native presentation witness and surfaces
unsupported control sequences instead of silently discarding them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re


CSI_FINAL_RE = re.compile(r"[\x40-\x7e]")


@dataclass
class VTScreenState:
    rows: int = 24
    cols: int = 80
    cursor_row: int = 0
    cursor_col: int = 0
    cursor_visible: bool = True
    alternate_screen: bool = False
    sgr: tuple[int, ...] = (0,)
    bytes_received: int = 0
    control_sequences: int = 0
    unsupported_sequences: list[str] = field(default_factory=list)
    _lines: list[list[str]] = field(init=False, repr=False)
    _primary_lines: list[list[str]] = field(init=False, repr=False)
    _saved_cursor: tuple[int, int] = field(default=(0, 0), init=False, repr=False)
    _escape_buffer: str = field(default="", init=False, repr=False)

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError("terminal_dimensions_must_be_positive")
        self._lines = self._blank_screen()
        self._primary_lines = self._blank_screen()

    def _blank_screen(self) -> list[list[str]]:
        return [[" "] * self.cols for _ in range(self.rows)]

    def _clamp_cursor(self) -> None:
        self.cursor_row = max(0, min(self.rows - 1, self.cursor_row))
        self.cursor_col = max(0, min(self.cols - 1, self.cursor_col))

    def resize(self, rows: int, cols: int) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("terminal_dimensions_must_be_positive")
        old_lines = self._lines
        old_primary = self._primary_lines
        self.rows, self.cols = rows, cols
        self._lines = self._resize_lines(old_lines)
        self._primary_lines = self._resize_lines(old_primary)
        self._clamp_cursor()

    def _resize_lines(self, old: list[list[str]]) -> list[list[str]]:
        lines = self._blank_screen()
        for row in range(min(self.rows, len(old))):
            for col in range(min(self.cols, len(old[row]))):
                lines[row][col] = old[row][col]
        return lines

    def feed(self, data: bytes | str) -> None:
        if isinstance(data, bytes):
            self.bytes_received += len(data)
            text = data.decode("utf-8", errors="replace")
        else:
            text = data
            self.bytes_received += len(data.encode("utf-8"))

        index = 0
        while index < len(text):
            if self._escape_buffer:
                consumed = self._consume_escape(text[index:])
                if consumed == 0:
                    index += 1
                else:
                    index += consumed
                continue
            char = text[index]
            if char == "\x1b":
                self._escape_buffer = "\x1b"
            elif char == "\n":
                self.cursor_row += 1
                self._scroll_if_needed()
            elif char == "\r":
                self.cursor_col = 0
            elif char == "\b":
                self.cursor_col = max(0, self.cursor_col - 1)
            elif char == "\t":
                self.cursor_col = min(self.cols - 1, ((self.cursor_col // 8) + 1) * 8)
            elif ord(char) >= 0x20 and char != "\x7f":
                self._put(char)
            index += 1

    def _consume_escape(self, text: str) -> int:
        sequence = self._escape_buffer
        if sequence == "\x1b":
            if not text:
                return 0
            first = text[0]
            if first == "[":
                self._escape_buffer = "\x1b["
                return 1
            if first == "]":
                self._escape_buffer = "\x1b]"
                return 1
            self._escape_buffer = ""
            self.control_sequences += 1
            if first == "7":
                self._saved_cursor = (self.cursor_row, self.cursor_col)
            elif first == "8":
                self.cursor_row, self.cursor_col = self._saved_cursor
                self._clamp_cursor()
            elif first == "c":
                self._lines = self._blank_screen()
                self.cursor_row = self.cursor_col = 0
            else:
                self._unsupported("\\x1b" + first)
            return 1

        if sequence == "\x1b]":
            bel = text.find("\x07")
            st = text.find("\x1b\\")
            end = min(value for value in (bel, st) if value >= 0) if (bel >= 0 or st >= 0) else -1
            if end < 0:
                self._escape_buffer += text
                return len(text)
            raw = self._escape_buffer + text[:end]
            self.control_sequences += 1
            self._unsupported(raw)
            self._escape_buffer = ""
            return end + (2 if st == end else 1)

        if sequence == "\x1b[":
            match = CSI_FINAL_RE.search(text)
            if match is None:
                self._escape_buffer += text
                return len(text)
            raw = self._escape_buffer + text[: match.end()]
            self.control_sequences += 1
            self._handle_csi(raw)
            self._escape_buffer = ""
            return match.end()

        self._escape_buffer = ""
        return 0

    def _handle_csi(self, raw: str) -> None:
        final = raw[-1]
        body = raw[2:-1]
        private = body.startswith("?")
        if private:
            body = body[1:]
        params = [int(value) if value else 0 for value in body.split(";") if value or body == ""]
        if not params:
            params = [0]

        if final in {"H", "f"}:
            row = params[0] if params[0] else 1
            col = params[1] if len(params) > 1 and params[1] else 1
            self.cursor_row, self.cursor_col = row - 1, col - 1
            self._clamp_cursor()
        elif final == "A":
            self.cursor_row -= params[0] or 1
            self._clamp_cursor()
        elif final == "B":
            self.cursor_row += params[0] or 1
            self._clamp_cursor()
        elif final == "C":
            self.cursor_col += params[0] or 1
            self._clamp_cursor()
        elif final == "D":
            self.cursor_col -= params[0] or 1
            self._clamp_cursor()
        elif final == "G":
            self.cursor_col = (params[0] or 1) - 1
            self._clamp_cursor()
        elif final == "J":
            self._erase_display(params[0])
        elif final == "K":
            self._erase_line(params[0])
        elif final == "m":
            self.sgr = tuple(params)
        elif final in {"h", "l"} and private:
            enabled = final == "h"
            for param in params:
                if param == 25:
                    self.cursor_visible = enabled
                elif param == 1049:
                    self._switch_alternate(enabled)
                else:
                    self._unsupported(raw)
        else:
            self._unsupported(raw)

    def _switch_alternate(self, enabled: bool) -> None:
        if enabled == self.alternate_screen:
            return
        if enabled:
            self._primary_lines = self._lines
            self._lines = self._blank_screen()
            self.cursor_row = self.cursor_col = 0
        else:
            self._lines = self._primary_lines
        self.alternate_screen = enabled
        self._clamp_cursor()

    def _erase_display(self, mode: int) -> None:
        if mode == 2:
            self._lines = self._blank_screen()
            self.cursor_row = self.cursor_col = 0
        elif mode == 0:
            self._erase_line(0)
            for row in range(self.cursor_row + 1, self.rows):
                self._lines[row] = [" "] * self.cols
        elif mode == 1:
            self._erase_line(1)
            for row in range(0, self.cursor_row):
                self._lines[row] = [" "] * self.cols
        else:
            self._unsupported(f"CSI {mode} J")

    def _erase_line(self, mode: int) -> None:
        if mode == 0:
            start, end = self.cursor_col, self.cols
        elif mode == 1:
            start, end = 0, self.cursor_col + 1
        elif mode == 2:
            start, end = 0, self.cols
        else:
            self._unsupported(f"CSI {mode} K")
            return
        self._lines[self.cursor_row][start:end] = [" "] * (end - start)

    def _put(self, char: str) -> None:
        self._lines[self.cursor_row][self.cursor_col] = char
        self.cursor_col += 1
        if self.cursor_col >= self.cols:
            self.cursor_col = 0
            self.cursor_row += 1
            self._scroll_if_needed()

    def _scroll_if_needed(self) -> None:
        if self.cursor_row < self.rows:
            return
        self._lines.pop(0)
        self._lines.append([" "] * self.cols)
        self.cursor_row = self.rows - 1

    def _unsupported(self, sequence: str) -> None:
        if sequence not in self.unsupported_sequences:
            self.unsupported_sequences.append(sequence)
        if len(self.unsupported_sequences) > 32:
            del self.unsupported_sequences[:-32]

    def text(self) -> str:
        return "\n".join("".join(line).rstrip() for line in self._lines).rstrip("\n")

    def to_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cursor": {"row": self.cursor_row, "col": self.cursor_col},
            "cursor_visible": self.cursor_visible,
            "alternate_screen": self.alternate_screen,
            "sgr": list(self.sgr),
            "bytes_received": self.bytes_received,
            "control_sequences": self.control_sequences,
            "unsupported_sequences": list(self.unsupported_sequences),
            "text": self.text(),
        }
