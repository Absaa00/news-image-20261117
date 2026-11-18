#!/usr/bin/env python3
"""News in one image — Tuesday 17 November 2026.

Draws a 1024x1024 newspaper front page summarising the real world news
of Tuesday 17 November 2026, using only the Python standard library and
Pillow. No network access. Fully deterministic: two runs write identical
bytes to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories (all reported on 17 Nov 2026 by BBC, AP, Reuters, Al Jazeera,
ABC News and Just Security):
  1. Kerch Bridge span collapses after a Ukrainian strike.
  2. Trump lands in Manila for the ASEAN summit.
  3. Two tankers hit mines in the Strait of Hormuz.
  4. JPMorgan blames a software bug for Monday's banking outage.
  5. ULA Vulcan rocket fails; 40 Amazon Leo satellites lost.
  6. Nvidia reports its first earnings since Jensen Huang's exit.
Plus an "Also today" panel: Pentagon audit fail, Depardieu plea, Japan
scrambles jets after Russian aircraft enter its airspace.

SPDX-License-Identifier: MIT
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 16

# Palette: newsprint.
PAPER = (246, 241, 231)
INK = (18, 18, 18)
NAVY = (19, 35, 63)
NAVY_LIGHT = (38, 62, 102)
GOLD = (217, 164, 65)
RED = (164, 30, 34)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
RULE = (150, 145, 132)
GREY = (90, 86, 76)
SKY = (207, 227, 238)
SEA = (46, 111, 142)
DARK_SKY = (22, 35, 61)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu font; fall back to Pillow's built-in bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines of text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text and clip to max_lines, adding an ellipsis if clipped."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + " ..."
    return lines


def kicker(draw, x, y, label, color=RED):
    fnt = SANS_B(14)
    draw.text((x, y), label, font=fnt, fill=color)
    return y + 20


# ---------------------------------------------------------------- scenes
def scene_bridge(d, x0, y0, x1, y1):
    """Kerch Bridge: two deck halves, a collapsed middle span, smoke."""
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    # sun
    d.ellipse([x1 - 52, y0 + 10, x1 - 18, y0 + 44], fill=(250, 214, 120))
    # sea
    sea_y = y0 + int((y1 - y0) * 0.68)
    d.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for i, wy in enumerate((sea_y + 14, sea_y + 34, sea_y + 54)):
        for wx in range(x0 + 8 + (i % 2) * 26, x1 - 20, 52):
            d.arc([wx, wy, wx + 34, wy + 12], 0, 180, fill=WHITE, width=2)
    deck_y = y0 + int((y1 - y0) * 0.52)
    mid = (x0 + x1) // 2
    # pylons
    for px in (x0 + 52, x1 - 62):
        d.rectangle([px, deck_y - 78, px + 10, deck_y], fill=(58, 74, 90))
        d.rectangle([px - 8, deck_y - 86, px + 18, deck_y - 78], fill=(58, 74, 90))
    # cables
    d.line([x0 + 57, deck_y - 82, mid - 52, deck_y], fill=(120, 130, 140), width=2)
    d.line([x1 - 57, deck_y - 82, mid + 52, deck_y], fill=(120, 130, 140), width=2)
    # deck halves
    d.rectangle([x0 + 8, deck_y, mid - 46, deck_y + 12], fill=(58, 74, 90))
    d.rectangle([mid + 46, deck_y, x1 - 8, deck_y + 12], fill=(58, 74, 90))
    # collapsed middle span, tilted down into the water
    d.polygon([(mid - 46, deck_y), (mid + 46, deck_y + 12),
               (mid + 38, deck_y + 46), (mid - 38, deck_y + 40)],
              fill=(120, 34, 30))
    # smoke over the break
    for cx, cy, r in ((mid - 18, deck_y - 26, 15), (mid + 6, deck_y - 40, 19),
                      (mid + 30, deck_y - 24, 13)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 118))
    # blast flash
    d.polygon([(mid, deck_y - 34), (mid - 10, deck_y - 12), (mid - 2, deck_y - 14),
               (mid, deck_y - 2), (mid + 8, deck_y - 16), (mid + 12, deck_y - 10)],
              fill=(250, 180, 60))


def scene_manila(d, x0, y0, x1, y1):
    """Manila skyline at dusk with three summit flags."""
    d.rectangle([x0, y0, x1, y1], fill=(255, 233, 184))
    d.ellipse([x1 - 58, y0 + 12, x1 - 22, y0 + 48], fill=(250, 190, 80))
    base = y1 - 8
    heights = [58, 92, 70, 110, 84, 64, 98, 74]
    bw = (x1 - x0 - 16) // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + 8 + i * bw
        d.rectangle([bx, base - hh, bx + bw - 4, base], fill=(58, 74, 90))
        for wy in range(base - hh + 8, base - 6, 14):
            for wx in range(bx + 4, bx + bw - 8, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(250, 214, 120))
    # three flags: US, Philippines, Thailand
    flags = [
        ("US", [(178, 34, 52), WHITE, (178, 34, 52), WHITE, (178, 34, 52)]),
        ("PH", [(0, 56, 147), (206, 17, 38)]),
        ("TH", [(165, 25, 49), WHITE, (45, 42, 125), WHITE, (165, 25, 49)]),
    ]
    fx = x0 + 14
    for _name, stripes in flags:
        d.line([fx, y0 + 14, fx, y0 + 66], fill=(60, 60, 60), width=2)
        fh = 34
        for j, col in enumerate(stripes):
            d.rectangle([fx + 2, y0 + 14 + j * fh // len(stripes),
                         fx + 34, y0 + 14 + (j + 1) * fh // len(stripes)],
                        fill=col)
        fx += 52


def scene_tanker(d, x0, y0, x1, y1):
    """Oil tanker, a naval mine, and fire on deck."""
    d.rectangle([x0, y0, x1, y1], fill=(220, 235, 245))
    sea_y = y0 + int((y1 - y0) * 0.66)
    d.rectangle([x0, sea_y, x1, y1], fill=SEA)
    for wx in range(x0 + 10, x1 - 20, 46):
        d.arc([wx, sea_y + 16, wx + 30, sea_y + 26], 0, 180, fill=WHITE, width=2)
    # hull
    d.polygon([(x0 + 14, sea_y - 6), (x1 - 14, sea_y - 6), (x1 - 34, sea_y + 30),
               (x0 + 34, sea_y + 30)], fill=(34, 34, 34))
    d.rectangle([x0 + 14, sea_y - 6, x1 - 14, sea_y + 2], fill=(120, 30, 30))
    # containers + bridge tower
    for i, col in enumerate(((200, 90, 40), (40, 110, 70), (200, 160, 40))):
        d.rectangle([x0 + 34 + i * 52, sea_y - 34, x0 + 80 + i * 52, sea_y - 6],
                    fill=col)
    d.rectangle([x1 - 74, sea_y - 52, x1 - 40, sea_y - 6], fill=WHITE)
    d.rectangle([x1 - 70, sea_y - 46, x1 - 44, sea_y - 38], fill=(40, 80, 120))
    # flame on deck
    fx = x0 + 150
    d.polygon([(fx - 16, sea_y - 6), (fx - 4, sea_y - 34), (fx + 2, sea_y - 14),
               (fx + 10, sea_y - 38), (fx + 18, sea_y - 6)],
              fill=(240, 120, 20))
    d.polygon([(fx - 8, sea_y - 6), (fx - 2, sea_y - 22), (fx + 4, sea_y - 10),
               (fx + 8, sea_y - 24), (fx + 12, sea_y - 6)],
              fill=(250, 200, 60))
    # naval mine, lower right, inside the scene box
    mx, my = x1 - 44, sea_y + 20
    for ang in range(0, 360, 45):
        import math
        r1, r2 = 12, 20
        x_a = mx + int(r1 * math.cos(math.radians(ang)))
        y_a = my + int(r1 * math.sin(math.radians(ang)))
        x_b = mx + int(r2 * math.cos(math.radians(ang)))
        y_b = my + int(r2 * math.sin(math.radians(ang)))
        d.line([x_a, y_a, x_b, y_b], fill=(20, 20, 20), width=3)
    d.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=(20, 20, 20))


def scene_bank(d, x0, y0, x1, y1):
    """Bank facade with a warning screen: the outage."""
    d.rectangle([x0, y0, x1, y1], fill=(238, 232, 214))
    # pediment + columns
    d.polygon([(x0 + 30, y0 + 26), (x1 - 30, y0 + 26), ((x0 + x1) // 2, y0 + 6)],
              fill=(210, 198, 168))
    d.rectangle([x0 + 30, y0 + 26, x1 - 30, y0 + 34], fill=(190, 176, 142))
    for cx in range(x0 + 44, x1 - 44, 34):
        d.rectangle([cx, y0 + 38, cx + 14, y1 - 26], fill=(228, 216, 184))
        d.rectangle([cx - 3, y0 + 34, cx + 17, y0 + 40], fill=(210, 198, 168))
    d.rectangle([x0 + 24, y1 - 26, x1 - 24, y1 - 14], fill=(190, 176, 142))
    # warning monitor, centre
    mx0, my0, mx1, my1 = (x0 + x1) // 2 - 52, y0 + 52, (x0 + x1) // 2 + 52, y0 + 104
    d.rectangle([mx0, my0, mx1, my1], fill=(24, 28, 38))
    d.rectangle([mx0 + 4, my0 + 4, mx1 - 4, my1 - 4], outline=(250, 200, 60), width=2)
    d.text(((mx0 + mx1) // 2 - 7, my0 + 12), "!", font=SANS_B(26), fill=(250, 200, 60))
    d.line([mx0 + 14, my1 - 14, mx0 + 40, my1 - 26, mx0 + 62, my1 - 20,
            mx0 + 88, my1 - 38], fill=(230, 60, 50), width=3)


def scene_rocket(d, x0, y0, x1, y1):
    """Vulcan rocket breaking apart mid-flight; satellites tumbling away."""
    d.rectangle([x0, y0, x1, y1], fill=DARK_SKY)
    for sx, sy in ((x0 + 20, y0 + 14), (x0 + 90, y0 + 26), (x1 - 30, y0 + 16),
                   (x0 + 150, y0 + 10), (x1 - 90, y0 + 40), (x0 + 40, y0 + 48)):
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=WHITE)
    mid_y = y0 + (y1 - y0) // 2 + 6
    # broken-off nose piece, tilted, upper left
    d.polygon([(x0 + 26, y0 + 18), (x0 + 44, y0 + 12), (x0 + 52, y0 + 30),
               (x0 + 34, y0 + 38)], fill=(200, 200, 200))
    d.polygon([(x0 + 26, y0 + 18), (x0 + 44, y0 + 12), (x0 + 48, y0 + 20),
               (x0 + 30, y0 + 26)], fill=(200, 60, 40))
    # main body, horizontal
    bx0, bx1 = x0 + 58, x1 - 62
    d.rectangle([bx0, mid_y - 13, bx1, mid_y + 13], fill=(230, 230, 230))
    d.rectangle([bx0, mid_y - 13, bx0 + 26, mid_y + 13], fill=(200, 60, 40))
    d.rectangle([bx1 - 34, mid_y - 13, bx1, mid_y + 13], fill=(200, 60, 40))
    # fins
    d.polygon([(bx1, mid_y - 13), (bx1 + 16, mid_y - 26), (bx1 + 16, mid_y - 13)],
              fill=(200, 60, 40))
    d.polygon([(bx1, mid_y + 13), (bx1 + 16, mid_y + 26), (bx1 + 16, mid_y + 13)],
              fill=(200, 60, 40))
    # flame
    d.polygon([(bx1 + 16, mid_y - 8), (x1 - 8, mid_y), (bx1 + 16, mid_y + 8)],
              fill=(250, 180, 60))
    # explosion burst where the stage broke
    ex, ey = bx0 + 62, mid_y - 4
    for ang in range(0, 360, 30):
        import math
        x_a = ex + int(9 * math.cos(math.radians(ang)))
        y_a = ey + int(9 * math.sin(math.radians(ang)))
        x_b = ex + int(24 * math.cos(math.radians(ang)))
        y_b = ey + int(24 * math.sin(math.radians(ang)))
        d.line([x_a, y_a, x_b, y_b], fill=(250, 160, 40), width=4)
    d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(250, 210, 90))
    # tumbling satellites
    for sx, sy in ((x0 + 30, y1 - 22), (x1 - 46, y0 + 66), (x0 + 120, y1 - 16)):
        d.rectangle([sx - 5, sy - 3, sx + 5, sy + 3], fill=(140, 170, 210))
        d.rectangle([sx - 11, sy - 1, sx - 5, sy + 1], fill=(90, 120, 160))
        d.rectangle([sx + 5, sy - 1, sx + 11, sy + 1], fill=(90, 120, 160))


def scene_chip(d, x0, y0, x1, y1):
    """AI chip with a market chart behind it."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 238, 244))
    # chart line, rising then wobbling
    pts = []
    n = 9
    vals = [0.78, 0.70, 0.74, 0.60, 0.66, 0.52, 0.58, 0.44, 0.36]
    for i, v in enumerate(vals):
        px = x0 + 12 + i * (x1 - x0 - 24) // (n - 1)
        py = y0 + 16 + int(v * (y1 - y0 - 32))
        pts.append((px, py))
    d.line(pts, fill=(34, 139, 80), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(34, 139, 80))
    # chip, centre
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    s = 46
    for k in range(-2, 3):
        d.line([cx + k * 18, cy - s - 10, cx + k * 18, cy - s], fill=(180, 150, 60),
               width=3)
        d.line([cx + k * 18, cy + s, cx + k * 18, cy + s + 10], fill=(180, 150, 60),
               width=3)
        d.line([cx - s - 10, cy + k * 18, cx - s, cy + k * 18], fill=(180, 150, 60),
               width=3)
        d.line([cx + s, cy + k * 18, cx + s + 10, cy + k * 18], fill=(180, 150, 60),
               width=3)
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(26, 26, 46))
    d.rectangle([cx - s + 6, cy - s + 6, cx + s - 6, cy + s - 6],
                outline=(180, 150, 60), width=2)
    d.text((cx - 24, cy - 11), "NVDA", font=SANS_B(17), fill=WHITE)


