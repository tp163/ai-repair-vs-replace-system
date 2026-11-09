"""REVIVAI icon set.

Every icon is a 24x24 duotone SVG: a soft tinted body (class ``f``) under a
crisp rounded stroke. Colour comes from ``currentColor`` so CSS decides the
hue, and no <defs>/gradients are used so the markup survives Streamlit's
markdown renderer unchanged.

Usage:
    from src.ui.icons import icon
    icon("battery")                 # default size, inherits colour
    icon("shield", solid=True)      # filled variant (trust bar)
    icon("cpu", cls="glow")         # adds the soft neon glow

All strings are single-line on purpose: a blank line inside an HTML block
would make Markdown end the block early.
"""
from __future__ import annotations

# name -> inner SVG markup.  f = tinted fill layer, k = detail stroke, d = dot
_PATHS: dict[str, str] = {
    # ── devices ────────────────────────────────────────────────
    "phone": (
        '<rect class="f" x="6.5" y="2.5" width="11" height="19" rx="2.8"/>'
        '<rect x="6.5" y="2.5" width="11" height="19" rx="2.8"/>'
        '<path d="M10.4 5.4h3.2"/><circle class="d" cx="12" cy="18.4" r=".7"/>'
    ),
    "phone-crack": (
        '<rect class="f" x="6.5" y="2.5" width="11" height="19" rx="2.8"/>'
        '<rect x="6.5" y="2.5" width="11" height="19" rx="2.8"/>'
        '<path d="M13.9 2.7 11.7 8.1l2.6 2.2-3.2 3.5 1.9 3.6"/>'
        '<path d="M11.7 8.1 8.9 7.2M14.3 10.3l2.5.5M11.1 13.8l-2.4 1"/>'
    ),
    "battery": (
        '<rect class="f" x="2.8" y="7" width="15.4" height="10" rx="2.6"/>'
        '<rect x="2.8" y="7" width="15.4" height="10" rx="2.6"/>'
        '<path d="M21 10.4v3.2"/>'
        '<path class="k" d="M11.3 8.9 8.6 12.4h2.9l-.9 2.9 3-3.6h-2.9z"/>'
    ),
    "plug": (
        '<path class="f" d="M6.6 7.2h10.8v4.1a5.4 5.4 0 0 1-10.8 0z"/>'
        '<path d="M6.6 7.2h10.8v4.1a5.4 5.4 0 0 1-10.8 0z"/>'
        '<path d="M9.2 3v4.2M14.8 3v4.2M12 16.7V21"/>'
    ),
    "thermo": (
        '<path class="f" d="M14 14.7V5.4a2 2 0 0 0-4 0v9.3a4 4 0 1 0 4 0z"/>'
        '<path d="M14 14.7V5.4a2 2 0 0 0-4 0v9.3a4 4 0 1 0 4 0z"/>'
        '<path class="k" d="M12 9.5v7"/><circle class="d" cx="12" cy="17.4" r="1.3"/>'
        '<path d="M17.2 6.2h2.2M17.2 9.2h1.5"/>'
    ),
    "display": (
        '<rect class="f" x="7" y="3" width="10" height="18" rx="2.4"/>'
        '<rect x="7" y="3" width="10" height="18" rx="2.4"/>'
    ),
    "cpu": (
        '<rect class="f" x="6" y="6" width="12" height="12" rx="2.6"/>'
        '<rect x="6" y="6" width="12" height="12" rx="2.6"/>'
        '<rect class="k" x="9.6" y="9.6" width="4.8" height="4.8" rx="1.1"/>'
        '<path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/>'
    ),
    "storage": (
        '<ellipse class="f" cx="12" cy="6.6" rx="7" ry="3"/>'
        '<path class="f" d="M5 6.6v10.8c0 1.7 3.1 3 7 3s7-1.3 7-3V6.6c0 1.7-3.1 3-7 3s-7-1.3-7-3z"/>'
        '<ellipse cx="12" cy="6.6" rx="7" ry="3"/>'
        '<path d="M5 6.6v10.8c0 1.7 3.1 3 7 3s7-1.3 7-3V6.6"/>'
        '<path class="k" d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>'
    ),
    # ── agents / pipeline ──────────────────────────────────────
    "stethoscope": (
        '<circle class="f" cx="18.6" cy="11.4" r="2.2"/>'
        '<path d="M6.2 3v5.2a4 4 0 0 0 8 0V3M5 3h2.4M13 3h2.4"/>'
        '<path d="M10.2 12.2v2.4a4.4 4.4 0 0 0 8.4 1.8v-2.8"/>'
        '<circle cx="18.6" cy="11.4" r="2.2"/>'
    ),
    "coins": (
        '<ellipse class="f" cx="12" cy="6.2" rx="7" ry="3"/>'
        '<ellipse cx="12" cy="6.2" rx="7" ry="3"/>'
        '<path d="M5 6.2v5.6c0 1.7 3.1 3 7 3s7-1.3 7-3V6.2"/>'
        '<path d="M5 11.8v5.6c0 1.7 3.1 3 7 3s7-1.3 7-3v-5.6"/>'
    ),
    "clipboard": (
        '<rect class="f" x="5" y="4.4" width="14" height="17" rx="2.6"/>'
        '<rect x="5" y="4.4" width="14" height="17" rx="2.6"/>'
        '<path d="M9 3.4h6a.9.9 0 0 1 .9.9v2H8.1v-2a.9.9 0 0 1 .9-.9z"/>'
        '<path class="k" d="M8.8 11.2h6.4M8.8 14.6h6.4M8.8 18h3.2"/>'
    ),
    "pulse": (
        '<rect class="f" x="3" y="4" width="18" height="16" rx="3.4"/>'
        '<rect x="3" y="4" width="18" height="16" rx="3.4"/>'
        '<path class="k" d="M6.5 12.2h3l1.7-3.8 2.6 7.4 1.6-3.6h2.1"/>'
    ),
    "layers": (
        '<path class="f" d="m12 3.2 8.8 4.6L12 12.4 3.2 7.8z"/>'
        '<path d="m12 3.2 8.8 4.6L12 12.4 3.2 7.8z"/>'
        '<path d="m3.2 12 8.8 4.6 8.8-4.6M3.2 16.2l8.8 4.6 8.8-4.6"/>'
    ),
    "trend": (
        '<rect class="f" x="3" y="4" width="18" height="16" rx="3.4"/>'
        '<rect x="3" y="4" width="18" height="16" rx="3.4"/>'
        '<path class="k" d="m7 14.6 3.4-3.6 2.6 2.4L17 9.4M14.2 9.4H17v2.8"/>'
    ),
    "scale": (
        '<path class="f" d="M5 7.2 2.4 13.4a2.6 2.6 0 0 0 5.2 0zM19 7.2l-2.6 6.2a2.6 2.6 0 0 0 5.2 0z"/>'
        '<path d="M12 4v16M7.5 20.4h9M5 7.2h14"/>'
        '<path d="M5 7.2 2.4 13.4a2.6 2.6 0 0 0 5.2 0zM19 7.2l-2.6 6.2a2.6 2.6 0 0 0 5.2 0z"/>'
    ),
    "trophy": (
        '<path class="f" d="M8 4h8v5.2a4 4 0 0 1-8 0z"/>'
        '<path d="M8 4h8v5.2a4 4 0 0 1-8 0z"/>'
        '<path d="M8 5.8H5.2v1.6A3 3 0 0 0 8 10.4M16 5.8h2.8v1.6a3 3 0 0 1-2.8 3M12 13.2v3.6M8.6 20h6.8M10 16.8h4"/>'
    ),
    "check-circle": (
        '<circle class="f" cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="9"/>'
        '<path class="k" d="m8.3 12.3 2.5 2.5 4.9-5.2"/>'
    ),
    "alert": (
        '<path class="f" d="M12 3.6 21 19.4H3z"/><path d="M12 3.6 21 19.4H3z"/>'
        '<path class="k" d="M12 10v4.2"/><circle class="d" cx="12" cy="16.8" r=".8"/>'
    ),
    "chat": (
        '<path class="f" d="M20.6 11.5a8.1 8.1 0 0 1-8.1 8.1H7.4L3.2 21.8l1.3-4.2A8.1 8.1 0 1 1 20.6 11.5z"/>'
        '<path d="M20.6 11.5a8.1 8.1 0 0 1-8.1 8.1H7.4L3.2 21.8l1.3-4.2A8.1 8.1 0 1 1 20.6 11.5z"/>'
        '<circle class="d" cx="8.4" cy="11.6" r=".95"/><circle class="d" cx="12.4" cy="11.6" r=".95"/>'
        '<circle class="d" cx="16.4" cy="11.6" r=".95"/>'
    ),
    "wrench": (
        '<path class="f" d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>'
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>'
    ),
    # ── navigation / chrome ────────────────────────────────────
    "user": (
        '<circle class="f" cx="12" cy="8" r="3.7"/><circle cx="12" cy="8" r="3.7"/>'
        '<path class="f" d="M4.6 20.2c.9-3.7 4-5.7 7.4-5.7s6.5 2 7.4 5.7z"/>'
        '<path d="M4.6 20.2c.9-3.7 4-5.7 7.4-5.7s6.5 2 7.4 5.7"/>'
    ),
    "heart": (
        '<path class="f" d="M12 20.2s-7.7-4.7-7.7-10.6A4.4 4.4 0 0 1 12 6.9a4.4 4.4 0 0 1 7.7 2.7c0 5.9-7.7 10.6-7.7 10.6z"/>'
        '<path d="M12 20.2s-7.7-4.7-7.7-10.6A4.4 4.4 0 0 1 12 6.9a4.4 4.4 0 0 1 7.7 2.7c0 5.9-7.7 10.6-7.7 10.6z"/>'
    ),
    "bookmark": (
        '<path class="f" d="M7 3.5h10a1 1 0 0 1 1 1V21l-6-4-6 4V4.5a1 1 0 0 1 1-1z"/>'
        '<path d="M7 3.5h10a1 1 0 0 1 1 1V21l-6-4-6 4V4.5a1 1 0 0 1 1-1z"/>'
        '<path class="k" d="M12 7.2v4.2M9.9 9.3h4.2"/>'
    ),
    "search": '<circle class="f" cx="11" cy="11" r="6.6"/><circle cx="11" cy="11" r="6.6"/><path d="m20.2 20.2-4.5-4.5"/>',
    "sparkle": (
        '<path class="f" d="m11 3.4 1.9 5.2 5.2 1.9-5.2 1.9L11 17.6l-1.9-5.2-5.2-1.9 5.2-1.9z"/>'
        '<path d="m11 3.4 1.9 5.2 5.2 1.9-5.2 1.9L11 17.6l-1.9-5.2-5.2-1.9 5.2-1.9z"/>'
        '<path d="M18.6 16.2v4M16.6 18.2h4"/>'
    ),
    "pin": (
        '<path class="f" d="M12 21.6s6.9-5.9 6.9-11.3a6.9 6.9 0 1 0-13.8 0c0 5.4 6.9 11.3 6.9 11.3z"/>'
        '<path d="M12 21.6s6.9-5.9 6.9-11.3a6.9 6.9 0 1 0-13.8 0c0 5.4 6.9 11.3 6.9 11.3z"/>'
        '<circle class="k" cx="12" cy="10.2" r="2.5"/>'
    ),
    "shield": (
        '<path class="f" d="M12 2.8 4.8 5.6v5.8c0 4.6 3 8.2 7.2 9.8 4.2-1.6 7.2-5.2 7.2-9.8V5.6z"/>'
        '<path d="M12 2.8 4.8 5.6v5.8c0 4.6 3 8.2 7.2 9.8 4.2-1.6 7.2-5.2 7.2-9.8V5.6z"/>'
        '<path class="k" d="m8.8 12.1 2.4 2.4 4.2-4.7"/>'
    ),
    "star": (
        '<path class="f" d="m12 3.2 2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/>'
        '<path d="m12 3.2 2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6-4.5-4.2 6.1-.7z"/>'
    ),
    "arrow": '<path d="M5 12h14M13.2 6.2 19 12l-5.8 5.8"/>',
    "chevron": '<path d="m9.5 6 6 6-6 6"/>',
}

# Solid variant tweaks live in CSS (.ico.solid .f / .k / .d), nothing to do here.


def icon(name: str, *, size: int | None = None, cls: str = "", solid: bool = False,
         stroke: float = 1.7) -> str:
    """Return an inline <svg> string for ``name`` (single line, no blank lines)."""
    body = _PATHS[name]
    classes = "ico" + (" solid" if solid else "") + (f" {cls}" if cls else "")
    dim = f' width="{size}" height="{size}"' if size else ""
    return (
        f'<svg class="{classes}"{dim} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{body}</svg>'
    )


def logo_mark() -> str:
    """The REVIVAI 'R' glyph: a bold R whose leg ends in a signal node."""
    return (
        '<svg class="logo-r" viewBox="0 0 32 32" fill="none" stroke="currentColor" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M9 25V7h8.2a5.2 5.2 0 0 1 0 10.4H9"/>'
        '<path d="M16.4 17.4 22.5 25"/>'
        '<circle cx="25.2" cy="8" r="1.7" fill="currentColor" stroke="none" class="node"/>'
        '</svg>'
    )
