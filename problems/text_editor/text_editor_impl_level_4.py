from interface import TextEditor


class _Document:
    def __init__(self):
        self.text: str = ""
        self.cursor_position: int = 0
        self.selection: tuple[int, int] | None = None
        self.undo_stack: list[tuple[str, int]] = []
        self.redo_stack: list[tuple[str, int]] = []


class TextEditorImpl(TextEditor):

    def __init__(self):
        self.documents: dict[str, _Document] = {"untitled": _Document()}
        self.current_name: str = "untitled"
        self.clipboard: str = ""

    @property
    def _doc(self) -> _Document:
        return self.documents[self.current_name]

    @property
    def text(self) -> str:
        return self._doc.text

    @text.setter
    def text(self, value: str) -> None:
        self._doc.text = value

    @property
    def cursor_position(self) -> int:
        return self._doc.cursor_position

    @cursor_position.setter
    def cursor_position(self, value: int) -> None:
        self._doc.cursor_position = value

    @property
    def selection(self) -> tuple[int, int] | None:
        return self._doc.selection

    @selection.setter
    def selection(self, value: tuple[int, int] | None) -> None:
        self._doc.selection = value

    @property
    def undo_stack(self) -> list[tuple[str, int]]:
        return self._doc.undo_stack

    @property
    def redo_stack(self) -> list[tuple[str, int]]:
        return self._doc.redo_stack

    def _record_change(self, old_text: str, old_cursor: int):
        if self.text != old_text:
            self.undo_stack.append((old_text, old_cursor))
            self.redo_stack.clear()

    # @@LEVEL 1@@
    def insert(self, text: str) -> str:
        """
        Should insert `text` at the cursor and return the document text.
        """
        old_text, old_cursor = self.text, self.cursor_position
        start, end = self.selection or (self.cursor_position, self.cursor_position)
        self.text = self.text[:start] + text + self.text[end:]
        self.cursor_position = start + len(text)
        self.selection = None
        self._record_change(old_text, old_cursor)
        return self.text

    def move_cursor(self, position: int) -> str:
        """
        Should move the cursor (clamped) and return the document text.
        """
        self.cursor_position = max(0, min(position, len(self.text)))
        self.selection = None
        return self.text

    def delete_forward(self) -> str:
        """
        Should delete the character after the cursor; returns the document text.
        """
        old_text, old_cursor = self.text, self.cursor_position
        if self.selection:
            start, end = self.selection
            self.text = self.text[:start] + self.text[end:]
            self.cursor_position = start
        elif self.cursor_position < len(self.text):
            self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]
        self.selection = None
        self._record_change(old_text, old_cursor)
        return self.text

    def backspace(self) -> str:
        """
        Should delete the character before the cursor; returns the document text.
        """
        old_text, old_cursor = self.text, self.cursor_position
        if self.selection:
            start, end = self.selection
            self.text = self.text[:start] + self.text[end:]
            self.cursor_position = start
        elif self.cursor_position != 0:
            self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
            self.cursor_position -= 1
        self.selection = None
        self._record_change(old_text, old_cursor)
        return self.text

    def get_cursor(self) -> int:
        """
        Should return the cursor position.
        """
        return self.cursor_position

    # @@LEVEL 2@@
    def select(self, left: int, right: int) -> str:
        """
        Should select text between `left` and `right` and return it.
        """
        left = max(0, min(left, len(self.text)))
        right = max(0, min(right, len(self.text)))
        if left > right:
            left, right = right, left
        self.cursor_position = right
        self.selection = (left, right) if left < right else None
        return self.text[left:right]

    def copy(self) -> str:
        """
        Should copy the selection to the clipboard and return the clipboard.
        """
        if self.selection:
            start, end = self.selection
            self.clipboard = self.text[start:end]
        return self.clipboard

    def paste(self) -> str:
        """
        Should insert the clipboard content and return the document text.
        """
        return self.insert(self.clipboard)

    # @@LEVEL 3@@
    def undo(self) -> str:
        """
        Should revert the most recent change; returns the document text.
        """
        if self.undo_stack:
            self.redo_stack.append((self.text, self.cursor_position))
            self.text, self.cursor_position = self.undo_stack.pop()
        self.selection = None
        return self.text

    def redo(self) -> str:
        """
        Should re-apply the most recently undone change; returns the text.
        """
        if self.redo_stack:
            self.undo_stack.append((self.text, self.cursor_position))
            self.text, self.cursor_position = self.redo_stack.pop()
        self.selection = None
        return self.text

    # @@LEVEL 4@@
    def create_document(self, name: str) -> bool:
        """
        Should create a new empty document. `False` if it already exists.
        """
        if name in self.documents:
            return False
        self.documents[name] = _Document()
        return True

    def switch_document(self, name: str) -> str | None:
        """
        Should switch to document `name` and return its text, or `None`.
        """
        if name not in self.documents:
            return None
        self.current_name = name
        return self.text
