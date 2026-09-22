"""
AppFrame wraps a ttk.Frame with auto-naming and a class-wide registry,
so other modules (e.g. elements.py) can retrieve a frame by name later
and load widgets into it.
"""
from tkinter import ttk
import sv_ttk
from layout import resolve_parent, place_widget

_TINTS = {
    "dark": "#242424",
    "light": "#ececec",
}

class AppFrame:
    """
    `target` can be an AppWindow instance (has `.root`) or another
    AppFrame instance (for nesting), so frames can be placed inside
    the root window or inside each other.
    """
    _registry: dict[str, "AppFrame"] = {}
    _counter: int = 0

    def __init__(
        self,
        target,  # AppWindow or AppFrame — where this frame gets placed
        name: str | None = None,
        layout: str = "pack",
        **layout_options,  # forwarded to pack()/place()/grid()
        ):
        
        AppFrame._counter += 1
        self.name = name or f"Frame_{AppFrame._counter}"

        self.parent = resolve_parent(target)
        self.frame = self._create_frame(self.parent)
        place_widget(self.frame, layout, **layout_options)

        AppFrame._registry[self.name] = self

    def _create_frame(self, parent) -> ttk.Frame:
        """Builds the ttk.Frame with a background tinted for the active theme."""
        style_name = f"{self.name}.TFrame"
        bg = _TINTS[sv_ttk.get_theme()]
        ttk.Style().configure(style_name, background=bg)
        return ttk.Frame(parent, style=style_name)

    @classmethod
    def get(cls, name: str) -> "AppFrame":
        """Retrieve a previously created frame by name (for elements.py, etc.)."""
        return cls._registry[name]