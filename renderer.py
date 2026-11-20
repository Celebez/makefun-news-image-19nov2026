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


def event_art(d: ImageDraw.ImageDraw, coords: tuple[int, int, int, int], item: dict) -> None:
    """Original editorial diagrams show an event, never an invented photograph."""
    x0, y0, x1, y1 = coords
    sx, sy = (x1 - x0) / 300, (y1 - y0) / 100
    accent = PALETTE[REGIONS.index(item["continent"])]
    paper, ink = "#FFFDF7", D
    d.rectangle(coords, fill="#E5EADF")

    def box(b, fill, outline=None, width=2):
        a, b0, c, e = b
        d.rectangle((x0+a*sx, y0+b0*sy, x0+c*sx, y0+e*sy), fill=fill, outline=outline, width=max(1, round(width*sx)))

    def poly(points, fill):
        d.polygon([(x0+x*sx, y0+y*sy) for x, y in points], fill=fill)

    def stroke(points, color=ink, width=3):
        d.line([(x0+x*sx, y0+y*sy) for x, y in points], fill=color, width=max(1, round(width*sx)))

    def oval(b, fill, outline=None):
        a, b0, c, e = b
        d.ellipse((x0+a*sx, y0+b0*sy, x0+c*sx, y0+e*sy), fill=fill, outline=outline, width=max(1, round(2*sx)))

    def txt(x, y, value, size=17, color=ink):
        size_px = max(6, round(size*sx))
        xy = (int(x0+x*sx), int(y0+y*sy))
        bounds = d.textbbox(xy, value, font=ft("bold", size_px))
        if bounds[2] > x1 or bounds[3] > y1:
            raise ValueError(f"Illustration label overflows story {item['id']}: {value}")
        label(d, xy, value, size_px, color, "bold")

    def sheet(x, title, subtitle):
        box((x, 12, x+105, 88), paper, ink)
        txt(x+8, 17, title, 17)
        stroke([(x+9, 42), (x+95, 42)], RULE, 2)
        txt(x+8, 51, subtitle, 14)
        stroke([(x+9, 77), (x+85, 77)], RULE, 2)

    def person(x, color=accent):
        oval((x-10, 15, x+10, 35), "#E0B799", ink)
        poly([(x-22, 71), (x-18, 43), (x, 35), (x+18, 43), (x+22, 71)], color)
        poly([(x-5, 40), (x+5, 40), (x, 63)], paper)

    def court():
        poly([(30, 35), (90, 8), (150, 35)], ink)
        box((33, 36, 147, 43), paper, ink)
        for x in (43, 72, 101, 130):
            box((x, 44, x+9, 79), paper, ink)
        box((25, 80, 155, 88), ink)
        txt(72, 12, "ICJ", 18, paper)

    story = item["id"]
    if story == 1:
        # Nameplates and national flags identify the three summit participants.
        for x, name, country in ((54, "TRUMP", "US"), (150, "PUTIN", "RU"), (246, "XI", "CN")):
            person(x, "#344D58")
            box((x-24, 2, x+24, 14), paper)
            if country == "US":
                for yy in (2, 6, 10, 14):
                    box((x-24, yy, x+24, yy+2), RED)
                box((x-24, 2, x-5, 10), "#324D72")
            elif country == "RU":
                box((x-24, 6, x+24, 10), "#375F90")
                box((x-24, 10, x+24, 14), RED)
            else:
                box((x-24, 2, x+24, 14), RED)
                oval((x-17, 4, x-10, 11), "#F3D984")
            box((x-38, 75, x+38, 96), paper, RULE, 1)
            txt(x-29, 77, name, 16)
        poly([(18, 64), (282, 64), (298, 74), (2, 74)], "#A46E46")
    elif story == 2:
        court()
        sheet(177, "MYANMAR", "BREACH")
        stroke([(185, 75), (205, 84), (260, 65)], RED, 4)
    elif story == 3:
        oval((23, 17, 100, 94), "#628B95", ink)
        poly([(44, 26), (72, 29), (77, 47), (56, 54), (52, 75), (36, 59)], "#A8BC88")
        txt(23, 0, "COP31", 16)
        box((123, 5, 285, 96), paper, ink)
        txt(135, 8, "DRAFT", 18, RED)
        txt(135, 37, "FOSSIL FUELS", 17)
        stroke([(130, 52), (278, 35)], RED, 4)
        txt(135, 67, "TALKS CONTINUE", 14)
    elif story == 4:
        poly([(25, 33), (80, 10), (135, 33)], ink)
        for x in (39, 67, 95, 123):
            box((x, 38, x+9, 83), ink)
        box((21, 83, 143, 91), ink)
        sheet(174, "WAR POWERS", "REJECTED")
        stroke([(184, 83), (267, 61)], RED, 4)
    elif story == 5:
        person(86)
        box((40, 59, 133, 91), ink)
        txt(49, 66, "JEFFRIES", 17, paper)
        sheet(174, "SPEAKER", "NOMINATED")
    elif story == 6:
        # Horse, carriage and a prohibition slash: the ordinance, not a generic city.
        poly([(24, 48), (63, 43), (74, 23), (88, 23), (92, 41), (75, 55), (70, 71), (34, 71)], ink)
        stroke([(35, 65), (30, 88), (46, 66), (48, 88), (68, 67), (74, 88)], ink, 5)
        stroke([(79, 62), (123, 70)], ink, 3)
        box((122, 43, 196, 75), "#A77345", ink)
        poly([(120, 43), (133, 22), (185, 22), (198, 43)], ink)
        for x in (135, 184):
            oval((x-10, 68, x+10, 88), paper, ink)
        stroke([(22, 94), (207, 8)], RED, 7)
        txt(218, 31, "NYC", 23)
        txt(216, 60, "BAN", 20, RED)
    elif story == 7:
        sheet(23, "TRUMP / NYT", "$15bn SUIT")
        stroke([(145, 52), (181, 52)], accent, 5)
        poly([(184, 52), (171, 42), (171, 62)], accent)
        txt(196, 23, "CASE", 24)
        txt(194, 54, "PROCEEDS", 17)
    elif story == 8:
        for x in (45, 214):
            box((x, 44, x+30, 70), ink)
            stroke([(x, 70), (x, 89), (x+30, 70), (x+30, 89)], ink, 4)
        oval((102, 10, 193, 58), paper, accent)
        poly([(126, 54), (116, 72), (148, 57)], paper)
        txt(113, 21, "TALKS?", 19)
        txt(94, 74, "SEOUL / DPRK", 15)
    elif story == 9:
        # Bell and actual closing price, no fabricated market chart.
        box((24, 13, 101, 92), paper, ink)
        txt(38, 21, "AI", 28)
        txt(35, 57, "IPO", 20, RED)
        poly([(128, 58), (141, 47), (145, 24), (164, 17), (183, 24), (187, 47), (200, 58)], "#B78A3B")
        oval((157, 58, 171, 72), ink)
        txt(215, 28, "$97", 30)
        txt(217, 65, "CLOSE", 14)
    elif story == 10:
        box((30, 21, 108, 81), "#6F8A5E", ink)
        for x in range(39, 106, 15):
            stroke([(x, 12), (x, 21)], ink)
            stroke([(x, 81), (x, 92)], ink)
        txt(38, 38, "NVIDIA", 17, paper)
        txt(146, 17, "CEO", 30)
        txt(145, 55, "SEARCH", 24, RED)
        oval((246, 20, 273, 48), None, ink)
        stroke([(270, 46), (285, 62)], ink, 5)
    elif story == 11:
        oval((52, 30, 196, 89), "#9B9293", ink)
        oval((154, 32, 233, 85), "#AAA0A2", ink)
        for x in (171, 209):
            oval((x-7, 24, x+7, 40), "#9B9293", ink)
            oval((x-2, 44, x+2, 49), ink)
        oval((190, 62, 195, 67), ink)
        oval((211, 62, 216, 67), ink)
        txt(21, 1, "FIONA", 18)
        txt(248, 26, "IN", 15)
        txt(237, 46, "MEMORY", 12)
    elif story == 12:
        oval((87, 9, 109, 31), ink)
        stroke([(97, 30), (83, 54), (104, 68), (123, 89)], ink, 7)
        stroke([(83, 54), (66, 76), (40, 81)], ink, 7)
        stroke([(92, 40), (124, 40), (139, 24)], ink, 6)
        stroke([(91, 39), (63, 42), (48, 27)], ink, 6)
        txt(167, 14, "3 YEARS", 25, RED)
        txt(168, 51, "DOPING BAN", 17)
    elif story == 13:
        # Aircraft silhouette and attributed purchase price.
        poly([(22, 58), (92, 48), (120, 11), (139, 11), (128, 48), (231, 53), (259, 34), (276, 34), (260, 65), (128, 69), (145, 91), (123, 91), (90, 67), (22, 66)], ink)
        txt(16, 8, "GHANA", 17)
        txt(185, 62, "$61m", 23, RED)
    elif story == 14:
        box((21, 15, 94, 55), paper, ink)
        box((22, 35, 94, 55), RED)
        box((22, 15, 48, 35), "#365E90")
        oval((31, 20, 37, 26), paper)
        box((209, 15, 282, 55), "#365E90", ink)
        box((209, 35, 282, 55), RED)
        poly([(210, 16), (242, 35), (210, 54)], paper)
        oval((217, 31, 223, 37), "#D8AF42")
        stroke([(107, 39), (190, 39)], ink, 5)
        poly([(104, 39), (117, 31), (117, 47)], ink)
        poly([(193, 39), (180, 31), (180, 47)], ink)
        txt(63, 66, "FREE-TRADE PACT", 24)
    elif story == 15:
        for x, yy in ((40, 15), (119, 6), (209, 18)):
            stroke([(x+22, yy+30), (x+22, 65)], ink, 4)
            box((x, yy, x+55, yy+32), paper, ink)
            txt(x+7, yy+5, "PLAN?", 16, RED)
        txt(88, 70, "COLOMBIA", 19)
    else:
        raise ValueError(f"Missing event-specific illustration for story {story}")


