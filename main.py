#!/usr/bin/env python3
"""THE DAILY GLOBE — front page summing up Tuesday 17 November 2026.

A single-file, standard-library-only program. It draws a newspaper front
page with a small built-in 5x7 bitmap font and writes a deterministic
1024x1024 PNG. No network, no randomness, no time, no files read: two runs
produce byte-identical output.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py        (writes out/entry.png)
The grader runs it as:  python3 -P -s /bot/main.py (writes /output/entry.png)
"""

import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- font -----
# One glyph per character: 7 rows of 5 pixels, '#' = ink, '.' = blank.
# Written for this entry; nothing here is copied from any other program.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#....", "#....", "#....", ".###."),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".###.", "#...#", "#...#", ".###.", "..##."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
}

FONT.update({
    '0': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '—': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", "#.#.#", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '•': (".....", ".....", ".##..", ".##..", ".##..", ".....", "....."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
})

# ------------------------------------------------------------------ canvas --
W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (185, 28, 28)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(rgb) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, rgb):
        self.rect(x, y, w, 1, rgb)

    def vline(self, x, y, h, rgb):
        self.rect(x, y, 1, h, rgb)

    def line(self, x0, y0, x1, y1, rgb):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, rgb)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, rgb, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, rgb)
                elif r * r - r <= d2 <= r * r:
                    self.set(xx, yy, rgb)

    def poly(self, pts, rgb):
        # Filled polygon via scanline fill (convex or concave, even-odd).
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, rgb)


def text_w(s, scale):
    return sum((6 if ch != ' ' else 6) for ch in s) * scale - scale


def draw_text(cv, x, y, s, scale, rgb):
    """Draw text left-aligned at (x, y); returns the width used."""
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == '#':
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, rgb)
        cx += 6 * scale
    return cx - x - scale


def draw_text_centered(cv, cx, y, s, scale, rgb):
    w = text_w(s, scale)
    draw_text(cv, cx - w // 2, y, s, scale, rgb)
    return w


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, max_w, scale, rgb, leading=None):
    lh = leading if leading is not None else 10 * scale
    for i, ln in enumerate(wrap(s, max_w, scale)):
        draw_text(cv, x, y + i * lh, ln, scale, rgb)
    return y + len(wrap(s, max_w, scale)) * lh


# --------------------------------------------------------------------- png --
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------------ scenes --
SKY = (191, 217, 232)
SEA = (43, 106, 143)
DEEPSEA = (30, 82, 116)
ISLAND = (107, 142, 90)
SAND = (201, 178, 130)
DARK = (58, 58, 58)
FIRE = (232, 89, 12)
FLAME = (245, 158, 11)
SMOKE = (120, 120, 118)


