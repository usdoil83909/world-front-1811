import os
import struct
import zlib
from pathlib import Path

SS = 2
OUT_W = OUT_H = 1024
WIDTH = HEIGHT = OUT_W * SS

PAPER = (250, 248, 242)
INK = (38, 46, 60)
RED = (188, 72, 72)
TEAL = (52, 112, 112)
OCHRE = (206, 160, 72)
CREAM = (254, 253, 249)
GREY = (128, 126, 122)
DARK_GREY = (82, 80, 78)
PALE = (214, 218, 226)
WHITE = (255, 255, 255)
SHADE = (242, 240, 236)

GLYPH_W = 6
GLYPH_H = 8
ADVANCE = 6
DATE_TEXT = 'WEDNESDAY 18 NOVEMBER 2026'

FONT = {
    'A': ('.###../#...#./#...#./#####./#...#./#...#./#...#./......'),
    'B': ('####../#...#./#...#./####../#...#./#...#./####../......'),
    'C': ('.###../#...#./#...../#...../#...../#...#./.###../......'),
    'D': ('####../#...#./#...#./#...#./#...#./#...#./####../......'),
    'E': ('#####./#...../#...../####../#...../#...../#####./......'),
    'F': ('#####./#...../#...../####../#...../#...../#...../......'),
    'G': ('.###../#...#./#...../#.###./#...#./#...#./.###../......'),
    'H': ('#...#./#...#./#...#./#####./#...#./#...#./#...#./......'),
    'I': ('#####./..#.../..#.../..#.../..#.../..#.../#####./......'),
    'J': ('..###./...#../...#../...#../#..#../#..#../.##.../......'),
    'K': ('#...#./#..#../#.#.../##..../#.#.../#..#../#...#./......'),
    'L': ('#...../#...../#...../#...../#...../#...../#####./......'),
    'M': ('#...#./##.##./#.#.#./#...#./#...#./#...#./#...#./......'),
    'N': ('#...#./##..#./#.#.#./#..##./#...#./#...#./#...#./......'),
    'O': ('.###../#...#./#...#./#...#./#...#./#...#./.###../......'),
    'P': ('####../#...#./#...#./####../#...../#...../#...../......'),
    'Q': ('.###../#...#./#...#./#...#./#.#.#./#..#../.##.#./......'),
    'R': ('####../#...#./#...#./####../#.#.../#..#../#...#./......'),
    'S': ('.###../#...#./#...../.###../....#./#...#./.###../......'),
    'T': ('#####./..#.../..#.../..#.../..#.../..#.../..#.../......'),
    'U': ('#...#./#...#./#...#./#...#./#...#./#...#./.###../......'),
    'V': ('#...#./#...#./#...#./#...#./#...#./.#.#../..#.../......'),
    'W': ('#...#./#...#./#...#./#.#.#./#.#.#./##.##./#...#./......'),
    'X': ('#...#./#...#./.#.#../..#.../.#.#../#...#./#...#./......'),
    'Y': ('#...#./#...#./.#.#../..#.../..#.../..#.../..#.../......'),
    'Z': ('#####./...#../..#.../.#..../#...../#...../#####./......'),
    'a': ('....../....../.##.../..#.../.##.../#.#.../.##.../......'),
    'b': ('#...../#...../###.../#.#.../###.../#.#.../###.../......'),
    'c': ('....../....../.##.../#...../#...../#...../.##.../......'),
    'd': ('..#.../..#.../.##.../#.#.../#.#.../#.#.../.##.../......'),
    'e': ('....../....../.##.../#.#.../###.../#...../.##.../......'),
    'f': ('..#.../.#..../###.../.#..../.#..../.#..../.#..../......'),
    'g': ('....../....../.##.../#.#.../#.#.../.##.../..#.../.##...'),
    'h': ('#...../#...../###.../#.#.../#.#.../#.#.../#.#.../......'),
    'i': ('.#..../....../.#..../.#..../.#..../.#..../.#..../......'),
    'j': ('..#.../....../..#.../..#.../..#.../..#.../..#.../.##...'),
    'k': ('#...../#...../#.#.../##..../#...../##..../#.#.../......'),
    'l': ('.#..../.#..../.#..../.#..../.#..../.#..../.#..../......'),
    'm': ('....../....../##.##./#.#.#./#.#.#./#.#.#./#.#.#./......'),
    'n': ('....../....../###.../#.#.../#.#.../#.#.../#.#.../......'),
    'o': ('....../....../.##.../#.#.../#.#.../#.#.../.##.../......'),
    'p': ('....../....../###.../#.#.../#.#.../###.../#...../#.....'),
    'q': ('....../....../.##.../#.#.../#.#.../.##.../..#.../..#...'),
    'r': ('....../....../###.../#.#.../#...../#...../#...../......'),
    's': ('....../....../.##.../#...../.##.../..#.../###.../......'),
    't': ('....../.#..../###.../.#..../.#..../.#..../..#.../......'),
    'u': ('....../....../#.#.../#.#.../#.#.../#.#.../.##.../......'),
    'v': ('....../....../#.#.../#.#.../#.#.../.##.../..#.../......'),
    'w': ('....../....../#.#.#./#.#.#./#.#.#./#.#.#./.#.#../......'),
    'x': ('....../....../#.#.../.##.../..#.../.##.../#.#.../......'),
    'y': ('....../....../#.#.../#.#.../.##.../..#.../..#.../.##...'),
    'z': ('....../....../###.../..#.../.#..../#...../###.../......'),
    '0': ('.###../#...#./#..##./#.#.#./##..#./#...#./.###../......'),
    '1': ('..#.../.##.../..#.../..#.../..#.../..#.../.###../......'),
    '2': ('.###../#...#./....#./...#../..#.../.#..../#####./......'),
    '3': ('####../....#./....#./.###../....#./....#./####../......'),
    '4': ('...#../..##../.#.#../#..#../#####./...#../...#../......'),
    '5': ('#####./#...../#...../####../....#./#...#./.###../......'),
    '6': ('.###../#...../#...../####../#...#./#...#./.###../......'),
    '7': ('#####./....#./...#../..#.../..#.../..#.../..#.../......'),
    '8': ('.###../#...#./#...#./.###../#...#./#...#./.###../......'),
    '9': ('.###../#...#./#...#./.####./....#./...#../.##.../......'),
    ' ': ('....../....../....../....../....../....../....../......'),
    '.': ('....../....../....../....../....../.##.../.##.../......'),
    ',': ('....../....../....../....../....../.##.../.##.../.##...'),
    ':': ('....../....../.##.../.##.../....../.##.../.##.../......'),
    ';': ('....../....../.##.../.##.../....../.##.../.##.../.##...'),
    "'": ('.##.../.##.../....../....../....../....../....../......'),
    '-': ('....../....../....../....../####../....../....../......'),
    '%': ('#..##./#.##../..##../.##.../##..../##.#../#..##./......'),
    '$': ('..#.../.####./#.#.../.###../...#../####../..#.../......'),
    '&': ('.##.../#..#../#.#.../.#..../#.#.#./#..#../.##.#./......'),
    '/': ('....#./....#./...#../..#.../.#..../.#..../#...../......'),
    '!': ('..#.../..#.../..#.../..#.../..#.../..#.../....../..#...'),
    '?': ('.###../#..#../...#../..##../..#.../....../..#.../......'),
    '(': ('..##../.#..../.#..../.#..../.#..../.#..../..##../......'),
    ')': ('..##../...#../...#../...#../...#../...#../..##../......'),
    '+': ('....../....../..#.../#####./..#.../....../....../......'),
    '=': ('....../....../....../#####./....../#####./....../......'),
}

