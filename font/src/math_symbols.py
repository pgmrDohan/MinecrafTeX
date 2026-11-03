"""Plain math symbols, accents and Greek variants that Monocraft does not draw.

These are ordinary (non-stretchy) glyphs that MathML/LaTeX emit for common
commands -- \\hat, \\vec, \\cdots, \\equiv, \\oplus, \\phi, \\hbar, \\langle,
\\lfloor, ... Without them the browser falls back to a non-pixel font in the
middle of a formula.

Every glyph is drawn the way Monocraft stores its own characters: a full
7-row cell (row 0 is the top, y = 6..7 px; row 6 sits on the baseline), so
operators centre on the 3.5 px math axis and accents sit at the top of the
cell. Taller glyphs set `bottom` to drop below the baseline. Advances follow the
same mono/proportional rules as the Monocraft loader, so the new glyphs space
exactly like their neighbours.

Glyphs whose codepoint Monocraft already covers are skipped by the build, so
this module only ever fills gaps.
"""
from __future__ import annotations

from pixelfont import Glyph
from monocraft_loader import (_ADVANCE_OVERRIDES_PX, _center_offset_px,
                              _proportional_advance_px)

_B = "....."  # blank 5-wide row

# codepoint -> (name, rows, bottom_px)
_SYMBOLS: dict[int, tuple[str, list[str], int]] = {}


def _sym(cp: int, name: str, rows: list[str], bottom: int = 0) -> None:
    _SYMBOLS[cp] = (name, rows, bottom)


def _flip(rows: list[str]) -> list[str]:
    return list(reversed(rows))


def _mirror(rows: list[str]) -> list[str]:
    return [r[::-1] for r in rows]


def _slash(rows: list[str]) -> list[str]:
    """Overlay a '/' across the glyph (for negated relations like \\nleq)."""
    h, w = len(rows), max(len(r) for r in rows)
    out = [list(r.ljust(w, ".")) for r in rows]
    for y in range(h):
        x = round((w - 1) * (1 - y / (h - 1)))
        out[y][x] = "#"
    return ["".join(r) for r in out]


# --- Accents (top of the cell, like Monocraft's ´ ` ¨ ¯) ----------------------
# Three-row accents are lifted 1 px (bottom=1) so their lowest row clears
# x-height letters the way Monocraft's two-row accents do.

_sym(0x02C6, "circumflex_accent_mod", ["..#..", ".#.#.", "#...#"] + [_B] * 4, bottom=1)
_sym(0x02C7, "caron_mod", ["#...#", ".#.#.", "..#.."] + [_B] * 4, bottom=1)
_sym(0x02D8, "breve_mod", ["#...#", ".###."] + [_B] * 5)
_sym(0x02DA, "ring_above_mod", ["..#..", ".#.#.", "..#.."] + [_B] * 4, bottom=1)
_sym(0x02DC, "small_tilde_mod", [".#..#", "#.#.#", "#..#."] + [_B] * 4, bottom=1)
_sym(0x20D7, "combining_right_arrow_above", ["...#.", "#####", "...#."] + [_B] * 4, bottom=1)
_sym(0x20DB, "combining_three_dots_above", ["#.#.#"] + [_B] * 6)

# --- Greek variants and letterlike symbols -----------------------------------

_sym(0x03F5, "greek_lunate_epsilon", [_B, _B, ".####", "#....", "####.", "#....", ".####"])
_sym(0x03D1, "greek_theta_symbol", ["..##.", ".#..#", ".#..#", "..###", "#...#", "#..#.", ".##.."])
_sym(0x03D5, "greek_phi_symbol", ["..#..", ".###.", "#.#.#", "#.#.#", "#.#.#", ".###.", "..#..", "..#.."], bottom=-1)
_sym(0x03D6, "greek_pi_symbol", [".......", ".......", "#######", ".#...#.", "#..#..#", "#..#..#", ".##.##."])
_sym(0x03F1, "greek_rho_symbol", [_B, _B, ".###.", "#...#", "#...#", "####.", "#....", "#....", ".###."], bottom=-2)
_sym(0x03F0, "greek_kappa_symbol", [_B, _B, "##..#", ".#.#.", "..#..", ".#.#.", "#..##"])
_sym(0x210F, "planck_over_two_pi", ["#....", "###..", "#.##.", "##..#", "#...#", "#...#", "#...#"])
_sym(0x2113, "script_small_l", ["..#..", ".#.#.", ".#.#.", ".##..", ".#...", ".#...", "..##."])
_sym(0x2135, "alef_symbol", ["#...#", "##..#", ".#.#.", "..#..", ".#.#.", "#..##", "#...#"])
_sym(0x2118, "weierstrass_p", [_B, _B, "..##.", "#.#.#", ".##.#", "..##.", ".#...", "#.#.."], bottom=-1)
_sym(0x2713, "check_mark", [_B, "....#", "...#.", "#..#.", ".##..", "..#..", _B])

