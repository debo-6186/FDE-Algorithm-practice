from interface import TextEditor

class TextEditorImpl(TextEditor):

    def __init__(self):
        self.text: str = ""
        self.cursor: int = 0
        self.selection: str = ""
        self.clipboard: str = ""
        self.sel_start: int | None = None
        self.sel_end: int | None = None

    # @@LEVEL 1@@
    def insert(self, text: str) -> str:
        """
        Should insert `text` at the cursor and return the document text.
        """
        if self.sel_start is not None:
            self.text = self.text[:self.sel_start] + text + self.text[self.sel_end:]
            self.cursor = self.sel_start + len(text)
        else:
            self.text = self.text[:self.cursor] + text + self.text[self.cursor:]
            self.cursor += len(text)
        self.sel_start = None
        self.sel_end = None
        self.selection = ""
        return self.text

    def move_cursor(self, position: int) -> str:
        """
        Should move the cursor (clamped) and return the document text.
        """
        self.cursor = max(0, min(position, len(self.text)))
        self.sel_start = None
        self.sel_end = None
        self.selection = ""
        return self.text

    def delete_forward(self) -> str:
        """
        Should delete the character after the cursor; returns the document text.
        """
        if self.sel_start is not None:
            self.text = self.text[:self.sel_start] + self.text[self.sel_end:]
            self.cursor = self.sel_start
        elif self.cursor < len(self.text):
            self.text = self.text[:self.cursor] + self.text[self.cursor+1:]

        self.sel_start = None
        self.sel_end = None
        self.selection = ""
        return self.text


    def backspace(self) -> str:
        """
        Should delete the character before the cursor; returns the document text.
        """
        if self.sel_start is not None:
            self.text = self.text[:self.sel_start] + self.text[self.sel_end:]
            self.cursor = self.sel_start
        elif self.cursor > 0:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor -= 1
        self.sel_start = None
        self.sel_end = None
        self.selection = ""
        return self.text
        

    def get_cursor(self) -> int:
        """
        Should return the cursor position.
        """
        return self.cursor

    # @@LEVEL 2@@
    def select(self, left: int, right: int) -> str:
        """
        Should select text between `left` and `right` and return it.
        """
        left = max(0, min(left, len(self.text)))
        right = max(0, min(right, len(self.text)))
        if left > right:
            left, right = right, left
        self.cursor = right
        if left == right:
            self.sel_start = None
            self.sel_end = None
            self.selection = ""
        else:
            self.sel_start = left
            self.sel_end = right
            self.selection = self.text[left:right]
        return self.selection

    def copy(self) -> str:
        """
        Should copy the selection to the clipboard and return the clipboard.
        """
        if self.selection != "":
            self.clipboard = self.selection
        return self.clipboard

    def paste(self) -> str:
        """
        Should insert the clipboard content and return the document text.
        """
        return self.insert(self.clipboard)