# ---------------------------------------------------------------- layout
def draw_masthead(d):
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 99], fill=GOLD)
    title = "THE WORLD IN ONE PAGE"
    fnt = SERIF_B(44)
    tw = d.textlength(title, font=fnt)
    d.text(((W - tw) / 2, 12), title, font=fnt, fill=WHITE)
    sub = "TUESDAY, 17 NOVEMBER 2026  ·  SIX STORIES THAT DEFINED THE DAY"
    fnt2 = SANS_B(15)
    tw2 = d.textlength(sub, font=fnt2)
    d.text(((W - tw2) / 2, 64), sub, font=fnt2, fill=GOLD)


def draw_lead(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=2)
    tx = x + 16
    ty = y + 14
    ty = kicker(d, tx, ty, "UKRAINE WAR  ·  TOP STORY")
    head = fit_lines(d, "Kerch Bridge span collapses after Ukrainian strike",
                     SERIF_B(30), 600, 2)
    ty = text_block(d, tx, ty + 2, head, SERIF_B(30), leading=36)
    cap = fit_lines(
        d,
        "Kyiv calls it an \u201cunprecedented operation\u201d weeks in the making; "
        "Moscow vows to rebuild the road link to occupied Crimea as both sides "
        "trade strikes on bridges.",
        SANS(16), 600, 4)
    text_block(d, tx, ty + 8, cap, SANS(16), fill=GREY, leading=21)
    ix0, iy0 = x + 640, y + 14
    ix1, iy1 = x + w - 16, y + h - 14
    scene_bridge(d, ix0, iy0, ix1, iy1)
    d.rectangle([ix0, iy0, ix1, iy1], outline=RULE, width=1)
    d.text((ix0, iy1 + 2), "", font=SANS(10), fill=GREY)


