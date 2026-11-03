"""MinecrafTeX math-specific glyphs and the stretchy-construction spec.

This module supplies everything Monocraft does not: the radical (U+221A) and
n-ary product (U+220F), display-size big operators, and -- most importantly --
the *vertical size variants* and *glyph-assembly parts* that let delimiters,
integrals and radicals GROW to fit their content. That adaptive sizing is the
whole point of MinecrafTeX versus a plain pixel font.

Design conventions
------------------
* All pieces are pixel-art on the shared 5-wide grid (matching Monocraft).
* Stretchy delimiters are centred on the math axis (3.5 px) like the base glyph.
* Assembly uses zero connector overlap (`MinConnectorOverlap = 0`) so parts abut
  on whole-pixel boundaries -- the engine can only grow them in 1 px steps, which
  keeps every assembled size perfectly crisp.

The build script consumes `math_extra_glyphs()`; the MATH table builder consumes
`MATH_CONSTRUCTIONS`.
"""
from __future__ import annotations

from dataclasses import dataclass

from pixelfont import Glyph, PIXEL, AXIS_PX

# Variant heights (in pixels) generated for each stretchy delimiter, on top of
# the ~7 px base glyph. ODD heights stay centred on the 3.5 px math axis, so the
# engine never has to half-pixel-shift them. We pre-draw a generous range so that
# realistic content (fractions, nested fractions) always hits a crisp solid
# variant and only pathologically tall content falls back to glyph assembly.
_VARIANT_HEIGHTS = [9, 11, 13, 15, 17, 19, 21, 23, 25,
                    31, 37, 43, 51, 61, 73, 87, 101]


@dataclass
class Construction:
    """Stretchy construction for one base symbol.

    `variants` are (glyph_name, advance_units) smallest->largest, INCLUDING the
    base glyph first. `parts` are assembly GlyphPartRecords bottom->top as
    (glyph_name, start_conn, end_conn, full_advance, is_extender).
    """
    codepoint: int
    base_name: str | None          # None -> resolve from cmap at build time
    base_advance: int
    variants: list[tuple[str, int]]
    parts: list[tuple[str, int, int, int, bool]]


_glyphs: list[Glyph] = []
_constructions: list[Construction] = []


def _g(name: str, rows: list[str], bottom_px: int,
       advance_px: int = 6, codepoint: int | None = None) -> Glyph:
    gl = Glyph(name=name, codepoint=codepoint, rows=rows,
               advance_px=advance_px, bottom_px=bottom_px)
    _glyphs.append(gl)
    return gl


def _centred_bottom(height_px: int) -> int:
    """bottom_px so a glyph of given height is centred on the 3.5 px axis."""
    return round((AXIS_PX + 0.5) - height_px / 2)


