#!/usr/bin/env python3
"""Render the Fervent Sphere front page for 25 November 2026.

Draws a dense newspaper front page (1024x1024, <=1 MiB PNG) with the
superskie winner template: masthead, UTC strip, numbers strip, 3 lead
stories, 10 secondary stories, world map, numbered briefs, date check.
Every number was verified against a primary source on 25 Nov 2026.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 240, 221)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
SEA = (199, 220, 230)
LAND = (216, 196, 154)
LAND_EDGE = (150, 128, 90)
TAG_COLORS = {
    "CONFIRMED": (30, 125, 50),
    "OFFICIALS": (21, 101, 192),
    "REPORTED": (141, 110, 0),
    "FORECAST": (106, 27, 154),
}
FD = "/usr/share/fonts/truetype/dejavu/"

def font(name, size):
    return ImageFont.truetype(FD + name, size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Bold.ttf", s)  # no italic file on this VM
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_line(draw, text, fnt, max_w):
    """Shorten with ellipsis until it fits max_w."""
    if fnt.getlength(text) <= max_w:
        return text
    while len(text) > 4 and fnt.getlength(text + "...") > max_w:
        text = text[:-1]
    return text + "..."

# ---------------------------------------------------------------- data
LEADS = [
    {
        "kicker": "UKRAINE  ·  BALTIC & LIBYA",
        "headline": "ZELENSKIY: UKRAINE SANK THE SHIPS",
        "summary": "Kyiv confirms drone strikes on a Russian cargo ship in the Gulf of Finland and a warship off Benghazi. Moscow calls it \u201cterrorism\u201d; Norway urges caution.",
        "tag": "CONFIRMED",
        "source": "REUTERS",
        "art": "ship",
        "color": (31, 78, 121),
    },
    {
        "kicker": "MARKETS  ·  NEW YORK",
        "headline": "DOW TOPS 50,000 AS THE AI RALLY CRACKS",
        "summary": "The Dow closes above 50,000 for the first time (+0.85% to 50,018.70) as the Nasdaq sinks 1.48%. Nvidia \u22125.9%; Anthropic below $83.",
        "tag": "CONFIRMED",
        "source": "REUTERS",
        "art": "chart",
        "color": (30, 125, 50),
    },
    {
        "kicker": "CLIMATE  ·  ANTALYA",
        "headline": "COP31 COLLAPSES \u2014 NO DEAL ON FOSSIL FUELS",
        "summary": "The UN climate summit ends with no final agreement as oil and gas producers block phaseout language, leaving vulnerable nations waiting on finance.",
        "tag": "REPORTED",
        "source": "MULTIPLE OUTLETS",
        "art": "globe",
        "color": (163, 22, 33),
    },
]

SECONDARY = [
    ("TECH · EARNINGS", "Dell beats big on AI servers",
     "EPS $9.45 vs $6.59; revenue $54.94bn; AI backlog $132.3bn.",
     "CONFIRMED", "COMPANY", "D", (21, 101, 192)),
    ("MIDDLE EAST · RIYADH", "Houthi drone hits Riyadh\u2019s tallest tower",
     "11 wounded in Riyadh tower strike; Houthis 60 km from Aden.",
     "OFFICIALS", "SAUDI CIVIL DEFENSE", "H", (163, 22, 33)),
    ("WAR · UKRAINE", "700,000 Russian soldiers killed, analysis finds",
     "New analysis: 700,000+ Russian dead; Moscow\u2019s own count ~500,000.",
     "REPORTED", "RFE/RL", "7", (90, 60, 30)),
    ("COURTS · NEW YORK", "Huawei guilty of stealing trade secrets",
     "Brooklyn jury convicts on trade secrets; acquits on racketeering.",
     "CONFIRMED", "REUTERS", "H", (31, 78, 121)),
    ("US · INTELLIGENCE", "CIA and spy chief\u2019s office breached",
     "Hackers hit CIA and ODNI; some unclassified data compromised.",
     "REPORTED", "REUTERS", "C", (80, 80, 80)),
    ("WAR · KYIV", "11 killed in strike on Kyiv apartment block",
     "Rescuers pull bodies from rubble of a Kyiv-region apartment block.",
     "OFFICIALS", "UKRAINE", "K", (90, 60, 30)),
    ("MIDDLE EAST · GAZA", "Gaza death toll reaches 74,746",
     "74,746 dead; Oxfam: pollution risks cover 99% of the strip.",
     "REPORTED", "WAFA / OXFAM", "G", (163, 22, 33)),
    ("SPORT · EUROPE", "Nine Champions League ties tonight",
     "Atl\u00e9tico\u2013Viking, Sporting\u2013Man Utd, PSG\u2013Roma headline Matchday 5.",
     "OFFICIALS", "UEFA", "U", (30, 125, 50)),
    ("TRADE · WASHINGTON", "US readies new tariffs on trading partners",
     "Washington readies fresh tariff announcements, BBC understands.",
     "REPORTED", "BBC", "T", (21, 101, 192)),
    ("US · WASHINGTON", "Trump gives Giuliani the Medal of Freedom",
     "Ex-mayor and Trump adviser gets top civilian honour.",
     "CONFIRMED", "AP", "M", (120, 60, 120)),
]

BRIEFS = [
    "Sarkozy corruption case ordered to trial; pre-trial hearing 1 Apr 2027. (REUTERS)",
    "Fort Hood shooter Hasan seeks stay of execution set for next week. (COURT RECORDS)",
    "US envoy \u2018not certain\u2019 Israel military aid ends this year as Trump promised. (REUTERS)",
    "Trump pardons Thanksgiving turkeys Freedom and Feathers. (AP)",
    "Nikkei falls as much as 2.9% as Asia follows Wall Street\u2019s tech slide. (REUTERS)",
    "Bitcoin slips below $60,000 to $59,099. (BINANCE)",
    "Core PCE and Q3 GDP due 13:30 UTC; consensus core PCE +3.4% a year. (FORECAST)",
    "US markets shut Thursday for Thanksgiving; early close Friday. (NYSE)",
    "Analog Devices \u221217.4%, HPE \u221216.3%, chip index SOXX \u22128.3%. (MARKET DATA)",
    "Huang to testify to Senate on 3 Dec; Warren demands board explain itself. (REUTERS)",
    "Kushner: Trump may weigh NATO-like guarantees for Ukraine. (RFE/RL)",
    "Iran to ration electricity from 22 Nov as winter gas crunch looms. (RFE/RL)",
    "266m people face acute food insecurity, says the World Food Programme. (WFP)",
    "Venezuela reports total public debt of $237.5bn. (OFFICIAL)",
    "India\u2019s food inflation rises again; vegetables dearer. (BBC)",
    "UK disability benefit PIP \u2018not fit for purpose\u2019, review finds. (BBC)",
    "UK nuclear-test veterans promised \u2018full truth\u2019 in independent panel. (BBC)",
    "Spain heads to election; huge socialist rally fills Barcelona. (REPORTED)",
    "Pentagon sharply criticises Canada over military modernisation. (REPORTED)",
    "California king tides could be biggest in four decades. (REPORTED)",
    "Man Utd\u2019s Yoro has Anfield red card overturned. (BBC)",
    "Land-mine casualties soar in Syria, two years after the war. (BBC)",
    "Silver \u22125.2%, gold \u22122.1% as Fed hike bets bite. (MARKET DATA)",
    "Australian court approves a2 Milk\u2019s A$62m class-action settlement. (REUTERS)",
]

UTC_SLOTS = [
    ("00:30", "Zelenskiy confirms the ship strikes"),
    ("01:00", "700,000 Russian dead: new analysis"),
    ("02:00", "Dell beats: EPS $9.45, backlog $132.3bn"),
    ("03:30", "Nikkei slides 2.9% in Asian trade"),
    ("13:30", "Core PCE + Q3 GDP due before US open"),
    ("17:45", "UCL: Sabah\u2013Bar\u00e7a, Slavia\u2013Villarreal KO"),
    ("20:00", "Atl\u00e9tico\u2013Viking headlines nine UCL ties"),
]

NUMBERS = [
    ("50,018.70", "Dow\u2019s first close above 50,000"),
    ("700,000+", "Russian soldiers killed in Ukraine"),
    ("$132.3bn", "Dell\u2019s AI server backlog"),
    ("74,746", "Gaza death toll (WAFA)"),
    ("266m", "in acute food insecurity (WFP)"),
    ("$59,099", "Bitcoin, below $60,000"),
]

DATE_CHECK_LEFT = ("LEFT OUT \u2014 Nvidia\u2019s +31.5% Monday surge and Huang\u2019s "
    "reinstatement (23 Nov) are yesterday\u2019s news. Anthropic\u2019s $81.3bn IPO "
    "(last Thu) is the listing, not today\u2019s slide below $83.")
DATE_CHECK_NOTYET = ("NOT YET \u2014 Core PCE + Q3 GDP (13:30 UTC) land after press time. "
    "All nine Champions League results \u2014 ties kick off 17:45 UTC. Thanksgiving "
    "shuts US markets on Thursday.")
KICKER = ("The Dow closed above 50,000 for the first time \u2014 on the very day "
    "the AI rally that carried it there began to fall apart.")
SOURCES_LINE = ("Sources: Reuters, AP, BBC, RFE/RL, UEFA, WFP, WAFA, Oxfam, company "
    "filings, market data via Binance. All figures checked 25 Nov 2026, 02:30 UTC.")

# Rough continent outlines (lon, lat) for the stylised map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-75, 35), (-80, 25),
     (-90, 20), (-97, 16), (-105, 20), (-117, 33), (-125, 40), (-140, 60),
     (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-68, -52), (-72, -40), (-72, -20), (-80, -5),
     (-82, 5)],
    [(-10, 36), (-9, 43), (0, 46), (-2, 50), (5, 53), (8, 57), (18, 56),
     (21, 60), (30, 70), (40, 68), (45, 60), (40, 50), (28, 45), (23, 40),
     (19, 42), (12, 44), (3, 43), (-2, 37)],
    [(-6, 35), (10, 37), (20, 32), (32, 31), (43, 12), (51, 11), (48, 0),
     (40, -15), (35, -25), (28, -33), (18, -35), (12, -18), (9, 4),
     (-8, 5), (-17, 15), (-16, 25)],
    [(40, 68), (60, 70), (75, 73), (100, 77), (130, 72), (160, 70),
     (178, 65), (170, 60), (160, 55), (140, 45), (130, 38), (127, 35),
     (120, 30), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22),
     (80, 15), (75, 8), (70, 20), (60, 25), (55, 26), (50, 30), (45, 30),
     (40, 36)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
]
# (num, lon, lat, name, display dlon, display dlat) — display offsets
# keep clustered pins readable; a leader line joins each pin to its true spot.
PINS = [
    (1, 28, 60, "Gulf of Finland", 0, 4),
    (2, 20, 32, "Benghazi", -6, -4),
    (3, 30.5, 50.5, "Kyiv", 8, 6),
    (4, 30.7, 36.9, "Antalya", 8, -6),
    (5, 46.7, 24.6, "Riyadh", 6, 6),
    (6, 45, 12.8, "Aden", -6, -6),
    (7, 34.5, 31.5, "Gaza", 10, -8),
    (8, -74, 40.7, "New York", 6, 6),
    (9, -77, 38.9, "Washington", -6, -6),
    (10, 2.35, 48.85, "Paris", 8, 8),
    (11, -0.1, 51.5, "London", -8, 8),
    (12, -3.7, 40.4, "Madrid", -8, -6),
    (13, 145, -37.8, "Melbourne", 0, 0),
]


# ---------------------------------------------------------------- drawing
def section_bar(d, x, y, w, text):
    d.rectangle([x, y, x + w, y + 16], fill=INK)
    d.text((x + 8, y + 3), text, font=SANS_B(11), fill=(255, 255, 255))

def draw_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 70, 110))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(24, 52, 84))
    d.polygon([(x + 18, y + h - 26), (x + 60, y + h - 26), (x + 52, y + h - 46),
               (x + 26, y + h - 46)], fill=(90, 90, 90))
    d.rectangle([x + 34, y + h - 62, x + 44, y + h - 46], fill=(60, 60, 60))
    d.rectangle([x + 70, y + h - 40, x + 76, y + h - 26], fill=(60, 60, 60))
    cx, cy = x + w - 42, y + 26
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 20, 8
        a = math.radians(ang)
        d.line([cx, cy, cx + r1 * math.cos(a), cy + r1 * math.sin(a)],
               fill=(255, 180, 40), width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 60))
    d.ellipse([x + 96, y + h - 14, x + 104, y + h - 6], fill=(255, 255, 255))
    d.ellipse([x + 150, y + h - 18, x + 156, y + h - 12], fill=(255, 255, 255))

def draw_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 40, 26))
    bars = [14, 22, 30, 38, 46, 54, 62, 70, 58, 40]
    bw, gap = 24, 7
    bx = x + 18
    for i, v in enumerate(bars):
        top = y + h - 12 - v
        col = (46, 160, 90) if i < 8 else (200, 60, 50)
        d.rectangle([bx, top, bx + bw, y + h - 12], fill=col)
        bx += bw + gap
    d.line([x + 10, y + 16, x + w - 10, y + 16], fill=(255, 210, 90),
           width=2)
    d.text((x + 12, y + 20), "50,000", font=SANS_B(13), fill=(255, 210, 90))

def draw_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 40, 30))
    cx, cy, r = x + w // 2 - 30, y + h // 2, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 140, 180))
    d.ellipse([cx - 18, cy - 22, cx - 2, cy - 6], fill=(70, 160, 90))
    d.ellipse([cx + 4, cy + 6, cx + 22, cy + 22], fill=(70, 160, 90))
    d.ellipse([cx - 6, cy - 2, cx + 8, cy + 10], fill=(70, 160, 90))
    d.line([cx - 20, cy - 26, cx - 6, cy - 8, cx - 16, cy + 8, cx + 2, cy + 24],
           fill=(255, 255, 255), width=3)
    fx = x + w - 62
    d.rectangle([fx, y + h - 34, fx + 12, y + h - 12], fill=(40, 40, 40))
    d.rectangle([fx + 18, y + h - 28, fx + 28, y + h - 12], fill=(40, 40, 40))
    d.ellipse([fx + 2, y + 12, fx + 12, y + 22], fill=(180, 180, 180))
    d.ellipse([fx + 16, y + 18, fx + 24, y + 26], fill=(180, 180, 180))
    d.text((x + w - 58, y + h - 12), "NO DEAL", font=SANS_B(11),
           fill=(255, 120, 110))

ART = {"ship": draw_ship, "chart": draw_chart, "globe": draw_globe}

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=RED)
    # Masthead
    title = "FERVENT SPHERE"
    tf = SERIF_B(52)
    d.text(((W - tf.getlength(title)) / 2, 12), title, font=tf, fill=INK)
    d.rectangle([22, 84, W - 22, 86], fill=RED)
    sub = "WEDNESDAY  25  NOVEMBER  2026    ·    37 STORIES  ·  6 CONTINENTS  ·  10 FIELDS"
    sf = SANS_B(14)
    d.text(((W - sf.getlength(sub)) / 2, 92), sub, font=sf, fill=INK)
    # UTC strip
    y = 116
    section_bar(d, 22, y, W - 44, "THE DAY IN UTC")
    y += 22
    col_w = (W - 44) / 7
    for i, (t, txt) in enumerate(UTC_SLOTS):
        cx = 22 + i * col_w
        d.text((cx + 4, y), t, font=SANS_B(12), fill=RED)
        for j, ln in enumerate(wrap(txt, SANS(10), col_w - 10)):
            d.text((cx + 4, y + 15 + j * 12), ln, font=SANS(10), fill=INK)
        if i:
            d.line([cx, y, cx, y + 40], fill=(200, 190, 160))
    # Numbers strip
    y = 178
    section_bar(d, 22, y, W - 44, "THE DAY IN NUMBERS")
    y += 22
    col_w = (W - 44) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 22 + i * col_w
        nf = SANS_B(17)
        d.text((cx + 4, y), num, font=nf, fill=RED)
        for j, ln in enumerate(wrap(lab, SANS(9), col_w - 10)):
            d.text((cx + 4, y + 22 + j * 11), ln, font=SANS(9), fill=INK)
        if i:
            d.line([cx, y, cx, y + 42], fill=(200, 190, 160))
    # Leads
    y = 244
    col_w, gap = 322, 12
    for i, lead in enumerate(LEADS):
        x = 22 + i * (col_w + gap)
        ART[lead["art"]](d, x, y, col_w, 64)
        d.text((x, y + 70), lead["kicker"], font=SANS_B(11), fill=RED)
        hy = y + 86
        for ln in wrap(lead["headline"], SERIF_B(19), col_w):
            d.text((x, hy), ln, font=SERIF_B(19), fill=INK)
            hy += 23
        sy = hy + 4
        for ln in wrap(lead["summary"], SANS(12), col_w):
            d.text((x, sy), ln, font=SANS(12), fill=(40, 40, 40))
            sy += 15
        tag = lead["tag"] + "  ·  " + lead["source"]
        ty = sy + 2
        d.rectangle([x, ty, x + 6 + SANS_B(10).getlength(tag), ty + 14],
                    fill=TAG_COLORS[lead["tag"]])
        d.text((x + 3, ty + 2), tag, font=SANS_B(10), fill=(255, 255, 255))
    d.line([22, 448, W - 22, 448], fill=INK, width=2)

    # Secondary stories: 2 columns x 5 rows
    y = 456
    for idx, (kick, head, summ, tag, src, letter, col) in enumerate(SECONDARY):
        cx = 22 + (idx % 2) * 500
        ry = y + (idx // 2) * 39
        d.rectangle([cx, ry, cx + 30, ry + 30], fill=col)
        lf = SANS_B(16)
        d.text((cx + (30 - lf.getlength(letter)) / 2, ry + 6), letter,
               font=lf, fill=(255, 255, 255))
        tx = cx + 38
        d.text((tx, ry), kick, font=SANS_B(9), fill=RED)
        hf = SANS_B(13)
        head_txt = fit_line(d, head, hf, 452 - hf.getlength(" · " + tag) - 8)
        d.text((tx, ry + 12), head_txt, font=hf, fill=INK)
        tw = hf.getlength(head_txt)
        d.text((tx + tw, ry + 12), " · " + tag, font=hf,
               fill=TAG_COLORS[tag])
        summ_txt = fit_line(d, summ, SANS(11), 452)
        d.text((tx, ry + 27), summ_txt, font=SANS(11), fill=(60, 60, 60))
    # World map
    y = 658
    section_bar(d, 22, y, W - 44, "WHERE IT HAPPENED")
    mx, my, mw, mh = 22, 680, 638, 92

    def proj(lon, lat):
        return (mx + (lon + 170) / 360 * mw, my + (75 - lat) / 130 * mh)

    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_EDGE)
    for num, lon, lat, _name, dx, dy in PINS:
        px, py = proj(lon, lat)
        qx, qy = proj(lon + dx, lat + dy)
        if dx or dy:
            d.line([px, py, qx, qy], fill=(110, 110, 110), width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        nf = SANS_B(8 if num < 10 else 7)
        t = str(num)
        d.text((qx - nf.getlength(t) / 2, qy - 5), t, font=nf,
               fill=(255, 255, 255))
    lx = 672
    for i, (_n, _lo, _la, name, _dx, _dy) in enumerate(PINS):
        cx = lx + (i // 7) * 168
        ry = my + 2 + (i % 7) * 13
        d.text((cx, ry), f"{i + 1}. {name}", font=SANS(10), fill=INK)
    # Briefs
    y = 778
    section_bar(d, 22, y, W - 44, "ALSO ON 25 NOVEMBER")
    bf = SANS(10)
    for i, b in enumerate(BRIEFS):
        cx = 22 + (i % 2) * 500
        ry = 800 + (i // 2) * 11.5
        d.text((cx, ry), f"{i + 1:02d}", font=SANS_B(10), fill=RED)
        txt = fit_line(d, b, bf, 452)
        d.text((cx + 24, ry), txt, font=bf, fill=INK)
    # Date check footer
    y = 942
    section_bar(d, 22, y, W - 44, "DATE CHECK")
    cf = SANS(10)
    for j, ln in enumerate(wrap(DATE_CHECK_LEFT, cf, 478)):
        d.text((22, 962 + j * 12), ln, font=cf, fill=(60, 60, 60))
    for j, ln in enumerate(wrap(DATE_CHECK_NOTYET, cf, 478)):
        d.text((522, 962 + j * 12), ln, font=cf, fill=(60, 60, 60))
    kf = SERIF_I(13)
    d.text(((W - kf.getlength(KICKER)) / 2, 996), KICKER, font=kf, fill=RED)
    sf2 = SANS(8)
    d.text(((W - sf2.getlength(SOURCES_LINE)) / 2, 1013), SOURCES_LINE,
           font=sf2, fill=(120, 120, 120))
    return img

if __name__ == "__main__":
    import os
    img = render()
    out = os.environ.get("OUT", "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}, {size} bytes")
    print(f"stories: {len(LEADS)} lead + {len(SECONDARY)} secondary + "
          f"{len(BRIEFS)} briefs = {len(LEADS) + len(SECONDARY) + len(BRIEFS)}")
    assert img.size[0] <= 1024 and img.size[1] <= 1024
    assert size <= 1048576, "over 1 MiB"