GLYPHS = {char: tuple(rows.split('/')) for char, rows in FONT.items()}
COMPACT_ADVANCE = {
    char: max(row.rfind('#') for row in rows) + 2 if char != ' ' else 3
    for char, rows in GLYPHS.items()
}


def glyph_corners(rows, x, y):
    """Find exposed corners so 2x text can soften its outline by one sample."""
    left = x == 0 or rows[y][x - 1] == '.'
    right = x == GLYPH_W - 1 or rows[y][x + 1] == '.'
    top = y == 0 or rows[y - 1][x] == '.'
    bottom = y == GLYPH_H - 1 or rows[y + 1][x] == '.'
    return (left and top, right and top, left and bottom, right and bottom)


GLYPH_CORNERS = {
    char: {(x, y): glyph_corners(rows, x, y)
           for y, row in enumerate(rows) for x, cell in enumerate(row) if cell == '#'}
    for char, rows in GLYPHS.items()
}


def glyph(char):
    return GLYPHS.get(char, GLYPHS[' '])


def glyph_pixels(text):
    return sum(row.count('#') for char in text for row in glyph(char))


def text_width(text, scale=1):
    return len(text) * ADVANCE * scale


def wrap_text(text, max_w, scale=1):
    lines = []
    line = ''
    for word in text.split():
        if text_width(word, scale) > max_w:
            word = ''.join(char for char in word if text_width(char, scale) <= max_w)
        if not word:
            continue
        candidate = f'{line} {word}' if line else word
        if text_width(candidate, scale) <= max_w:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or ['']