def _add_vertical_delimiter(key: str, codepoint: int, base_name: str,
                            base_height_px: int,
                            top: list[str], ext: str, bottom: list[str],
                            mid: list[str] | None = None,
                            advance_px: int = 5) -> None:
    """Register size variants + an assembly for a vertically-stretchy symbol.

    Variant glyph i = top + ext*k (+ mid + ext*k) + bottom, sized to the target
    heights. Assembly parts are the caps plus the extender(s).
    """
    variants: list[tuple[str, int]] = [(base_name, base_height_px * PIXEL)]

    for h in _VARIANT_HEIGHTS:
        if mid is None:
            k = h - len(top) - len(bottom)
            rows = top + [ext] * k + bottom
        else:
            k2 = (h - len(top) - len(bottom) - len(mid)) // 2
            rows = top + [ext] * k2 + mid + [ext] * k2 + bottom
        name = f"{key}.v{h}"
        _g(name, rows, _centred_bottom(len(rows)), advance_px=advance_px)
        variants.append((name, len(rows) * PIXEL))

    # Assembly parts (drawn at baseline; engine stacks + centres them). Each part
    # advertises a connector region equal to its full advance and the extender is
    # 1 px tall, so the engine can overlap neighbours on matching pixel columns to
    # hit any target height exactly -- no gaps between the caps and the extender.
    bot_name = f"{key}.bot"
    ext_name = f"{key}.ext"
    top_name = f"{key}.top"
    _g(bot_name, bottom, 0, advance_px=advance_px)
    _g(ext_name, [ext], 0, advance_px=advance_px)
    _g(top_name, top, 0, advance_px=advance_px)

    nb, nt = len(bottom) * PIXEL, len(top) * PIXEL
    if mid is None:
        parts = [
            (bot_name, 0, nb, nb, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (top_name, nt, 0, nt, False),
        ]
    else:
        mid_name = f"{key}.mid"
        _g(mid_name, mid, 0, advance_px=advance_px)
        nm = len(mid) * PIXEL
        parts = [
            (bot_name, 0, nb, nb, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (mid_name, nm, nm, nm, False),
            (ext_name, PIXEL, PIXEL, PIXEL, True),
            (top_name, nt, 0, nt, False),
        ]

    _constructions.append(Construction(codepoint, base_name,
                                       base_height_px * PIXEL, variants, parts))


# --- Stretchy delimiters (base glyphs come from Monocraft via cmap) ----------

_add_vertical_delimiter(
    "parenleft", 0x0028, "left_parenthesis", 7,
    top=["..##.", ".##..", ".#..."], ext=".#...",
    bottom=[".#...", ".##..", "..##."])

_add_vertical_delimiter(
    "parenright", 0x0029, "right_parenthesis", 7,
    top=[".##..", "..##.", "...#."], ext="...#.",
    bottom=["...#.", "..##.", ".##.."])

_add_vertical_delimiter(
    "bracketleft", 0x005B, "left_square_bracket", 7,
    top=[".###.", ".#..."], ext=".#...",
    bottom=[".#...", ".###."])

_add_vertical_delimiter(
    "bracketright", 0x005D, "right_square_bracket", 7,
    top=[".###.", "...#."], ext="...#.",
    bottom=["...#.", ".###."])

_add_vertical_delimiter(
    "braceleft", 0x007B, "left_curly_brace", 7,
    top=["..##.", "..#..", "..#.."], ext="..#..",
    mid=[".#...", "#....", ".#..."], bottom=["..#..", "..#..", "..##."])

_add_vertical_delimiter(
    "braceright", 0x007D, "right_curly_brace", 7,
    top=[".##..", "..#..", "..#.."], ext="..#..",
    mid=["...#.", "....#", "...#."], bottom=["..#..", "..#..", ".##.."])

_add_vertical_delimiter(
    "bar", 0x007C, "vertical_line", 7,
    top=["..#.."], ext="..#..", bottom=["..#.."])


# --- Radical (Monocraft has no U+221A): base + upward-growing variants -------
#
# The surd has a 6 px advance. The top row draws 1 px past that advance so it
# overlaps TeX's vinculum; an exact edge-to-edge join can rasterize with a
# hairline seam in PDFs. MinecrafTeX sets RadicalExtraAscender to zero so this
# connector and the overbar occupy the same pixel row.
_RAD_CHECK = ["#...#.", ".#.#..", "..#..."]   # the V, bottom 3 rows (width 6)
_RAD_VBAR = "....#."                            # rising right stroke (col 4)
_RAD_TOP = "....###"                            # stroke + 1 px overbar overlap


def _radical_rows(height_px: int) -> list[str]:
    n_vbar = height_px - len(_RAD_CHECK) - 1
    return [_RAD_TOP] + [_RAD_VBAR] * n_vbar + _RAD_CHECK


# Base radical (7 px), sits on the baseline (grows upward, not axis-centred).
_g("radical", _radical_rows(7), 0, advance_px=6, codepoint=0x221A)
_rad_variants = [("radical", 7 * PIXEL)]
for h in _VARIANT_HEIGHTS:
    nm = f"radical.v{h}"
    _g(nm, _radical_rows(h), 0, advance_px=6)
    _rad_variants.append((nm, h * PIXEL))

# Radical assembly: check at the bottom, repeatable vertical stroke, top cap with
# the connecting tongue.
_g("radical.bot", _RAD_CHECK, 0, advance_px=6)
_g("radical.ext", [_RAD_VBAR], 0, advance_px=6)
_g("radical.top", [_RAD_TOP], 0, advance_px=6)
_constructions.append(Construction(
    0x221A, "radical", 7 * PIXEL, _rad_variants,
    [("radical.bot", 0, len(_RAD_CHECK) * PIXEL, len(_RAD_CHECK) * PIXEL, False),
     ("radical.ext", PIXEL, PIXEL, PIXEL, True),
    ("radical.top", PIXEL, 0, PIXEL, False)]))


# --- Display-size big operators ---------------------------------------------
# Base integral/sum come from Monocraft; we add a larger DISPLAY variant so they
# grow in display style (engine compares advance to DisplayOperatorMinHeight).

# Display integral: a tall, graceful S (15 px) so it visually spans a typical
# display integrand (a fraction/radical), matching Computer Modern's display
# integral. Big operators do NOT stretch to the integrand (that is not how TeX
# works); they have a single fixed display size, which is what this variant is.
_g("integral.display", [
    "...##",
    "..#.#",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "#.#..",
    "##...",
], bottom_px=-3, codepoint=None)
_constructions.append(Construction(
    0x222B, "integral", 8 * PIXEL,
    [("integral", 8 * PIXEL), ("integral.display", 15 * PIXEL)], []))

# Display summation (9 px tall sigma; vertex at the left-centre like the base).
_g("summation.display", [
    "#########",
    "#........",
    ".#.......",
    "..#......",
    "...#.....",
    "..#......",
    ".#.......",
    "#........",
    "#########",
], bottom_px=-1, advance_px=10, codepoint=None)
_constructions.append(Construction(
    0x2211, "n_ary_summation", 7 * PIXEL,
    [("n_ary_summation", 7 * PIXEL), ("summation.display", 9 * PIXEL)], []))

# N-ary product (Monocraft lacks U+220F): base + display variant.
_g("product", [
    "#####",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
    ".#.#.",
], bottom_px=0, codepoint=0x220F)
_g("product.display", [
    "#######",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
    ".#...#.",
], bottom_px=-1, advance_px=8, codepoint=None)
_constructions.append(Construction(
    0x220F, "product", 7 * PIXEL,
    [("product", 7 * PIXEL), ("product.display", 9 * PIXEL)], []))


# --- Plain math symbols Monocraft is missing -------------------------------
# Common relations/operators absent from the base set. Drawn 7-row on the shared
# 5-wide grid (bottom_px = 0, like Monocraft operators) so they sit naturally in
# a line of pixel math.

_g("less_equal", [
    "...#.",
    "..#..",
    ".#...",
    "..#..",
    "...#.",
    ".....",
    "#####",
], bottom_px=0, codepoint=0x2264)

_g("greater_equal", [
    ".#...",
    "..#..",
    "...#.",
    "..#..",
    ".#...",
    ".....",
    "#####",
], bottom_px=0, codepoint=0x2265)

_g("approx_equal", [
    ".....",
    ".#.##",
    "##.#.",
    ".....",
    ".#.##",
    "##.#.",
    ".....",
], bottom_px=0, codepoint=0x2248)

_g("tilde_operator", [
    ".....",
    ".....",
    ".#..#",
    "#.#.#",
    "#..#.",
    ".....",
    ".....",
], bottom_px=0, codepoint=0x223C)

_g("element_of", [
    "..###",
    ".#...",
    "#....",
    "####.",
    "#....",
    ".#...",
    "..###",
], bottom_px=0, codepoint=0x2208)

_g("contains_member", [
    "###..",
    "...#.",
    "....#",
    ".####",
    "....#",
    "...#.",
    "###..",
], bottom_px=0, codepoint=0x220B)

_g("nabla", [
    "#####",
    "#...#",
    "#...#",
    ".#.#.",
    ".#.#.",
    "..#..",
    ".....",
], bottom_px=0, codepoint=0x2207)

_g("dot_operator", [
    ".....",
    ".....",
    ".....",
    "..#..",
    ".....",
    ".....",
    ".....",
], bottom_px=0, advance_px=4, codepoint=0x22C5)

_g("union", [
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    ".###.",
], bottom_px=0, codepoint=0x222A)

_g("empty_set", [
    "....#",
    ".###.",
    "#..##",
    "#.#.#",
    "##..#",
    ".###.",
    "#....",
], bottom_px=0, codepoint=0x2205)


# --- More stretchy delimiters: ceilings, floors, double bar, angle brackets ----
# Base glyphs live in math_symbols.py (Monocraft has none of these).

_add_vertical_delimiter(
    "ceilleft", 0x2308, "left_ceiling", 7,
    top=[".###.", ".#..."], ext=".#...", bottom=[".#..."])

_add_vertical_delimiter(
    "ceilright", 0x2309, "right_ceiling", 7,
    top=[".###.", "...#."], ext="...#.", bottom=["...#."])

_add_vertical_delimiter(
    "floorleft", 0x230A, "left_floor", 7,
    top=[".#..."], ext=".#...", bottom=[".#...", ".###."])

_add_vertical_delimiter(
    "floorright", 0x230B, "right_floor", 7,
    top=["...#."], ext="...#.", bottom=["...#.", ".###."])

_add_vertical_delimiter(
    "dblbar", 0x2016, "double_vertical_line", 7,
    top=[".#.#."], ext=".#.#.", bottom=[".#.#."])


def _angle_rows(height_px: int, left: bool) -> list[str]:
    """A pixel angle bracket: one ink pixel per row, point at the middle row.

    Angle brackets cannot be assembled from a straight extender, so (like TeX)
    they only come in pre-drawn sizes. Width grows slowly with height.
    """
    width = min(8, 4 + (height_px - 7) // 6)
    centre = (height_px - 1) / 2
    rows = []
    for y in range(height_px):
        x = int((width - 1) * abs(y - centre) / centre + 0.5)
        if not left:
            x = width - 1 - x
        rows.append("." + "." * x + "#" + "." * (width - 1 - x) + ".")
    return rows


for _key, _cp, _base, _left in (("angleleft", 0x27E8, "mathematical_left_angle_bracket", True),
                                ("angleright", 0x27E9, "mathematical_right_angle_bracket", False)):
    _angle_variants = [(_base, 7 * PIXEL)]
    for _h in _VARIANT_HEIGHTS:
        _rows = _angle_rows(_h, _left)
        _g(f"{_key}.v{_h}", _rows, _centred_bottom(_h), advance_px=len(_rows[0]))
        _angle_variants.append((f"{_key}.v{_h}", _h * PIXEL))
    _constructions.append(Construction(_cp, _base, 7 * PIXEL, _angle_variants, []))


# --- Display sizes for the big operators math_symbols.py adds -----------------
# 9 px tall like the display summation/product, centred on the axis.

def _big_op_display(codepoint: int, base_name: str, base_height_px: int,
                    rows: list[str], bottom_px: int = -1) -> None:
    name = f"{base_name}.display"
    _g(name, rows, bottom_px, advance_px=len(rows[0]) + 1)
    _constructions.append(Construction(
        codepoint, base_name, base_height_px * PIXEL,
        [(base_name, base_height_px * PIXEL), (name, len(rows) * PIXEL)], []))


def _wedge_rows(width: int, height: int) -> list[str]:
    half = (width - 1) // 2
    rows = []
    for y in range(height):
        d = int(half * y / (height - 1) + 0.5)
        row = ["."] * width
        row[half - d] = row[half + d] = "#"
        rows.append("".join(row))
    return rows


_CUP_DISPLAY = ["#.....#"] * 8 + [".#####."]
_WEDGE_DISPLAY = _wedge_rows(7, 9)
_CIRCLE9 = ["...###...", ".##...##.", ".#.....#.", "#.......#", "#.......#",
            "#.......#", ".#.....#.", ".##...##.", "...###..."]


def _with(rows: list[str], marks: list[tuple[int, int]]) -> list[str]:
    out = [list(r) for r in rows]
    for x, y in marks:
        out[y][x] = "#"
    return ["".join(r) for r in out]


_big_op_display(0x22C3, "n_ary_union", 7, _CUP_DISPLAY)
_big_op_display(0x22C2, "n_ary_intersection", 7, _CUP_DISPLAY[::-1])
_big_op_display(0x22C0, "n_ary_logical_and", 7, _WEDGE_DISPLAY)
_big_op_display(0x22C1, "n_ary_logical_or", 7, _WEDGE_DISPLAY[::-1])
_big_op_display(0x2210, "n_ary_coproduct", 7,
                [".#...#."] * 8 + ["#######"])
_big_op_display(0x2A00, "n_ary_circled_dot", 7,
                _with(_CIRCLE9, [(4, 4)]))
_big_op_display(0x2A01, "n_ary_circled_plus", 7,
                _with(_CIRCLE9, [(4, y) for y in range(9)] + [(x, 4) for x in range(9)]))
_big_op_display(0x2A02, "n_ary_circled_times", 7,
                _with(_CIRCLE9, [(d, d) for d in range(1, 8)] + [(8 - d, d) for d in range(1, 8)]))


def _display_integrals() -> None:
    from math_symbols import overlay, repeat_integral
    display = next(g for g in _glyphs if g.name == "integral.display")
    double = repeat_integral(display.rows, 2)
    # \oiint: the contour ring around the middle of the display \iint.
    mid = len(double) // 2
    ring = [""] * (mid - 1) + [".######.", "#......#", ".######."]
    for cp, base, rows in ((0x222C, "double_integral", double),
                           (0x222D, "triple_integral", repeat_integral(display.rows, 3)),
                           (0x222F, "surface_integral", overlay(double, ring, 0))):
        _g(f"{base}.display", rows, display.bottom_px, advance_px=len(rows[0]))
        _constructions.append(Construction(
            cp, base, 8 * PIXEL,
            [(base, 8 * PIXEL), (f"{base}.display", len(rows) * PIXEL)], []))


_display_integrals()


# --- Horizontally stretchy symbols --------------------------------------------
# Wide accents, over/under bars, braces and arrows. Same scheme as the vertical
# delimiters, turned sideways: pre-drawn widths so common sizes stay crisp, plus
# a glyph assembly (left cap, 1 px extender, optional middle, right cap) for
# anything wider. Each cap's connecting column contains the extender's pixels,
# so overlapping a connector never adds or removes ink.

# Variant widths in pixels; the engine picks the first one at least as wide as
# the content, then falls back to the assembly.
_HORIZ_WIDTHS = list(range(6, 42, 2)) + [45, 51, 61, 71, 81, 101]

_horiz_constructions: list[Construction] = []


def _add_horizontal(key: str, codepoint: int, left: list[str], ext: str,
                    right: list[str], mid: list[str] | None = None,
                    bottom_px: int = 0, base_k: int | None = None) -> None:
    """Register width variants + an assembly for a horizontally-stretchy symbol.

    `left`/`right`/`mid` are row lists (top row first); `ext` is the extender
    column, one character per row. With `base_k` set, the symbol has no cmap'd
    glyph yet and the k-extender shape becomes its base glyph.
    """
    def shape(k: int) -> list[str]:
        if mid is None:
            return [l + e * k + r for l, e, r in zip(left, ext, right)]
        return [l + e * k + m + e * k + r for l, e, m, r in zip(left, ext, mid, right)]

    if base_k is not None:
        rows = shape(base_k)
        _g(key, rows, bottom_px, advance_px=len(rows[0]), codepoint=codepoint)

    fixed = len(left[0]) + len(right[0]) + (len(mid[0]) if mid else 0)
    variants: list[tuple[str, int]] = [(key, 0)]  # base advance resolved at build
    seen: set[int] = set()
    for width in _HORIZ_WIDTHS:
        k = width - fixed if mid is None else (width - fixed) // 2
        if k <= (base_k or 0) or k in seen:
            continue
        seen.add(k)
        rows = shape(k)
        name = f"{key}.h{len(rows[0])}"
        _g(name, rows, bottom_px, advance_px=len(rows[0]))
        variants.append((name, len(rows[0]) * PIXEL))

    names = {}
    for part, rows in (("left", left), ("ext", list(ext)), ("mid", mid), ("right", right)):
        if rows is not None:
            names[part] = f"{key}.{part}"
            _g(names[part], rows, bottom_px, advance_px=len(rows[0]))
    nl, nr = len(left[0]) * PIXEL, len(right[0]) * PIXEL
    parts = [(names["left"], 0, nl, nl, False),
             (names["ext"], PIXEL, PIXEL, PIXEL, True)]
    if mid is not None:
        nm = len(mid[0]) * PIXEL
        parts += [(names["mid"], nm, nm, nm, False),
                  (names["ext"], PIXEL, PIXEL, PIXEL, True)]
    parts.append((names["right"], nr, 0, nr, False))
    _horiz_constructions.append(Construction(codepoint, key, 0, variants, parts))


def _hat_rows(width: int) -> list[str]:
    """\\widehat: a staircase peak that flattens out as it widens (like TeX)."""
    height = 3 if width <= 13 else 4 if width <= 31 else 5
    centre = (width - 1) / 2
    rows = [["."] * width for _ in range(height)]
    for x in range(width):
        y = int((height - 1) * abs(x - centre) / centre + 0.5)
        rows[y][x] = "#"
    return ["".join(r) for r in rows]


# \widehat: pre-drawn only -- a peak has no straight piece to repeat.
_g("widehat", _hat_rows(5), 5, advance_px=5, codepoint=0x0302)
_hat_variants = [("widehat", 0)]
for _w in range(7, 62, 2):
    _g(f"widehat.h{_w}", _hat_rows(_w), 5, advance_px=_w)
    _hat_variants.append((f"widehat.h{_w}", _w * PIXEL))
_horiz_constructions.append(Construction(0x0302, "widehat", 0, _hat_variants, []))

# \overline / \underline (math-core emits COMBINING LOW LINE for both).
_add_horizontal("lowline.math", 0x0332, ["#"], "#", ["#"], bottom_px=-1, base_k=3)

# Arrows, on the same 7-row cell as Monocraft's own arrow glyphs.
_ARROW_SHAFT = "...#..."
_DOUBLE_SHAFT = "..#.#.."
_HEAD_RIGHT = ["...", "#..", ".#.", "###", ".#.", "#..", "..."]
_HEAD_LEFT = [r[::-1] for r in _HEAD_RIGHT]
_DOUBLE_HEAD_RIGHT = ["...", "#..", "##.", "..#", "##.", "#..", "..."]
_DOUBLE_HEAD_LEFT = [r[::-1] for r in _DOUBLE_HEAD_RIGHT]
_SHAFT = list(_ARROW_SHAFT)
_DOUBLE = list(_DOUBLE_SHAFT)

_add_horizontal("rightarrow", 0x2192, _SHAFT, _ARROW_SHAFT, _HEAD_RIGHT)
_add_horizontal("leftarrow", 0x2190, _HEAD_LEFT, _ARROW_SHAFT, _SHAFT)
_add_horizontal("leftrightarrow", 0x2194,
                ["...", "..#", ".##", "###", ".##", "..#", "..."], _ARROW_SHAFT,
                ["...", "#..", "##.", "###", "##.", "#..", "..."])
_add_horizontal("Rightarrow", 0x21D2, _DOUBLE, _DOUBLE_SHAFT, _DOUBLE_HEAD_RIGHT)
_add_horizontal("Leftarrow", 0x21D0, _DOUBLE_HEAD_LEFT, _DOUBLE_SHAFT, _DOUBLE)
_add_horizontal("Leftrightarrow", 0x21D4, _DOUBLE_HEAD_LEFT, _DOUBLE_SHAFT, _DOUBLE_HEAD_RIGHT)
_add_horizontal("mapsto", 0x21A6, list(".#####."), _ARROW_SHAFT, _HEAD_RIGHT)
_add_horizontal("hookrightarrow", 0x21AA,
                ["..", ".#", "#.", ".#", "..", "..", ".."], _ARROW_SHAFT, _HEAD_RIGHT)
# \xlongequal stretches '='.
_add_horizontal("equal", 0x003D, list("..#..#."), "..#..#.", list("..#..#."))

# Over/under braces, parentheses and brackets.
_add_horizontal("overbrace", 0x23DE, ["..", ".#", "#."], ".#.", ["..", "#.", ".#"],
                mid=[".#.", "#.#", "..."], bottom_px=5, base_k=0)
_add_horizontal("underbrace", 0x23DF, ["#.", ".#", ".."], ".#.", [".#", "#.", ".."],
                mid=["...", "#.#", ".#."], bottom_px=-3, base_k=0)
_add_horizontal("overparen", 0x23DC, [".#", "#."], "#.", ["#.", ".#"],
                bottom_px=5, base_k=1)
_add_horizontal("underparen", 0x23DD, ["#.", ".#"], ".#", [".#", "#."],
                bottom_px=-2, base_k=1)
_add_horizontal("overbracket", 0x23B4, ["#", "#"], "#.", ["#", "#"],
                bottom_px=5, base_k=3)
_add_horizontal("underbracket", 0x23B5, ["#", "#"], ".#", ["#", "#"],
                bottom_px=-2, base_k=3)


def math_extra_glyphs() -> list[Glyph]:
    """All MinecrafTeX-specific outline glyphs (radical, variants, parts, ...)."""
    return list(_glyphs)


MATH_CONSTRUCTIONS: list[Construction] = _constructions
MATH_HORIZ_CONSTRUCTIONS: list[Construction] = _horiz_constructions

# Italic corrections (units) so scripts on slanted/asymmetric operators clear the
# glyph body -- most important for the integral, whose limits sit at its side.
ITALIC_CORRECTIONS: dict[str, int] = {
    "integral": 2 * PIXEL,
    "integral.display": 3 * PIXEL,
    "double_integral": 2 * PIXEL,
    "double_integral.display": 3 * PIXEL,
    "triple_integral": 2 * PIXEL,
    "triple_integral.display": 3 * PIXEL,
    "surface_integral": 2 * PIXEL,
    "surface_integral.display": 3 * PIXEL,
}

# Math cut-in kerns (units) per glyph corner, so a big operator's limits tuck
# past its hooks instead of colliding with them -- the same mechanism real math
# fonts use for integral limits. Corners: 'tr','tl','br','bl'. Any corner left
# unset falls back to the italic correction. The integral's lower limit attaches
# at the bottom-right; a positive kern pushes it clear of the left-leaning hook.
MATH_KERNS: dict[str, dict[str, int]] = {
    "integral": {"br": 4 * PIXEL},
    "integral.display": {"br": 6 * PIXEL},
    "double_integral": {"br": 4 * PIXEL},
    "double_integral.display": {"br": 6 * PIXEL},
    "triple_integral": {"br": 4 * PIXEL},
    "triple_integral.display": {"br": 6 * PIXEL},
    "surface_integral": {"br": 4 * PIXEL},
    "surface_integral.display": {"br": 6 * PIXEL},
}
