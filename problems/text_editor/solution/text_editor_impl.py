from __future__ import annotations

from text_editor import TextEditor


class Document:
    def __init__(self):
        self.text = ""
        self.cursor = 0
        self.selection: tuple[int, int] | None = None
        self.undo_stack: list[tuple[str, int]] = []   # (text, cursor) before each change
        self.redo_stack: list[tuple[str, int]] = []   # (text, cursor) after each undone change


class TextEditorImpl(TextEditor):

    def __init__(self):
        self.docs: dict[str, Document] = {"untitled": Document()}
        self.current = "untitled"
        self.clipboard = ""

    @property
    def doc(self) -> Document:
        return self.docs[self.current]

    # ---- the one place where text changes -------------------------------------
    def _replace(self, start: int, end: int, new: str, cursor_after: int) -> str:
        d = self.doc
        text = d.text[:start] + new + d.text[end:]
        if text != d.text:                           # only real changes are undoable
            d.undo_stack.append((d.text, d.cursor))
            d.redo_stack.clear()
            d.text = text
            d.cursor = cursor_after
        d.selection = None
        return d.text

    def _clamp(self, p: int) -> int:
        return max(0, min(p, len(self.doc.text)))

    # ---- Level 1 ---------------------------------------------------------------
    def insert(self, text: str) -> str:
        d = self.doc
        start, end = d.selection or (d.cursor, d.cursor)
        return self._replace(start, end, text, start + len(text))

    def move_cursor(self, position: int) -> str:
        self.doc.cursor = self._clamp(position)
        self.doc.selection = None
        return self.doc.text

    def delete_forward(self) -> str:
        d = self.doc
        if d.selection:
            start, end = d.selection
            return self._replace(start, end, "", start)
        return self._replace(d.cursor, min(d.cursor + 1, len(d.text)), "", d.cursor)

    def backspace(self) -> str:
        d = self.doc
        if d.selection:
            start, end = d.selection
            return self._replace(start, end, "", start)
        start = max(d.cursor - 1, 0)
        return self._replace(start, d.cursor, "", start)

    def get_cursor(self) -> int:
        return self.doc.cursor

    # ---- Level 2 ---------------------------------------------------------------
    def select(self, left: int, right: int) -> str:
        d = self.doc
        left, right = sorted((self._clamp(left), self._clamp(right)))
        d.cursor = right
        d.selection = (left, right) if left < right else None
        return d.text[left:right]

    def copy(self) -> str:
        d = self.doc
        if d.selection:
            start, end = d.selection
            self.clipboard = d.text[start:end]
        return self.clipboard

    def paste(self) -> str:
        return self.insert(self.clipboard)

    # ---- Level 3 ---------------------------------------------------------------
    def undo(self) -> str:
        d = self.doc
        if d.undo_stack:
            d.redo_stack.append((d.text, d.cursor))
            d.text, d.cursor = d.undo_stack.pop()
        d.selection = None
        return d.text

    def redo(self) -> str:
        d = self.doc
        if d.redo_stack:
            d.undo_stack.append((d.text, d.cursor))
            d.text, d.cursor = d.redo_stack.pop()
        d.selection = None
        return d.text

    # ---- Level 4 ---------------------------------------------------------------
    def create_document(self, name: str) -> bool:
        if name in self.docs:
            return False
        self.docs[name] = Document()
        return True

    def switch_document(self, name: str) -> str | None:
        if name not in self.docs:
            return None
        self.current = name
        return self.doc.text