def draw_panel(d, x, y, w, h, kick, headline, caption, scene):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=2)
    ih = 118
    scene(d, x + 8, y + 8, x + w - 8, y + 8 + ih)
    d.rectangle([x + 8, y + 8, x + w - 8, y + 8 + ih], outline=RULE, width=1)
    ty = y + 8 + ih + 10
    ty = kicker(d, x + 12, ty, kick)
    head = fit_lines(d, headline, SERIF_B(19), w - 24, 3)
    ty = text_block(d, x + 12, ty + 2, head, SERIF_B(19), leading=23)
    cap = fit_lines(d, caption, SANS(13), w - 24, 4)
    text_block(d, x + 12, ty + 6, cap, SANS(13), fill=GREY, leading=17)


def draw_also_today(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=2)
    ty = y + 12
    ty = kicker(d, x + 12, ty, "ALSO TODAY")
    items = [
        ("Pentagon audit fails again.",
         "Independent auditors cannot verify $4.8tn in assets \u2014 the ninth "
         "year running."),
        ("Depardieu admits assault charge.",
         "The French actor drops his appeal in a Paris court."),
        ("Japan scrambles jets.",
         "Two suspected Russian aircraft entered Japanese airspace."),
    ]
    for bold, rest in items:
        d.rectangle([x + 12, ty + 5, x + 20, ty + 13], fill=RED)
        lines = fit_lines(d, bold + " " + rest, SANS(13), w - 40, 3)
        ty = text_block(d, x + 28, ty, lines, SANS(13), fill=INK, leading=17)
        ty += 12


