"""
Small shared helpers used across the library so AppFrame and every
widget in elements.py don't each re-implement the same logic.
"""
def resolve_parent(target):
    """
    Given an AppWindow (has `.root`) or an AppFrame (has `.frame`),
    return the actual Tk widget to use as a parent.
    """
    return target.root if hasattr(target, "root") else target.frame


def place_widget(widget, layout: str = "pack", **layout_options) -> None:
    """Places a widget using pack, place, or grid, chosen by name."""
    if layout == "pack":
        widget.pack(**layout_options)
    elif layout == "place":
        widget.place(**layout_options)
    elif layout == "grid":
        widget.grid(**layout_options)
    else:
        raise ValueError(f"Unknown layout method: {layout!r}")