def draw_text(canvas, x, y, text, scale, colour, max_w=None, max_h=None, seen=None,
              compact=False):
    if scale < 2:
        raise ValueError('All printed text must use scale 2 or larger')
    if any(char not in GLYPHS for char in text):
        raise ValueError(f'Unsupported character in {text!r}')
    advances = [COMPACT_ADVANCE[char] if compact else ADVANCE for char in text]
    width = scale * sum(advances)
    if x < 0 or y < 0 or x + width > OUT_W or y + 8 * scale > OUT_H:
        raise ValueError(f'Text outside page: {text!r}')
    if max_w is not None and width > max_w:
        raise ValueError(f'Text exceeds column: {text!r}')
    if max_h is not None and max_h < 8 * scale:
        raise ValueError(f'Text exceeds height: {text!r}')
    if max_w is not None and max_w <= 0 or max_h is not None and max_h <= 0:
        return
    ix = x * SS
    iy = y * SS
    ibs = scale * SS
    iright = None if max_w is None else ix + max_w * SS
    ibottom = None if max_h is None else iy + max_h * SS
    gx = ix
    for char, advance in zip(text, advances):
        if iright is not None and gx >= iright:
            break
        for row_index, row in enumerate(glyph(char)):
            py = iy + row_index * ibs
            if ibottom is not None and py >= ibottom:
                break
            sy0 = py
            sy1 = py + ibs
            if ibottom is not None:
                sy1 = min(sy1, ibottom)
            if sy0 >= sy1:
                continue
            for col_index, pixel in enumerate(row):
                if pixel != '#':
                    continue
                px = gx + col_index * ibs
                sx0 = px
                sx1 = px + ibs
                if iright is not None:
                    sx1 = min(sx1, iright)
                if sx0 >= sx1:
                    continue
                if seen is not None:
                    key = (sx0, sy0)
                    if key in seen:
                        raise RuntimeError(f'glyph pixel painted twice at {key}')
                    seen.add(key)
                corners = GLYPH_CORNERS[char][col_index, row_index]
                canvas.glyph_cell(sx0, sy0, sx1 - sx0, sy1 - sy0, colour, corners)
        gx += advance * ibs


