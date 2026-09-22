"""
Widgets for loading into an AppFrame or AppWindow: a Button class with
convenience constructors for common file-dialog patterns, and a Table
class (built on ttk.Treeview, Tkinter's only grid-style widget).
"""
from tkinter import filedialog, ttk
from layout import resolve_parent, place_widget

class Button:
    """
    Use Button(...) directly when you already have a callback function
    to run. Use the alternate constructors below (Button.browse_file,
    Button.browse_directory, Button.save_file) for the common cases of
    picking a path and handing it off to your own function.
    """
    _registry: dict[str, "Button"] = {}
    _counter: int = 0

    def __init__(
        self,
        target,  # AppWindow or AppFrame — where this button gets placed
        command,  # callback: a zero-argument function to run on click
        text: str = "Button",
        name: str | None = None,
        layout: str = "pack",
        **layout_options,
    ):
        Button._counter += 1
        self.name = name or f"Button_{Button._counter}"

        self.parent = resolve_parent(target)
        self.widget = ttk.Button(self.parent, text=text, command=command)
        place_widget(self.widget, layout, **layout_options)

        Button._registry[self.name] = self

    @classmethod
    def browse_directory(cls, target, on_select, text="Browse...", **kwargs):
        """
        on_select: a function taking one argument (the chosen folder path).
        Nothing is called if the user cancels the dialog.
        """
        def _command():
            path = filedialog.askdirectory()
            if path:
                on_select(path)

        return cls(target, _command, text=text, **kwargs)

    @classmethod
    def browse_file(
        cls, target, on_select, text="Open...",
        filetypes=(("All files", "*.*"),), **kwargs,
    ):
        """on_select: a function taking one argument (the chosen file path)."""
        def _command():
            path = filedialog.askopenfilename(filetypes=filetypes)
            if path:
                on_select(path)

        return cls(target, _command, text=text, **kwargs)

    @classmethod
    def save_file(
        cls, target, on_save, text="Save As...",
        filetypes=(("All files", "*.*"),), defaultextension="", **kwargs,
    ):
        """
        on_save: a function taking one argument (the chosen output path).
        This button only picks the path — your on_save function does the
        actual writing.
        """
        def _command():
            path = filedialog.asksaveasfilename(
                filetypes=filetypes, defaultextension=defaultextension,
            )
            if path:
                on_save(path)

        return cls(target, _command, text=text, **kwargs)

    @classmethod
    def get(cls, name: str) -> "Button":
        return cls._registry[name]


class Table:
    """
    A managed ttk.Treeview used as a flat table (show="headings" hides
    the tree column, so it behaves like a spreadsheet grid).
    """
    _registry: dict[str, "Table"] = {}
    _counter: int = 0

    def __init__(
        self,
        target,  # AppWindow or AppFrame — where this table gets placed
        columns: list[str],
        name: str | None = None,
        layout: str = "pack",
        **layout_options,
        ):
        
        Table._counter += 1
        self.name = name or f"Table_{Table._counter}"
        self.columns = columns

        self.parent = resolve_parent(target)
        self.widget = ttk.Treeview(self.parent, columns=columns, show="headings")
        for col in columns:
            self.widget.heading(col, text=col)
            self.widget.column(col, anchor="w")

        place_widget(self.widget, layout, **layout_options)

        Table._registry[self.name] = self

    def load_rows(self, rows) -> None:
        """rows: an iterable of tuples/lists, values in the same order as columns."""
        self.clear()
        for row in rows:
            self.widget.insert("", "end", values=row)

    def clear(self) -> None:
        for item in self.widget.get_children():
            self.widget.delete(item)

    @classmethod
    def get(cls, name: str) -> "Table":
        return cls._registry[name]