# --- Arrows ------------------------------------------------------------------

_sym(0x21A6, "rightwards_arrow_from_bar", [_B, "#.#..", "#..#.", "#####", "#..#.", "#.#..", _B])
_sym(0x21AA, "rightwards_arrow_with_hook", ["......", ".#.#..", "#...#.", ".#####", "....#.", "...#..", "......"])
_sym(0x2197, "north_east_arrow", [_B, "..###", "...##", "..#.#", ".#...", "#....", _B])
_sym(0x2198, "south_east_arrow", _flip([_B, "..###", "...##", "..#.#", ".#...", "#....", _B]))
_sym(0x2196, "north_west_arrow", _mirror([_B, "..###", "...##", "..#.#", ".#...", "#....", _B]))
_sym(0x2199, "south_west_arrow", _flip(_mirror([_B, "..###", "...##", "..#.#", ".#...", "#....", _B])))
_sym(0x2195, "up_down_arrow", ["..#..", ".###.", "#.#.#", "..#..", "#.#.#", ".###.", "..#.."])
_sym(0x21C0, "rightwards_harpoon_barb_up", [_B, "..#..", "...#.", "#####", _B, _B, _B])
_sym(0x21CC, "rightwards_over_leftwards_harpoon", [_B, "...#.", "#####", _B, "#####", ".#...", _B])
_sym(0x21DD, "rightwards_squiggle_arrow", [".......", "....#..", ".#.#.#.", "#.#.###", ".....#.", "....#..", "......."])

# --- Binary operators ----------------------------------------------------------

_sym(0x2217, "asterisk_operator", [_B, "..#..", "#.#.#", ".###.", "#.#.#", "..#..", _B])
_sym(0x2218, "ring_operator", [_B, _B, ".###.", ".#.#.", ".###.", _B, _B])
_sym(0x2219, "bullet_operator", [_B, _B, "..#..", ".###.", "..#..", _B, _B])
_sym(0x22C4, "diamond_operator", [_B, _B, "..#..", ".#.#.", "..#..", _B, _B])
_sym(0x2216, "set_minus", [_B, "#....", ".#...", "..#..", "...#.", "....#", _B])
_sym(0x2295, "circled_plus", [_B, ".###.", "#.#.#", "#####", "#.#.#", ".###.", _B])
_sym(0x2296, "circled_minus", [_B, ".###.", "#...#", "#####", "#...#", ".###.", _B])
_sym(0x2297, "circled_times", [_B, ".###.", "##.##", "#.#.#", "##.##", ".###.", _B])
_sym(0x2298, "circled_division_slash", [_B, ".###.", "#..##", "#.#.#", "##..#", ".###.", _B])
_sym(0x2299, "circled_dot_operator", [_B, ".###.", "#...#", "#.#.#", "#...#", ".###.", _B])
_sym(0x2293, "square_cap", [_B, "#####", "#...#", "#...#", "#...#", "#...#", _B])
_sym(0x2294, "square_cup", [_B, "#...#", "#...#", "#...#", "#...#", "#####", _B])
_sym(0x228E, "multiset_union", ["#...#", "#.#.#", "#####", "#.#.#", "#...#", "#...#", ".###."])
_sym(0x22C9, "left_normal_factor_semidirect_product", [_B, "#...#", "##.#.", "#.#..", "##.#.", "#...#", _B])
_sym(0x22CA, "right_normal_factor_semidirect_product", [_B, "#...#", ".#.##", "..#.#", ".#.##", "#...#", _B])
_sym(0x2220, "angle", [_B, "....#", "...#.", "..#..", ".#...", "#....", "#####"])

# --- Relations -----------------------------------------------------------------