def draw_footer(d):
    d.rectangle([0, 1000, W, H], fill=NAVY)
    txt = ("Sources: BBC · AP · Reuters · Al Jazeera · ABC News · Just Security  —  "
           "Drawn entirely by code; no photographs.")
    fnt = SANS(12)
    tw = d.textlength(txt, font=fnt)
    d.text(((W - tw) / 2, 1006), txt, font=fnt, fill=(200, 205, 215))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    # lead story
    draw_lead(d, MARGIN, 108, W - 2 * MARGIN, 272)
    # grid rows
    px = [MARGIN, 351, 686]
    pw = 322
    row1 = [
        ("DIPLOMACY  ·  ASIA",
         "Trump lands in Manila for ASEAN summit",
         "First stop of a three-day Asia trip; signs a joint trade statement "
         "with Thailand before talks with Xi and Putin in China.",
         scene_manila),
        ("MIDDLE EAST  ·  ENERGY",
         "Two tankers hit mines in Strait of Hormuz",
         "Iran\u2019s Revolutionary Guards say the tankers caught fire on an "
         "\u201cunauthorised\u201d route; a third US carrier arrives in the region.",
         scene_tanker),
        ("MARKETS  ·  BANKING",
         "JPMorgan blames software bug for outage",
         "Online banking, branches and Zelle slowed on Monday; the bank says "
         "there is no sign of a cyberattack.",
         scene_bank),
    ]
    for (kick, head, cap, scene), x in zip(row1, px):
        draw_panel(d, x, 388, pw, 300, kick, head, cap, scene)
    row2 = [
        ("SPACE",
         "Vulcan rocket fails; 40 Amazon satellites lost",
         "ULA\u2019s Vulcan suffered an anomaly ten minutes after lift-off from "
         "Cape Canaveral and never reached orbit.",
         scene_rocket),
        ("TECH  ·  EARNINGS",
         "Nvidia reports after Huang\u2019s exit",
         "First earnings since Jensen Huang resigned; Wall Street watches "
         "AI-chip demand and the new chief\u2019s plan.",
         scene_chip),
    ]
    for (kick, head, cap, scene), x in zip(row2, px[:2]):
        draw_panel(d, x, 696, pw, 292, kick, head, cap, scene)
    draw_also_today(d, px[2], 696, pw, 292)
    draw_footer(d)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    if not out_dir.strip():
        print("error: MAKEFUN_OUTPUT_DIR is set but empty", file=sys.stderr)
        return 1
    out_dir = os.path.abspath(os.path.expanduser(out_dir))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output dir {out_dir}: {exc}", file=sys.stderr)
        return 1
    path = os.path.join(out_dir, "entry.png")
    img = build()
    try:
        img.save(path, format="PNG")
    except OSError as exc:
        print(f"error: cannot write {path}: {exc}", file=sys.stderr)
        return 1
    size = os.path.getsize(path)
    if size > 1024 * 1024:
        print(f"error: {path} is {size} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    print(f"wrote {path} ({img.size[0]}x{img.size[1]}, {size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
