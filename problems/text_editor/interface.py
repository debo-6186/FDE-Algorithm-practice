from __future__ import annotations

from abc import ABC


class TextEditor(ABC):
    """
    `TextEditor` interface.
    Default implementations return placeholder values; override every method
    in `TextEditorImpl` (text_editor_impl.py).
    """

# @@LEVEL 1@@
    def insert(self, text: str) -> str:
        """
        Should insert `text` at the cursor and return the document text.
        """
        # default implementation
        return ""

    def move_cursor(self, position: int) -> str:
        """
        Should move the cursor (clamped) and return the document text.
        """
        # default implementation
        return ""

    def delete_forward(self) -> str:
        """
        Should delete the character after the cursor; returns the document text.
        """
        # default implementation
        return ""

    def backspace(self) -> str:
        """
        Should delete the character before the cursor; returns the document text.
        """
        # default implementation
        return ""

    def get_cursor(self) -> int:
        """
        Should return the cursor position.
        """
        # default implementation
        return -1

# @@LEVEL 2@@
    def select(self, left: int, right: int) -> str:
        """
        Should select text between `left` and `right` and return it.
        """
        # default implementation
        return ""

    def copy(self) -> str:
        """
        Should copy the selection to the clipboard and return the clipboard.
        """
        # default implementation
        return ""

    def paste(self) -> str:
        """
        Should insert the clipboard content and return the document text.
        """
        # default implementation
        return ""

# @@LEVEL 3@@
    def undo(self) -> str:
        """
        Should revert the most recent change; returns the document text.
        """
        # default implementation
        return ""

    def redo(self) -> str:
        """
        Should re-apply the most recently undone change; returns the text.
        """
        # default implementation
        return ""

# @@LEVEL 4@@
    def create_document(self, name: str) -> bool:
        """
        Should create a new empty document. `False` if it already exists.
        """
        # default implementation
        return False

    def switch_document(self, name: str) -> str | None:
        """
        Should switch to document `name` and return its text, or `None`.
        """
        # default implementation
        return None