_LEQ = ["...#.", "..#..", ".#...", "..#..", "...#.", _B, "#####"]
_SUBSETEQ = [".####", "#....", "#....", "#....", ".####", _B, "#####"]
_PREC = [_B, "....#", "..##.", "##...", "..##.", "....#", _B]

_sym(0x2243, "asymptotically_equal_to", [_B, ".#..#", "#.#.#", "#..#.", _B, "#####", _B])
_sym(0x2245, "approximately_equal_to", [".#..#", "#.#.#", "#..#.", _B, "#####", _B, "#####"])
_sym(0x2261, "identical_to", [_B, "#####", _B, "#####", _B, "#####", _B])
_sym(0x224D, "equivalent_to", [_B, "#...#", ".###.", _B, ".###.", "#...#", _B])
_sym(0x2250, "approaches_the_limit", ["..#..", _B, "#####", _B, _B, "#####", _B])
_sym(0x225C, "delta_equal_to", ["..#..", ".#.#.", ".###.", _B, "#####", _B, "#####"])
_sym(0x226A, "much_less_than", ["......", "..#..#", ".#..#.", "#..#..", ".#..#.", "..#..#", "......"])
_sym(0x226B, "much_greater_than", _mirror(["......", "..#..#", ".#..#.", "#..#..", ".#..#.", "..#..#", "......"]))
_sym(0x227A, "precedes", _PREC)
_sym(0x227B, "succeeds", _mirror(_PREC))
_sym(0x2AAF, "precedes_above_single_line_equals", ["....#", "..##.", "##...", "..##.", "....#", _B, "#####"])
_sym(0x2AB0, "succeeds_above_single_line_equals", _mirror(["....#", "..##.", "##...", "..##.", "....#", _B, "#####"]))
_sym(0x2272, "less_than_or_equivalent_to", ["...#.", "..#..", ".#...", "..#..", "...#.", _B, ".##.#", "#..#."], bottom=-1)
_sym(0x2273, "greater_than_or_equivalent_to", [".#...", "..#..", "...#.", "..#..", ".#...", _B, ".##.#", "#..#."], bottom=-1)
_sym(0x2270, "neither_less_than_nor_equal_to", _slash(_LEQ))
_sym(0x2271, "neither_greater_than_nor_equal_to", _slash(_mirror(_LEQ)))
_sym(0x2288, "neither_subset_of_nor_equal_to", _slash(_SUBSETEQ))
_sym(0x2289, "neither_superset_of_nor_equal_to", _slash(_mirror(_SUBSETEQ)))
_sym(0x228A, "subset_of_with_not_equal_to", [".####", "#....", "#....", "#....", ".####", "....#", "#####", "..#.."], bottom=-1)
_sym(0x228B, "superset_of_with_not_equal_to", _mirror([".####", "#....", "#....", "#....", ".####", "....#", "#####", "..#.."]), bottom=-1)
_sym(0x2224, "does_not_divide", ["..#..", "..#..", "..#.#", "..##.", ".##..", "#.#..", "..#.."])
_sym(0x2323, "smile", [_B, _B, _B, "#...#", ".###.", _B, _B])
_sym(0x2322, "frown", [_B, _B, ".###.", "#...#", _B, _B, _B])

# --- Dots ------------------------------------------------------------------------
# Same 3 px period as Monocraft's horizontal ellipsis, centred on the math axis.

_sym(0x22EF, "midline_horizontal_ellipsis", [".......", ".......", ".......", "#..#..#", ".......", ".......", "......."])
_sym(0x22EE, "vertical_ellipsis", ["#", ".", ".", "#", ".", ".", "#"])
_sym(0x22F1, "down_right_diagonal_ellipsis", ["#......", ".......", ".......", "...#...", ".......", ".......", "......#"])

# --- Delimiters (stretchy variants live in math_glyphs.py) ------------------------