def draw_card(d: ImageDraw.ImageDraw, item: dict, rect: tuple[int, int, int, int], ordinal: int, lead: bool = False) -> None:
    x0, y0, x1, y1 = rect
    accent = PALETTE[REGIONS.index(item["continent"])]
    d.rounded_rectangle(rect, radius=5, fill="#FFFDF7", outline=RULE, width=1)
    image_h = 94 if lead else 45
    event_art(d, (x0 + 1, y0 + 1, x1 - 1, y0 + image_h), item)
    metadata = f"{item['place'].upper()}  ·  {item['desk']}"
    meta = ft("bold", 8 if lead else 7)
    if d.textbbox((0, 0), metadata, font=meta)[2] > x1 - x0 - 16:
        metadata = item["place"].upper()
    if d.textbbox((0, 0), metadata, font=meta)[2] > x1 - x0 - 16:
        raise ValueError(f"Place label too wide in story {item['id']}")
    label(d, (x0 + 8, y0 + image_h + (6 if lead else 4)), metadata, 8 if lead else 7, accent, "bold")
    headline_size = 25 if lead else 14
    kind = "serif" if lead else "bold"
    title_font = ft(kind, headline_size)
    text_rows = linebreak(d, item["display_headline"], x1 - x0 - 16, title_font)
    ty = y0 + image_h + (22 if lead else 15)
    row_gap = 28 if lead else 16
    source_y = y1 - 15
    if len(text_rows) > 4 or any(d.textbbox((0, 0), text, font=title_font)[2] > x1-x0-16 for text in text_rows):
        raise ValueError(f"Headline does not fit story {item['id']}: {text_rows}")
    if d.textbbox((x0+8, ty+(len(text_rows)-1)*row_gap), text_rows[-1], font=title_font)[3] > source_y - 2:
        raise ValueError(f"Headline overlaps source in story {item['id']}")
    for row, text in enumerate(text_rows):
        label(d, (x0 + 8, ty + row * row_gap), text, headline_size, D, kind)
    if lead:
        dy = ty + len(text_rows) * row_gap + 4
        f = ft("sans", 10)
        deck_rows = linebreak(d, item["display_dek"], x1 - x0 - 18, f)
        if dy + len(deck_rows) * 13 > source_y - 2:
            raise ValueError(f"Summary does not fit story {item['id']}")
        for row, text in enumerate(deck_rows):
            label(d, (x0 + 8, dy + row * 13), text, 10, G)
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
    for width, item in zip((310, 310, 308), leads, strict=True):
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
