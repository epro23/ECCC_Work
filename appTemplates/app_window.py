"""
Reusable base class for spinning up in-house Tkinter applications quickly.
"""
import ctypes
import sys
import tkinter as tk
from tkinter import ttk
from typing import Literal

import sv_ttk

class AppWindow:
    """
    Base class for the application root window.

    Subclass this and override build_ui() to add widgets.
    """
    def __init__(
        self,
        title: str = "Application",
        size: str = "900x600",
        min_size: tuple[int, int] = (600, 400),
        resizable: tuple[bool, bool] = (True, True),
        theme: Literal["dark", "light"] = "dark",
        icon_path: str | None = None,
        ):

        self._set_dpi_awareness()  # must happen before Tk() is created

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(size)
        self.root.minsize(*min_size)
        self.root.resizable(*resizable)

        if icon_path:
            self.root.iconbitmap(icon_path)  # .ico only, Windows

        # sv_ttk restyles all ttk widgets; call it once the root exists
        sv_ttk.set_theme(theme)

        # Intercept the window-manager close (X button) so subclasses
        # can clean up (save state, close DB connections, etc.)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_ui()

    def _set_dpi_awareness(self) -> None:
        """
        Without this, Tkinter apps render blurry/scaled incorrectly on
        Windows displays with scaling above 100% (very common on
        corporate laptops). Must be called before the Tk root exists.
        """
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass  # older Windows without shcore; safe to ignore

    def build_ui(self) -> None:
        """Override in subclasses to add widgets to self.root."""
        placeholder = ttk.Label(self.root, text="Override build_ui()")
        placeholder.pack(padx=20, pady=20)

    def on_close(self) -> None:
        """Override for cleanup; default just destroys the window."""
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    app = AppWindow(title="Test App")
    app.run()