_sym(0x2308, "left_ceiling", [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".#..."])
_sym(0x2309, "right_ceiling", [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", "...#."])
_sym(0x230A, "left_floor", [".#...", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."])
_sym(0x230B, "right_floor", ["...#.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."])
_sym(0x2016, "double_vertical_line", [".#.#."] * 7)
_sym(0x27E8, "mathematical_left_angle_bracket", ["...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#"])
_sym(0x27E9, "mathematical_right_angle_bracket", ["#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."])

# --- Big operators (display variants live in math_glyphs.py) ----------------------

_INTEGRAL = ["...##", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "##..."]


def overlay(rows: list[str], other: list[str], dx: int) -> list[str]:
    """Union of two pixel images, `other` shifted right by `dx` pixels."""
    w = max(max(len(r) for r in rows), dx + max(len(r) for r in other))
    out = [list(r.ljust(w, ".")) for r in rows]
    for y, r in enumerate(other):
        for x, c in enumerate(r):
            if c == "#":
                out[y][dx + x] = "#"
    return ["".join(r) for r in out]


def repeat_integral(rows: list[str], n: int, step: int = 3) -> list[str]:
    """Side-by-side integral signs for \\iint / \\iiint (shared with display sizes)."""
    out = rows
    for i in range(1, n):
        out = overlay(out, rows, step * i)
    return out


_IINT = repeat_integral(_INTEGRAL, 2)
_sym(0x222C, "double_integral", _IINT, bottom=-1)
_sym(0x222D, "triple_integral", repeat_integral(_INTEGRAL, 3), bottom=-1)
# Surface integral: \iint with the contour ring of Monocraft's \oint.
_sym(0x222F, "surface_integral",
     overlay(_IINT, ["", "", ".######.", "#......#", ".######."], 0), bottom=-1)

_sym(0x2210, "n_ary_coproduct", [".#.#."] * 6 + ["#####"])
_sym(0x22C0, "n_ary_logical_and", ["..#..", "..#..", ".#.#.", ".#.#.", ".#.#.", "#...#", "#...#"])
_sym(0x22C1, "n_ary_logical_or", _flip(["..#..", "..#..", ".#.#.", ".#.#.", ".#.#.", "#...#", "#...#"]))
_sym(0x22C2, "n_ary_intersection", [".###."] + ["#...#"] * 6)
_sym(0x2A00, "n_ary_circled_dot", ["..###..", ".#...#.", "#.....#", "#..#..#", "#.....#", ".#...#.", "..###.."])
_sym(0x2A01, "n_ary_circled_plus", ["..###..", ".#.#.#.", "#..#..#", "#######", "#..#..#", ".#.#.#.", "..###.."])
_sym(0x2A02, "n_ary_circled_times", ["..###..", ".#...#.", "#.#.#.#", "#..#..#", "#.#.#.#", ".#...#.", "..###.."])

# --- Invisible operators -----------------------------------------------------------
# Function application / invisible times / separator / plus: MathML emits these
# between tokens. They must exist (zero-width) or the browser falls back.

_ZERO_WIDTH = {
    0x2061: "function_application",
    0x2062: "invisible_times",
    0x2063: "invisible_separator",
    0x2064: "invisible_plus",
}


def _dotless(rows: list[str]) -> list[str]:
    """Drop the tittle: blank the topmost ink row (and the gap row under it)."""
    out = list(rows)
    first = next(i for i, r in enumerate(out) if "#" in r)
    out[first] = "." * len(out[first])
    return out


def symbol_glyphs(base_by_cp: dict[int, Glyph],
                  proportional: bool = False) -> list[Glyph]:
    """Glyphs for every codepoint above that `base_by_cp` does not already have."""
    out: list[Glyph] = []

    def add(cp: int, name: str, rows: list[str], bottom: int) -> None:
        if cp in base_by_cp:
            return
        if proportional:
            advance = _proportional_advance_px(cp, rows)
            x_offset = _center_offset_px(rows, advance)
        else:
            width = max(len(r) for r in rows)
            advance = _ADVANCE_OVERRIDES_PX.get(cp, max(6, width + 1))
            x_offset = _center_offset_px(rows, advance) if cp in _ADVANCE_OVERRIDES_PX else 0.0
        out.append(Glyph(name=name, codepoint=cp, rows=rows, advance_px=advance,
                         x_offset_px=x_offset, bottom_px=bottom))

    for cp, (name, rows, bottom) in _SYMBOLS.items():
        add(cp, name, rows, bottom)

    # Dotless j, derived from Monocraft's own j so it matches exactly.
    j = base_by_cp.get(ord("j"))
    if j is not None:
        add(0x0237, "latin_small_letter_dotless_j", _dotless(j.rows), j.bottom_px)

    for cp, name in _ZERO_WIDTH.items():
        if cp not in base_by_cp:
            out.append(Glyph(name=name, codepoint=cp, rows=[], advance_px=0))
    return out