def scene_gulf(cv, x, y, w, h):
    """Strait of Hormuz: sky, sea, Qeshm island, a jet, a burning tanker."""
    cv.rect(x, y, w, h * 2 // 5, SKY)
    cv.rect(x, y + h * 2 // 5, w, h - h * 2 // 5, SEA)
    cv.rect(x, y + h * 2 // 5, w, 3, SAND)
    # Island (Qeshm) on the right.
    cv.poly([(x + w * 3 // 5, y + h * 2 // 5), (x + w * 3 // 4, y + h // 4),
             (x + w - 8, y + h * 2 // 5)], ISLAND)
    # Jet, top left, with motion lines.
    jx, jy = x + w // 8, y + h // 6
    cv.poly([(jx, jy), (jx + 34, jy + 6), (jx, jy + 12)], DARK)
    cv.poly([(jx + 12, jy + 2), (jx + 26, jy - 6), (jx + 24, jy + 6)], DARK)
    cv.hline(jx - 46, jy + 6, 40, (255, 255, 255))
    cv.hline(jx - 30, jy + 12, 24, (255, 255, 255))
    # Explosion over the island.
    ex, ey = x + w * 3 // 4, y + h // 5
    for r, c in ((26, FIRE), (18, FLAME), (10, (255, 214, 64))):
        cv.circle(ex, ey, r, c)
    cv.circle(ex, ey - 30, 8, SMOKE)
    cv.circle(ex - 10, ey - 42, 6, SMOKE)
    # Tanker on the sea, left, with fire.
    tx, ty = x + w // 5, y + h * 3 // 4
    cv.rect(tx, ty, 120, 16, (30, 30, 34))
    cv.rect(tx + 18, ty - 14, 22, 14, (200, 60, 40))
    cv.rect(tx + 84, ty - 10, 12, 10, (220, 220, 220))
    cv.circle(tx + 60, ty - 12, 9, FIRE)
    cv.circle(tx + 60, ty - 22, 6, FLAME)
    cv.hline(tx - 30, ty + 20, 180, (255, 255, 255))


def scene_kerch(cv, x, y, w, h):
    """A bridge over the strait with a broken span and smoke."""
    cv.rect(x, y, w, h * 3 // 5, SKY)
    cv.rect(x, y + h * 3 // 5, w, h - h * 3 // 5, SEA)
    deck = y + h // 2
    cv.rect(x, deck, w, 5, DARK)
    # Arches left and right of the gap.
    for ax in (x + 30, x + w - 130):
        cv.line(ax, deck, ax + 50, deck - 26, DARK)
        cv.line(ax + 100, deck, ax + 50, deck - 26, DARK)
    # Broken span: tilted pieces falling into the gap.
    gx = x + w // 2 - 40
    cv.line(gx, deck, gx + 34, deck + 26, DARK)
    cv.line(gx + 44, deck, gx + 78, deck + 20, DARK)
    cv.circle(gx + 40, deck - 14, 10, SMOKE)
    cv.circle(gx + 52, deck - 26, 7, SMOKE)
    cv.circle(gx + 40, deck - 6, 7, FIRE)
    # Pylons.
    cv.rect(x + 24, deck - 34, 5, 34, DARK)
    cv.rect(x + w - 30, deck - 34, 5, 34, DARK)


def scene_shenzhen(cv, x, y, w, h):
    """A skyline with three flags: a summit in Shenzhen."""
    cv.rect(x, y, w, h, (223, 232, 242))
    cv.circle(x + w - 46, y + 22, 14, (245, 190, 60))
    base = y + h
    towers = [(0, 52), (34, 78), (76, 44), (112, 88), (152, 60), (196, 96),
              (238, 54), (280, 80), (322, 48), (360, 70), (398, 40)]
    for tx, th in towers:
        cv.rect(x + tx, base - th, 30, th, (51, 65, 85))
        for wy in range(base - th + 8, base - 6, 12):
            cv.rect(x + tx + 6, wy, 5, 5, (250, 204, 21))
            cv.rect(x + tx + 18, wy, 5, 5, (250, 204, 21))
    # Three flag poles with red flags.
    for i, fx in enumerate((x + 90, x + w // 2, x + w - 130)):
        cv.vline(fx, y + 8, 34, DARK)
        cv.rect(fx, y + 8, 30, 16, RED if i != 1 else (200, 160, 40))


def scene_mongolia(cv, x, y, w, h):
    """Steppe, a podium, and the Mongolian flag."""
    cv.rect(x, y, w, h * 3 // 5, (232, 238, 247))
    cv.rect(x, y + h * 3 // 5, w, h - h * 3 // 5, (122, 158, 92))
    cv.circle(x + w - 60, y + 20, 12, (245, 190, 60))
    # Flag pole with blue flag and red stripe.
    px = x + w // 2
    cv.vline(px, y + 10, h // 2, DARK)
    cv.rect(px, y + 10, 44, 24, (0, 94, 180))
    cv.rect(px, y + 10, 10, 24, (200, 40, 40))
    # Podium.
    cv.poly([(px - 52, y + h - 8), (px - 40, y + h // 2 + 8),
             (px + 40, y + h // 2 + 8), (px + 52, y + h - 8)], (124, 90, 58))
    cv.rect(px - 30, y + h // 2 + 8, 60, 5, (90, 64, 40))
    # Microphones.
    cv.line(px - 12, y + h // 2 + 8, px - 18, y + h // 2 - 12, DARK)
    cv.line(px + 12, y + h // 2 + 8, px + 18, y + h // 2 - 12, DARK)
    cv.circle(px - 18, y + h // 2 - 14, 3, DARK)
    cv.circle(px + 18, y + h // 2 - 14, 3, DARK)


def scene_japan(cv, x, y, w, h):
    """Two jets over the sea off Japan, first breach since 2024."""
    cv.rect(x, y, w, h * 3 // 5, (207, 224, 242))
    cv.rect(x, y + h * 3 // 5, w, h - h * 3 // 5, SEA)
    cv.circle(x + 44, y + 20, 13, (245, 190, 60))
    for jx, jy in ((x + w // 4, y + h // 4), (x + w // 2, y + h // 5)):
        cv.poly([(jx, jy), (jx + 36, jy + 6), (jx, jy + 12)], DARK)
        cv.poly([(jx + 12, jy + 2), (jx + 28, jy - 7), (jx + 26, jy + 6)], DARK)
        cv.hline(jx - 40, jy + 6, 34, (255, 255, 255))
    # Waves.
    for wx in range(x + 12, x + w - 20, 46):
        cv.hline(wx, y + h * 3 // 4, 26, (255, 255, 255))

# ------------------------------------------------------------------ layout --
MX = 32                 # side margin
CW = W - 2 * MX          # content width: 960
COL = (CW - 24) // 2     # grid column width: 468


def story(cv, x, y, tab, headlines, body, scene):
    """One grid story: red tab, headline, body, picture strip. Fixed height."""
    draw_text(cv, x, y, tab, 2, RED)
    hy = y + 20
    for ln in headlines:
        draw_text(cv, x, hy, ln, 3, INK)
        hy += 25
    by = y + 20 + 50 + 6
    for i, ln in enumerate(wrap(body, COL, 2)):
        draw_text(cv, x, by + i * 20, ln, 2, INK)
    sy = y + 20 + 50 + 6 + 80 + 8
    cv.rect(x, sy, COL, 64, SKY)
    scene(cv, x, sy, COL, 64)
    cv.rect(x, sy, COL, 2, INK)
    cv.rect(x, sy + 62, COL, 2, INK)
    return y + 20 + 50 + 6 + 80 + 8 + 64


def build(cv):
    cv.rect(0, 0, W, H, PAPER)
    # Masthead.
    cv.rect(MX, 16, CW, 2, INK)
    draw_text_centered(cv, W // 2, 26, "THE DAILY GLOBE", 8, INK)
    cv.rect(MX, 90, CW, 3, RED)
    draw_text_centered(cv, W // 2, 98, "TUESDAY, 17 NOVEMBER 2026", 2, RED)
    cv.rect(MX, 120, CW, 2, INK)

    # Lead story: the Gulf.
    draw_text_centered(cv, W // 2, 130, "THE GULF — WAR AT SEA", 2, RED)
    draw_text_centered(cv, W // 2, 152, "U.S. STRIKES IRAN", 7, INK)
    draw_text_centered(cv, W // 2, 206, "IRAN HITS BACK IN BAHRAIN", 5, INK)
    draw_para(cv, MX, 250,
              "Jets hit an IRGC missile site on Qeshm Island as Tehran's drones "
              "target a U.S. radar base — and a tanker burns in the Strait of Hormuz.",
              CW, 2, INK)
    cv.rect(MX, 292, CW, 130, SKY)
    scene_gulf(cv, MX, 292, CW, 130)
    cv.rect(MX, 292, CW, 2, INK)
    cv.rect(MX, 420, CW, 2, INK)
    draw_text(cv, MX, 428, "A tanker burns in the Strait of Hormuz.", 2, GREY)
    cv.rect(MX, 458, CW, 2, INK)

    # Grid, row one.
    y1 = story(cv, MX, 470, "UKRAINE", ["KERCH BRIDGE HIT AGAIN"],
               "A second strike in two days drops a road span into the strait, "
               "Kyiv says. Traffic halts. Russia hits two bridges in Kyiv in reply.",
               scene_kerch)
    story(cv, MX + COL + 24, 470, "SUMMIT",
          ["TRUMP, XI, PUTIN", "TO MEET THURSDAY"],
          "The three leaders will hold a three-way meeting in Shenzhen at the "
          "APEC summit, days after the week's attacks.",
          scene_shenzhen)
    # Grid, row two.
    y2 = story(cv, MX, 710, "MONGOLIA", ["PRESIDENT QUITS", "OVER GRAFT CLAIMS"],
               "Ukhnaa Khurelsukh steps down a day after the opposition accused "
               "him of graft and threatened impeachment.",
               scene_mongolia)
    story(cv, MX + COL + 24, 710, "ASIA", ["JAPAN SCRAMBLES JETS"],
          "Two suspected Russian planes enter Japanese airspace off Fukuoka — "
          "the first breach since September 2024. Tokyo protests.",
          scene_japan)
    _ = (y1, y2)

    # In Brief band.
    cv.rect(MX, 946, CW, 72, LIGHT)
    cv.rect(MX, 946, CW, 2, INK)
    cv.rect(MX, 1016, CW, 2, INK)
    cv.rect(MX, 946, 2, 72, INK)
    cv.rect(MX + CW - 2, 946, 2, 72, INK)
    draw_text(cv, MX + 12, 952, "IN BRIEF", 2, RED)
    briefs = ["• An-12 crashes in Siberia; 19 dead.",
              "• Prague trains collide; 46 hurt.",
              "• West urges Gaza crossings open."]
    for i, b in enumerate(briefs):
        bx = MX + 12 + i * 320
        for j, ln in enumerate(wrap(b, 296, 2)):
            draw_text(cv, bx, 974 + j * 20, ln, 2, INK)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    build(cv)
    path = os.path.join(out, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
