"""Build the original 40-item newspaper illustration outside the offline grade sandbox."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W = H = 1024
P = "#F5F1E7"
D = "#162823"
G = "#716E66"
RULE = "#CFC7B8"
RED = "#BD4A32"
REGIONS = ["North America", "South America", "Europe", "Africa", "Asia", "Oceania"]
PALETTE = ["#457481", "#BE5339", "#648163", "#A77345", "#645D78", "#648783"]
FONTS = {
    "serif": "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "bold": "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf",
    "sans": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
}


def ft(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


def label(d: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, color: str = D, kind: str = "sans") -> None:
    d.text(xy, value, fill=color, font=ft(kind, size))


def linebreak(d: ImageDraw.ImageDraw, text: str, width: int, face: ImageFont.FreeTypeFont) -> list[str]:
    words = text.split()
    rows: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and d.textbbox((0, 0), candidate, font=face)[2] > width:
            rows.append(current)
            current = word
        else:
            current = candidate
    if current:
        rows.append(current)
    return rows


def rule(d: ImageDraw.ImageDraw, y: int, x0: int = 32, x1: int = 992, color: str = RULE, thickness: int = 1) -> None:
    d.line((x0, y, x1, y), fill=color, width=thickness)


def sigil(d: ImageDraw.ImageDraw, coords: tuple[int, int, int, int], idx: int, accent: str, lead: bool) -> None:
    x0, y0, x1, y1 = coords
    bg = ["#DCE7E4", "#EADFD4", "#E4E9DA", "#E9E0D1", "#E5DEEB", "#DCE8E6"][idx % 6]
    d.rectangle(coords, fill=bg)
    cx, cy = int(x0 + (x1 - x0) * .70), int(y0 + (y1 - y0) * .40)
    radius = min(28, (x1 - x0) // 5, max(8, (y1 - y0) // 2 - 4))
    for rr in (radius // 3, radius * 2 // 3, radius):
        d.arc((cx - rr, cy - rr, cx + rr, cy + rr), 190, 342, fill=accent, width=2)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=accent)
    d.arc((x0 + 7, y0 + 4, x0 + (x1 - x0) * .78, y0 + (y1 - y0) * .94), 196, 344, fill="#FFFDF8", width=2)
    d.line((x0 + 8, y1 - 8, x0 + (x1 - x0) * .38, y0 + 8), fill=accent, width=2)
    d.line((x0 + (x1 - x0) * .39, y1 - 8, x0 + (x1 - x0) * .10, y0 + 10), fill="#FFFDF8", width=2)
    if lead:
        d.line((x0 + 10, y1 - 6, x1 - 10, y1 - 6), fill=accent, width=2)


def draw_card(d: ImageDraw.ImageDraw, item: dict, rect: tuple[int, int, int, int], ordinal: int, lead: bool = False) -> None:
    x0, y0, x1, y1 = rect
    accent = PALETTE[ordinal % 6]
    d.rounded_rectangle(rect, radius=5, fill="#FFFDF7", outline=RULE, width=1)
    main_lead = bool(lead and item["id"] == 1)
    image_h = 94 if main_lead else 65 if lead else 38
    sigil(d, (x0 + 1, y0 + 1, x1 - 1, y0 + image_h), ordinal, accent, lead)
    metadata = f"{item['place'].upper()}  ·  {item['desk']}"
    meta = ft("bold", 8 if lead else 7)
    if d.textbbox((0, 0), metadata, font=meta)[2] > x1 - x0 - 16:
        while metadata and d.textbbox((0, 0), metadata + "…", font=meta)[2] > x1 - x0 - 16:
            metadata = metadata[:-1]
        metadata = metadata.rstrip() + "…"
    label(d, (x0 + 8, y0 + image_h + (6 if lead else 4)), metadata, 8 if lead else 7, accent, "bold")
    headline_size = 20 if main_lead else 14 if lead else 12
    title_font = ft("serif", headline_size)
    text_rows = linebreak(d, item["headline"], x1 - x0 - 16, title_font)
    ty = y0 + image_h + (22 if lead else 15)
    row_gap = headline_size + 2 if lead else 13
    visible_rows = min(len(text_rows), 3 if lead else 4)
    if visible_rows < len(text_rows) and visible_rows:
        text_rows[visible_rows - 1] = text_rows[visible_rows - 1].rstrip(".,;: ") + "…"
    for row, text in enumerate(text_rows[:visible_rows]):
        label(d, (x0 + 8, ty + row * row_gap), text, headline_size, D, "serif")
    source_y = y1 - 15
    if main_lead and item.get("dek"):
        dy = ty + visible_rows * row_gap + 3
        available = source_y - dy - 3
        if available > 14:
            f = ft("sans", 9)
            rows = linebreak(d, item["dek"], x1 - x0 - 18, f)
            visible = rows[:min(2, available // 12)]
            if len(rows) > len(visible) and visible:
                visible[-1] = visible[-1].rstrip(".,;: ") + "…"
            for row, text in enumerate(visible):
                label(d, (x0 + 8, dy + row * 12), text, 9, G)
    label(d, (x0 + 8, source_y), f"{item['id']:02}  /  {item['source'].upper()}", 7, "#476C59", "bold")
    rule(d, y0 + image_h, x0 + 8, x1 - 8)


def draw_locator(d: ImageDraw.ImageDraw) -> None:
    shapes = [
        ([(62,741),(76,715),(99,707),(121,722),(113,745),(128,754),(116,770),(99,758),(89,787),(76,811),(64,802),(72,773),(60,758)],0),
        ([(118,807),(141,801),(152,816),(144,842),(132,870),(123,858),(127,835),(114,821)],1),
        ([(165,719),(187,710),(202,718),(196,731),(179,735),(167,729)],2),
        ([(186,752),(211,741),(229,747),(234,760),(221,770),(219,792),(205,813),(193,807),(184,785),(174,768)],3),
        ([(215,712),(244,705),(272,717),(272,731),(249,736),(233,726),(219,730)],4),
        ([(270,786),(285,784),(290,797),(277,803)],4),
        ([(270,740),(296,731),(322,742),(329,758),(317,773),(301,764),(289,750),(276,754)],4),
        ([(301,784),(324,776),(342,791),(338,808),(320,813),(304,804)],5),
        ([(105,693),(117,685),(125,691),(119,699)],4),
    ]
    def map_y(y: int) -> int:
        return int(800 + (y - 685) * 0.70)

    for points, shade in shapes:
        d.polygon([(x, map_y(y)) for x, y in points], fill=PALETTE[shade], outline=P)
    for x, y, i in [(82,745,0),(132,824,1),(185,722,2),(207,772,3),(264,741,4),(318,795,5)]:
        cy = map_y(y)
        d.ellipse((x-4,cy-4,x+4,cy+4), fill="#FFFDF7", outline=PALETTE[i], width=2)


def build() -> Image.Image:
    issue = json.loads((ROOT / "story-data.json").read_text(encoding="utf-8"))
    stories = issue["stories"]
    if len(stories) != 40 or [s["id"] for s in stories] != list(range(1, 41)):
        raise ValueError("The edition requires 40 distinct stories in a consecutive index.")
    if {s["continent"] for s in stories} != set(REGIONS):
        raise ValueError("All six inhabited continents must be represented.")
    im = Image.new("RGB", (W, H), P)
    d = ImageDraw.Draw(im)
    label(d, (35, 21), "THE WORLD IN ONE DAY", 13, RED, "bold")
    label(d, (483, 25), "THURSDAY EDITION   /   40 STORIES   /   SIX CONTINENTS", 10, G, "bold")
    rule(d, 46, color=D, thickness=2)
    label(d, (34, 50), "WORLD", 45, D, "serif")
    label(d, (220, 61), "IN FOCUS", 17, RED, "bold")
    label(d, (462, 54), "19 NOVEMBER 2026", 32, D, "serif")
    label(d, (860, 62), "THURSDAY", 12, RED, "bold")
    label(d, (37, 103), "ONE DAY. SIX CONTINENTS. FORTY STORIES, BRIEFLY.", 10, G, "bold")
    totals = Counter(x["continent"] for x in stories)
    d.rounded_rectangle((32, 128, 992, 157), radius=3, fill=D)
    px = 43
    for i, region in enumerate(REGIONS):
        label(d, (px, 137), f"{region.upper()}  {totals[region]:02}", 9, "#FFFDF7", "bold")
        px += 130 if len(region) > 10 else 110
        if i < 5:
            d.ellipse((px-12, 141, px-7, 146), fill=PALETTE[i])
    leads = [s for s in stories if s.get("lead")]
    x, top = 32, 173
    for width, item in zip((470, 230, 228), leads, strict=True):
        draw_card(d, item, (x, top, x + width, top + 273), item["id"] - 1, True)
        x += width + 16
    small = stories[3:15]
    gap, cell_w, cell_h = 12, 150, 143
    for i, item in enumerate(small):
        row, col = divmod(i, 6)
        x, y = 32 + col * (cell_w + gap), 458 + row * (cell_h + 12)
        draw_card(d, item, (x, y, x + cell_w, y + cell_h), item["id"] - 1)
    # Arrange six cards across each of two lower rows; illustrations stay within their image band.
    rule(d, 767)
    label(d, (39, 778), "ALSO ON THURSDAY  ·  25 MORE STORIES", 10, RED, "bold")
    source_labels = {
        "Associated Press": "AP", "Democracy Now!": "Democracy Now",
        "Philippine Daily Inquirer": "Inquirer", "The Guardian": "Guardian",
        "Presidency of Brazil": "Brazil Gov.", "AllAfrica": "AllAfrica",
        "MercoPress": "MercoPress", "Reuters": "Reuters",
        "Arab News": "Arab News", "RNZ": "RNZ",
    }
    for i, item in enumerate(stories[15:]):
        col, row = divmod(i, 13)
        x, y = (40, 520)[col], 805 + row * 13
        color = PALETTE[REGIONS.index(item["continent"])]
        place = item["place"].split("·")[0].split("/")[0].strip()
        source = source_labels.get(item["source"], item["source"])
        prefix, suffix = f"{place.upper()}  ·  ", f"  [{source}]"
        title = item["headline"]
        available = 444
        f = ft("sans", 9)
        while title and d.textbbox((0, 0), prefix + title + suffix, font=f)[2] > available:
            title = title.rsplit(" ", 1)[0] if " " in title else title[:-1]
        clipped = title != item["headline"]
        label(d, (x, y), f"{item['id']:02}", 9, color, "bold")
        label(d, (x + 20, y), prefix + title + ("…" if clipped else "") + suffix, 9, D)
    rule(d, 977, color=D)
    label(d,(39,986),"40 STORIES  ·  ORIGINAL VECTOR EDITORIAL ART  ·  19 NOVEMBER 2026",8,G,"bold")
    return im


if __name__ == "__main__":
    out = build()
    out.save(ROOT / "entry.png", format="PNG", optimize=True, compress_level=9)
    print(f"Rendered {out.width}x{out.height} artwork: {(ROOT / 'entry.png').stat().st_size} bytes")