def draw_text_block(canvas, x, y, text, scale, colour, max_w, max_h, align='left', line_gap=None, lines=None):
    if max_w <= 0 or max_h <= 0:
        return
    line_px = GLYPH_H * scale
    gap = line_px if line_gap is None else line_gap
    usable = max(1, 1 + (max_h - line_px) // gap)
    if lines is None:
        lines = wrap_text(text, max_w, scale)
    if len(lines) > usable:
        raise ValueError(f'Text would be truncated: {text!r}')
    for index, line in enumerate(lines[:usable]):
        remaining = max_h - index * gap
        if remaining <= 0:
            break
        width = text_width(line, scale)
        if align == 'center':
            lx = x + (max_w - width) // 2
        elif align == 'right':
            lx = x + max_w - width
        else:
            lx = x
        draw_text(canvas, lx, y + index * gap, line, scale, colour, max_w, remaining)


class Canvas:
    def __init__(self):
        self.pixels = bytearray(bytes(PAPER) * (WIDTH * HEIGHT))

    def rect_internal(self, x0, y0, width, height, colour):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(WIDTH, x0 + width)
        y1 = min(HEIGHT, y0 + height)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * WIDTH + x0) * 3
            self.pixels[start:start + len(row)] = row

    def rect(self, x, y, width, height, colour):
        self.rect_internal(x * SS, y * SS, width * SS, height * SS, colour)

    def glyph_cell(self, x, y, width, height, colour, corners):
        offsets = []
        samples = []
        for exposed, (cx, cy) in zip(corners, ((x, y), (x + width - 1, y),
                                              (x, y + height - 1),
                                              (x + width - 1, y + height - 1))):
            if exposed:
                offset = (cy * WIDTH + cx) * 3
                offsets.append(offset)
                samples.append(self.pixels[offset:offset + 3])
        self.rect_internal(x, y, width, height, colour)
        for offset, sample in zip(offsets, samples):
            self.pixels[offset:offset + 3] = sample

    def paper(self):
        # An ordered, rotated printing screen, never random noise. The broad
        # elliptical paper vignette changes brightness by at most four levels.
        # Render both at 2x so the fine dots have clean, antialiased edges.
        pixels = self.pixels
        xdist = [(2 * x - WIDTH) ** 2 for x in range(WIDTH)]
        denom = WIDTH * WIDTH + HEIGHT * HEIGHT
        offset = 0
        for y in range(HEIGHT):
            yd = (2 * y - HEIGHT) ** 2
            for x in range(WIDTH):
                vignette = min(4, 4 * (xdist[x] + yd) // denom)
                u = (29 * x + 8 * y) % 240 - 120
                v = (29 * y - 8 * x) % 240 - 120
                radius = 20 + (16 * x + 11 * y) // WIDTH
                # Ease the edge of each regularly spaced printing dot.
                shade = max(0, min(9, (radius * radius - u * u - v * v) // 28 + 4))
                tone = vignette + shade
                pixels[offset] = PAPER[0] - tone
                pixels[offset + 1] = PAPER[1] - tone
                pixels[offset + 2] = PAPER[2] - tone
                offset += 3

    def downsample(self):
        out = bytearray(OUT_W * OUT_H * 3)
        src = self.pixels
        sw = WIDTH * 3
        for oy in range(OUT_H):
            sy = oy * SS
            row0 = sy * sw
            row1 = row0 + sw
            for ox in range(OUT_W):
                sx = ox * SS * 3
                sx2 = sx + 3
                i00 = row0 + sx
                i01 = row0 + sx2
                i10 = row1 + sx
                i11 = row1 + sx2
                r = src[i00] + src[i01] + src[i10] + src[i11]
                g = src[i00 + 1] + src[i01 + 1] + src[i10 + 1] + src[i11 + 1]
                b = src[i00 + 2] + src[i01 + 2] + src[i10 + 2] + src[i11 + 2]
                di = (oy * OUT_W + ox) * 3
                out[di] = (r + 2) // 4
                out[di + 1] = (g + 2) // 4
                out[di + 2] = (b + 2) // 4
        return out

    def write_png(self, path):
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

        out_pixels = self.downsample()
        rows = b''.join(b'\0' + out_pixels[y * OUT_W * 3:(y + 1) * OUT_W * 3] for y in range(OUT_H))
        header = struct.pack('>IIBBBBB', OUT_W, OUT_H, 8, 2, 0, 0, 0)
        path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


LEADS = (
    ('01 / GULF CONFLICT', ('US AND IRAN', 'TRADE FIRE', 'OVER BAHRAIN'),
     ('IRGC: US RADAR STRUCK.', 'QESHM BLASTS REPORTED.',
      'TANKER HIT IN HORMUZ;', 'ALL 24 CREW ARE SAFE.'),
     '24', ('TANKER CREW', 'ALL SAFE'), RED),
    ('02 / WAR IN EUROPE', ('KERCH BRIDGE', 'HIT FOR A', 'SECOND DAY'),
     ("KYIV'S BIGGEST DRONE RAID.", 'TWO DEAD, RUSSIA SAYS.',
      'CRIMEA LINK HALTED;', 'KYIV: REFINING DISABLED.'),
     '55%', ('RUSSIAN REFINING', 'KYIV SAYS'), RED),
    ('03 / APEC SHENZHEN', ('TRUMP, XI', 'AND PUTIN', 'HEAD TO APEC'),
     ('21 LEADERS MEET IN CHINA.', 'A TRILATERAL IS EXPECTED.',
      'BEIJING SNUBS JAPAN OVER', 'TAIWAN: NO BILATERAL.'),
     '21', ('APEC LEADERS', 'IN SHENZHEN'), TEAL),
)

MID_STORIES = (
    (('NVIDIA POSTS', 'RECORD QUARTER'),
     '$115.8BN SALES, UP 103%; $130BN OUTLOOK. HUANG OFFERS TO RETURN.'),
    (('TRUMP TRIP SHADOWED', 'BY US MIDTERMS'),
     'HE FLIES TO ASIA AFTER DEMOCRATS WIN BOTH CHAMBERS OF CONGRESS.'),
    (('WALL STREET FALLS', 'FOR FOURTH SESSION'),
     'DOW -1.6% TO 50,759. FED DECEMBER RISE PRICED AT 95%.'),
    (("GAZA TRUCE 'FACING", "COLLAPSE' - US BOARD"),
     'BOARD OF PEACE TELLS UN: REBUILDING HAS STALLED.'),
    (('FRANCE: 150,000', 'PROTEST OVER PRICES'),
     "STRIKERS REJECT MACRON'S 1.6% MINIMUM-WAGE RISE."),
    (('COP31 ENTERS', 'ITS FINAL WEEK'),
     "DRAFT: 'IMMEDIATE' FOSSIL EXIT; $120BN FOR ADAPTATION."),
)

# Two complete lines per brief, not clipped excerpts. These are condensed
# exclusively from the original entry's BRIEFS; duplicate APEC, Nvidia and
# Socceroos entries have been removed. Order groups related regional stories.
BRIEFS = (
    ('Voyager 1', '24 light-hours away'),
    ('Measles status lost', 'US, Mexico, Bolivia'),
    ('India bus crash', 'Uttarakhand: 9 dead'),
    ('Sudan holds Haroun', 'ICC fugitive held'),
    ('Quad leaders meet', 'First in two years'),
    ('Trump hints at Kim', 'May meet in China'),
    ('Australia sanctions', '3 settlers listed'),
    ('Jordan 2-0 Australia', 'Football in Doha'),
    ('UK inflation', 'Seen rising to 3.7%'),
    ('Euro prices', 'Seen up 4.0%'),
    ('IMF on Ukraine GDP', 'Sees a 0.5% decline'),
    ('Tara Gas hit', 'Hormuz; crew safe'),
    ('Iran bus mourning', 'Turns political'),
    ('NSA network outage', 'Classified system'),
    ('178 sites attacked', 'Via injected code'),
    ('Chase app fault', 'Accounts, Zelle hit'),
    ('Anthropic IPO', 'Prices today'),
    ('Ghana space agency', 'Cabinet approval'),
    ('Gambia poll pledge', 'Rivals vow peace'),
    ('South Sudan vote', 'UN: Dec. warning'),
    ('Sudan peace talks', 'Geneva talks resume'),
    ('Ramstein: Kyiv asks', 'For interceptors'),
    ('Kyiv deep strikes', 'US official objects'),
    ('Xi snubs Takaichi', 'No bilateral talks'),
    ('Odisha sea rescue', 'Coast guard saves 27'),
    ('France wage rise', '1.6% called too low'),
    ('Gaza aid shortages', 'Agencies report'),
    ('Moscow drone claim', '1,441 down overnight'),
    ('Zaporizhzhia power', 'Substations hit'),
    ('Oil: Brent $92.70', 'WTI near $84.39'),
    ('Gold slips', '$3,819 an ounce'),
    ('Qeshm explosions', 'Reported again'),
    ('Australia refugees', 'Intake cut proposed'),
)

# Equirectangular land mask, sampled at cell centers from 84 N, 180 W.
# Longitude step: 3.75 degrees. Latitude step: 3.5 degrees.
MAP_ROWS = (
    '.......................#####..###########.......................................................',
    '.................####.#####..##############.....................................................',
    '...............####...######...############.............................#####...................',
    '......#........#####.#######.....########.........................######################........',
    '#...#####################.###.....######............#######....##.##############################',
    '...####################..######...####....##.......###########################################..',
    '...#.#################....######...##............####..########################################.',
    '.....##.....############...#####..............#....##.################################...###....',
    '.............############..####..............###..###################################....##.....',
    '..............###################.............########################################..........',
    '...............################................######################################...........',
    '...............###############.................####.####...########################...#.........',
    '...............##############................###.....##############################..#..........',
    '................############.................##.###....#########################.....#..........',
    '................###########...................#####......#######################...##...........',
    '.................#########...................###############.###################................',
    '...................###....#.................#############.###..#################................',
    '....................##.....#................###################...#############.#...............',
    '....................###.#...##.............###############.####.....##...####...................',
    '.......................##..................###################......##...####...#...............',
    '.........................#..................###############.........#.....###..##...............',
    '..........................######............#################.......#.....#......#..............',
    '...........................#######.............##############............##....#................',
    '...........................########...............##########..............##.####...............',
    '...........................#########..............##########..............##.##.#..#............',
    '..........................#############...........#########................#........###.........',
    '...........................############............########....................#.......#........',
    '...........................###########.............########..........................#..........',
    '............................##########.............#######..##...................###.##.........',
    '.............................########..............#######..#...................#######.........',
    '.............................########..............######...#.................##########........',
    '.............................######.................#####.....................###########.......',
    '.............................######.................####.......................##########.......',
    '.............................#####...................##........................##...####........',
    '............................####.....................................................###......#.',
    '............................####......................................................#.......#.',
    '............................###.............................................................##..',
    '............................##..................................................................',
    '............................##..................................................................',
    '.............................##.................................................................',
    '................................................................................................',
    '................................................................................................',
    '...............................#................................................................',
    '.............................###..........................#########...#################.........',
    '............................###...........##################################################....',
    '.........########################......######################################################...',
)

# City, latitude, longitude, and label offsets from the projected point.
MAP_MARKERS = (
    ('Bahrain / Gulf', 26.2, 50.6, 0, 16),
    ('Kerch / Bridge', 45.4, 36.5, 22, 0),
    ('Shenzhen / APEC', 22.5, 114.1, 0, 9),
    ('Brasilia / Brazil', -15.8, -47.9, 0, 0),
    ('Moscow / Drones', 55.8, 37.6, 0, -16),
    ('Jerusalem / Gaza', 31.8, 35.2, -17, 0),
    ('Delhi / India', 28.6, 77.2, 0, 0),
    ('Tokyo / APEC', 35.7, 139.7, 0, 0),
    ('Lagos / W. Africa', 6.5, 3.4, 0, 0),
    ('New York / Dow', 40.7, -74.0, 0, 0),
)


def lines(canvas, x, y, content, scale=2, colour=INK, width=312, gap=None):
    """Print complete, preflighted lines; never silently shrink or truncate."""
    gap = 8 * scale if gap is None else gap
    for index, line in enumerate(content):
        draw_text(canvas, x, y + index * gap, line, scale, colour,
                  max_w=width, max_h=8 * scale)


def draw_header(canvas):
    count = len(LEADS) + len(MID_STORIES) + len(BRIEFS)
    canvas.rect(20, 10, 984, 2, INK)
    draw_text(canvas, 20, 18, f'{count} STORIES / 6 CONTINENTS / ONE PAGE', 2, INK)
    draw_text_block(canvas, 680, 18, 'WEDNESDAY / WORLD DESK', 2, RED, 324, 16, align='right')
    draw_text(canvas, 16, 40, 'THE WORLD', 10, INK)
    draw_text_block(canvas, 600, 54, '18 NOV 2026', 6, RED, 404, 48, align='right')
    canvas.rect(20, 122, 984, 3, INK)
    canvas.rect(20, 128, 984, 1, INK)


def draw_leads(canvas):
    for index, (label, headline, body, figure, caption, accent) in enumerate(LEADS):
        x = 20 + index * 336
        canvas.rect(x, 138, 312, 20, accent)
        draw_text(canvas, x + 6, 140, label, 2, WHITE)
        lines(canvas, x, 166, headline, 3)
        lines(canvas, x, 242, body)
        draw_text(canvas, x, 310, figure, 5, accent)
        caption_x = x + text_width(figure, 5) + 18
        lines(canvas, caption_x, 312, caption, colour=accent,
              width=x + 312 - caption_x)
        if index < 2:
            canvas.rect(x + 323, 166, 1, 184, PALE)
    canvas.rect(20, 356, 984, 2, INK)


def draw_numbers(canvas):
    draw_text(canvas, 20, 366, 'BY THE NUMBERS', 2, RED)
    draw_text_block(canvas, 680, 366, 'WHAT MOVED', 2, RED, 324, 16, align='right')
    stats = (
        ('$92.70', 'BRENT / PER BARREL'),
        ('$3,819', 'GOLD / PER OUNCE'),
        ('50,759', 'DOW / -1.6%'),
        ('+103%', 'NVIDIA SALES / YOY'),
    )
    for index, (figure, label) in enumerate(stats):
        x = 20 + index * 252
        draw_text(canvas, x, 389, figure, 5, INK if index < 3 else TEAL)
        draw_text(canvas, x, 432, label, 2, DARK_GREY)
        if index < 3:
            canvas.rect(x + 239, 391, 1, 53, PALE)
    canvas.rect(20, 454, 984, 1, INK)


def draw_mid_grid(canvas):
    for index, (headline, body) in enumerate(MID_STORIES):
        x = 20 + (index % 3) * 336
        y = 464 + (index // 3) * 85
        lines(canvas, x, y, headline, colour=TEAL)
        draw_text_block(canvas, x, y + 33, body, 2, INK, 312, 46, line_gap=15)
        if index < 3:
            canvas.rect(x, y + 81, 312, 1, PALE)
        if index % 3 < 2:
            canvas.rect(x + 323, y, 1, 79, PALE)


def draw_briefs(canvas):
    canvas.rect(20, 633, 984, 2, INK)
    draw_text(canvas, 20, 640, 'ALSO ON WEDNESDAY', 2, RED)
    draw_text_block(canvas, 412, 640, f'{len(BRIEFS)} NEWS BRIEFS', 2, RED,
                    192, 16, align='right')
    for x in (211, 409, 610):
        canvas.rect(x, 660, 1, 330, PALE)
    for index, (title, body) in enumerate(BRIEFS):
        column, row = divmod(index, 11)
        x = 20 + column * 198
        y = 660 + row * 30
        draw_text(canvas, x, y, title, 2, TEAL, max_w=186, compact=True)
        draw_text(canvas, x, y + 15, body, 2, INK, max_w=186, compact=True)


def dotted_rule(canvas, left, right, y, colour):
    for x in range(left, right, 4):
        canvas.rect(x, y, 2, 1, colour)


def draw_world_map(canvas):
    left, top, step = 620, 694, 4
    right = left + 96 * step
    draw_text(canvas, left, 640, 'WORLD MAP', 2, RED)
    draw_text_block(canvas, left, 640, '18 NOV / LOCATORS', 2, DARK_GREY,
                    right - left, 16, align='right')
    dotted_rule(canvas, left, right, 681, GREY)

    for row_index, row in enumerate(MAP_ROWS):
        for column, cell in enumerate(row):
            if cell == '#':
                canvas.rect(left + column * step, top + row_index * step, 3, 3, GREY)

    pins = []
    for number, (city, latitude, longitude, dx, dy) in enumerate(MAP_MARKERS, 1):
        x = left + round((longitude + 180) / 3.75 * step)
        y = top + round((84 - latitude) / 3.5 * step)
        if dx or dy:
            canvas.rect(min(x, x + dx), min(y, y + dy), abs(dx) + 1, abs(dy) + 1, RED)
            canvas.rect(x - 1, y - 1, 3, 3, RED)
        pins.append((number, city, x + dx, y + dy))

    dotted_rule(canvas, left, right, 891, GREY)
    for number, city, x, y in pins:
        label = str(number)
        size = 20 if number < 10 else 26
        canvas.rect(x - size // 2 - 1, y - size // 2 - 1, size + 2, size + 2, PAPER)
        canvas.rect(x - size // 2, y - size // 2, size, size, RED)
        draw_text(canvas, x - text_width(label, 2) // 2 + 1, y - 7, label, 2, WHITE)
        column, row = divmod(number - 1, 5)
        key_x = left + column * 196
        key_y = 900 + row * 18
        draw_text(canvas, key_x, key_y, label, 2, RED)
        draw_text(canvas, key_x + 28, key_y, city, 2, INK, max_w=160, compact=True)


def verify_text_rendering():
    scratch = Canvas()
    for scale, text in ((2, 'WORLD / 18.11.2026'), (3, 'KERCH BRIDGE'), (6, '18 NOV 2026')):
        seen = set()
        draw_text(scratch, 0, 0, text, scale, INK, seen=seen)
        if len(seen) != glyph_pixels(text):
            raise RuntimeError(f'Incorrect glyph paint at scale {scale}')


def main():
    verify_text_rendering()
    canvas = Canvas()
    canvas.paper()
    draw_header(canvas)
    draw_leads(canvas)
    draw_numbers(canvas)
    draw_mid_grid(canvas)
    draw_briefs(canvas)
    draw_world_map(canvas)
    canvas.rect(20, 995, 984, 2, INK)
    draw_text(canvas, 20, 1000, DATE_TEXT, 2, INK)
    draw_text_block(canvas, 680, 1000, 'WORLD DESK / MAKE.FUN', 2, RED,
                    324, 16, align='right')

    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'))
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'entry.png'
    canvas.write_png(path)

    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('bad PNG signature')
    if struct.unpack('>II', data[16:24]) != (OUT_W, OUT_H):
        raise RuntimeError('bad PNG dimensions')
    if len(data) > 1048576:
        raise RuntimeError('PNG too large')
    count = len(LEADS) + len(MID_STORIES) + len(BRIEFS)
    if not 40 <= count <= 48:
        raise RuntimeError(f'Expected 40-48 story entries, got {count}')
    print(f'ok {len(data)} bytes / {OUT_W}x{OUT_H} / {count} stories / minimum text scale 2')


if __name__ == '__main__':
    main()
