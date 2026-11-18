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
HEADLINE_BOX = (280, 82)
HEADLINE_SCALE = 3
HEADLINE_LINE_GAP = 24
HEADLINE_LINES = 3
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


def draw_text(canvas, x, y, text, scale, colour, max_w=None, max_h=None, seen=None):
    if max_w is not None and max_w <= 0 or max_h is not None and max_h <= 0:
        return
    ix = x * SS
    iy = y * SS
    ibs = scale * SS
    iadv = ADVANCE * scale * SS
    iright = None if max_w is None else ix + max_w * SS
    ibottom = None if max_h is None else iy + max_h * SS
    for index, char in enumerate(text):
        gx = ix + index * iadv
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
                canvas.rect_internal(sx0, sy0, sx1 - sx0, sy1 - sy0, colour)


def draw_text_block(canvas, x, y, text, scale, colour, max_w, max_h, align='left', line_gap=None, lines=None):
    if max_w <= 0 or max_h <= 0:
        return
    line_px = GLYPH_H * scale
    gap = line_px if line_gap is None else line_gap
    usable = max(1, 1 + (max_h - line_px) // gap)
    if lines is None:
        lines = wrap_text(text, max_w, scale)
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

    def semi_circle(self, x, y, width, height, colour):
        ix = x * SS
        iy = y * SS
        iw = width * SS
        ih = height * SS
        cx = ix + iw / 2.0
        rx = iw / 2.0
        for yy in range(iy, iy + ih + 1):
            offset = (iy + ih - yy) / float(ih)
            span = rx * (1.0 - offset * offset) ** 0.5
            left = int(cx - span)
            right = int(cx + span)
            self.rect_internal(left, yy, right - left + 1, 1, colour)

    def arc(self, x, y, width, height, colour, thickness=2):
        ix = x * SS
        iy = y * SS
        iw = width * SS
        ih = height * SS
        ith = max(1, thickness * SS)
        cx = ix + iw / 2.0
        rx = iw / 2.0
        base = iy + ih
        for yy in range(iy, iy + ih + 1):
            offset = (base - yy) / float(ih)
            if offset < -1.0 or offset > 1.0:
                continue
            span = rx * (1.0 - offset * offset) ** 0.5
            for edge in (cx - span, cx + span):
                self.rect_internal(int(round(edge)) - ith // 2, yy, ith, 1, colour)

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


def draw_illustration(canvas, index, x, y):
    if index == 0:
        canvas.rect(x, y + 42, 286, 30, TEAL)
        canvas.arc(x + 178, y + 8, 64, 42, GREY, 2)
        canvas.rect(x + 205, y + 46, 5, 6, GREY)
        for px, py in ((166, 20), (226, 30), (258, 14)):
            canvas.rect(x + px, y + py, 6, 6, RED)
        for mx, my in ((38, 18), (106, 8)):
            canvas.rect(x + mx + 9, y + my + 1, 3, 3, GREY)
            canvas.rect(x + mx + 2, y + my + 1, 7, 3, GREY)
            canvas.rect(x + mx, y + my, 3, 1, GREY)
            canvas.rect(x + mx, y + my + 4, 3, 1, GREY)
    elif index == 1:
        canvas.rect(x, y + 50, 286, 26, TEAL)
        canvas.semi_circle(x + 18, y + 34, 106, 32, TEAL)
        canvas.semi_circle(x + 136, y + 34, 106, 32, TEAL)
        canvas.rect(x + 12, y + 38, 12, 30, INK)
        canvas.rect(x + 124, y + 38, 12, 30, INK)
        canvas.rect(x + 242, y + 38, 12, 30, INK)
        canvas.rect(x + 8, y + 28, 270, 10, INK)
        canvas.rect(x + 252, y + 12, 6, 6, RED)
    else:
        for bx, bh in ((12, 38), (42, 54), (74, 30), (106, 62), (140, 44), (174, 56), (208, 36), (242, 50)):
            top = 75 - bh
            canvas.rect(x + bx, y + top, 26, bh, INK)
            for wy in range(top + 7, 75, 12):
                canvas.rect(x + bx + 5, y + wy, 5, 5, OCHRE)
                canvas.rect(x + bx + 15, y + wy, 5, 5, OCHRE)
        for fx, fc in ((52, RED), (150, WHITE), (224, TEAL)):
            canvas.rect(x + fx, y + 2, 2, 18, INK)
            canvas.rect(x + fx + 2, y + 3, 14, 8, fc)
            if fc == WHITE:
                canvas.rect(x + fx + 1, y + 2, 16, 1, INK)
                canvas.rect(x + fx + 1, y + 12, 16, 1, INK)
                canvas.rect(x + fx + 15, y + 3, 1, 10, INK)


def draw_header(canvas):
    canvas.rect(0, 0, OUT_W, 96, INK)
    draw_text_block(canvas, 20, 14, 'THE DAY IN WORLD NEWS', 1, WHITE, 400, 9)
    draw_text_block(canvas, 20, 14, '45 STORIES - 6 CONTINENTS - ONE PAGE', 1, WHITE, 984, 9, align='right')
    draw_text_block(canvas, 0, 30, DATE_TEXT, 6, WHITE, OUT_W, 44, align='center', line_gap=42)
    subtitle = 'Every story here happened, or was first reported, on this day.'
    draw_text_block(canvas, 0, 82, subtitle, 1, PALE, OUT_W, 9, align='center')


def prepare_headline(headline, panel):
    original = headline
    lines = wrap_text(headline, HEADLINE_BOX[0], HEADLINE_SCALE)
    while len(lines) > HEADLINE_LINES:
        words = headline.split()
        if len(words) == 1:
            raise ValueError(f'lead panel {panel} headline cannot be shortened')
        headline = ' '.join(words[:-1])
        lines = wrap_text(headline, HEADLINE_BOX[0], HEADLINE_SCALE)
    if panel == 1 and headline != original:
        raise ValueError('lead panel 1 headline must not be shortened')
    if ' '.join(lines) != headline:
        raise ValueError(f'lead panel {panel} headline lost text while wrapping')
    for line in lines:
        if text_width(line, HEADLINE_SCALE) > HEADLINE_BOX[0]:
            raise ValueError(f'lead panel {panel} line exceeds 280px: {line}')
    if HEADLINE_LINES * HEADLINE_LINE_GAP > HEADLINE_BOX[1]:
        raise ValueError('three headline lines do not fit in the 82px box')
    print(f'lead panel {panel} wrapped headline lines (scale 3, {HEADLINE_BOX[0]}x{HEADLINE_BOX[1]}):')
    for line in lines:
        print(f'  {line}')
    return lines


def draw_leads(canvas):
    leads = [
        ('1  MIDDLE EAST - CONFLICT', 'US AND IRAN TRADE FIRE OVER BAHRAIN', "Iran's IRGC says its drones struck a US radar at Bahrain's Sheikh Isa base; Iranian media report blasts and smoke over Qeshm island. A tanker was hit in Hormuz and all 24 crew are safe.", RED),
        ('2  EUROPE - WAR IN UKRAINE', 'KERCH BRIDGE HIT FOR A SECOND DAY', 'Kyiv mounted its biggest drone raid of the war; Russia says two died and traffic over the Crimea link is halted. Kyiv says 55% of Russian refining is disabled.', INK),
        ('3  ASIA - DIPLOMACY', 'TRUMP, XI AND PUTIN HEAD FOR SHENZHEN', "APEC's 21 leaders meet in Shenzhen today and a US-China-Russia trilateral is expected. Beijing refuses a bilateral with Japan's Takaichi over Taiwan.", TEAL),
    ]
    for index, (label, headline, body, accent) in enumerate(leads):
        x = 20 + index * 344
        y = 104
        canvas.rect(x, y, 296, 272, CREAM)
        canvas.rect(x, y, 296, 1, INK)
        canvas.rect(x, y + 271, 296, 1, INK)
        canvas.rect(x, y, 1, 272, INK)
        canvas.rect(x + 295, y, 1, 272, INK)
        canvas.rect(x + 1, y + 1, 294, 4, accent)
        canvas.rect(x + 1, y + 5, 294, 18, INK)
        draw_text_block(canvas, x + 6, y + 8, label, 1, WHITE, 284, 12)
        lines = prepare_headline(headline, index + 1)
        draw_text_block(canvas, x + 8, y + 26, headline, HEADLINE_SCALE, INK,
                        HEADLINE_BOX[0], HEADLINE_BOX[1], line_gap=HEADLINE_LINE_GAP, lines=lines)
        draw_text_block(canvas, x + 8, y + 112, body, 1, INK, 280, 72, line_gap=10)
        draw_illustration(canvas, index, x + 5, y + 190)


def draw_mid_grid(canvas):
    stories = [
        ('NVIDIA POSTS RECORD QUARTER', 'Revenue $115.8bn, up 103%; a $130bn outlook lifts shares, and Huang offers to return.'),
        ('TRIP SHADOWED BY MIDTERMS', 'Trump flies to Asia after Democrats won both chambers of Congress.'),
        ('FOURTH STRAIGHT FALL ON WALL ST', 'The Dow drops 1.6% to 50,759; a December Fed rise is priced at 95%.'),
        ("GAZA TRUCE 'FACING COLLAPSE'", 'The US-led Board of Peace tells the Security Council that rebuilding has stalled.'),
        ('FRANCE PROTESTS OVER PRICES', "150,000 join strikes and Macron's 1.6% minimum-wage rise is rejected."),
        ('COP31 ENTERS FINAL WEEK', "The Antalya draft urges an 'immediate' fossil-fuel exit and $120bn for adaptation."),
    ]
    for index, (headline, body) in enumerate(stories):
        col = index % 3
        row = index // 3
        x = 20 + col * 344
        y = 384 + row * 108
        canvas.rect(x, y, 296, 100, CREAM)
        canvas.rect(x, y, 296, 1, GREY)
        canvas.rect(x, y + 99, 296, 1, GREY)
        canvas.rect(x, y, 1, 100, GREY)
        canvas.rect(x + 295, y, 1, 100, GREY)
        canvas.rect(x + 5, y + 7, 16, 16, INK)
        draw_text_block(canvas, x + 5, y + 11, str(index + 4), 1, WHITE, 16, 10, align='center')
        draw_text_block(canvas, x + 24, y + 2, headline.upper(), 2, INK, 264, 36, line_gap=16)
        draw_text_block(canvas, x + 24, y + 42, body, 1, GREY, 264, 36, line_gap=9)


def draw_numbers(canvas):
    canvas.rect(20, 608, 984, 46, INK)
    draw_text_block(canvas, 28, 616, 'BY THE NUMBERS', 1, WHITE, 160, 9)
    stats = (
        ('$115.8BN', 'NVIDIA QUARTER'),
        ('16.09BN MI', 'VOYAGER 1'),
        ('55%', 'RUSSIAN REFINING HIT'),
        ('95%', 'FED RISE PRICED'),
    )
    for index, (figure, label) in enumerate(stats):
        centre = 292 + index * 204
        box_x = centre - 95
        draw_text_block(canvas, box_x, 612, figure, 3, WHITE, 190, 22, align='center', line_gap=21)
        draw_text_block(canvas, box_x, 637, label, 1, PALE, 190, 9, align='center')


MAP_ROWS = (
    '................................................................',
    '........................#.......................................',
    '..##.#.#..............#####.....#.........######.##..#..........',
    '.#############.#.....#######....##.#....##############..........',
    '###################...#####.########.#####################......',
    '.##################.....#...##############################......',
    '...#################.......###############################......',
    '..##################.........##############################.....',
    '...#################.........##############################.....',
    '....################..........#############################.....',
    '....#############..............#########################........',
    '.......#..##.##.#.............##########################........',
    '...........#.................###########..######..###...........',
    '.............................##########....#####................',
    '...............####..........###########.....###....###.........',
    '................###...........##########...........######.......',
    '...............######.......############............##..........',
    '...............######.........#########.........................',
    '..............######.........##########.........................',
    '...............######........###########........................',
    '..............########........##########...........#.#.#........',
    '..............#######..........#######.............######.......',
    '...............#####............#####.............########......',
    '...............#####............####..............#######.......',
    '...............######.............#................###..........',
    '................###..................................#..........',
    '................##.#........................................#...',
    '.................#........................................####..',
    '................................................................',
    '................................##.##..##.......................',
    '..............................#..##.####........................',
    '................................................................',
)

MAP_MARKERS = (
    (1, 52, 9),
    (2, 33, 6),
    (3, 55, 10),
    (4, 10, 6),
    (5, 33, 12),
    (6, 35, 17),
    (7, 46, 13),
    (8, 54, 22),
    (9, 9, 19),
)

BRIEFS = (
    '10. Voyager 1 - now 24 light-hours from Earth.',
    '11. Measles - US, Mexico, Bolivia lose status.',
    '12. India - Bus crash in Uttarakhand kills nine.',
    '13. Sudan - Army holds ICC fugitive Ahmed Haroun.',
    '14. APEC opens - 21 leaders meet in Shenzhen.',
    "15. Quad - First leaders' summit in two years.",
    '16. Kim meeting - Trump hints at talks in China.',
    '17. Sanctions - Australia lists three settlers.',
    '18. Football - Jordan beat Australia 2-0 in Doha.',
    '19. UK inflation - Seen rising to 3.7%.',
    '20. Euro prices - Seen up 4.0%.',
    '21. Ukraine economy - IMF sees GDP down 0.5%.',
    '22. Tanker - Tara Gas hit in Hormuz; crew safe.',
    '23. Iran - Bus-crash mourning turns political.',
    '24. NSA - Classified network outage.',
    '25. Cyberattack - 178 sites hit via injected code.',
    '26. Bank apps - A Chase fault hit accounts, Zelle.',
    '27. Anthropic - IPO prices today.',
    '28. Nvidia - Huang offers to return if asked.',
    '29. Ghana - Cabinet approves space agency.',
    '30. Gambia - Rivals pledge a peaceful poll.',
    '31. South Sudan - UN warns on December polls.',
    '32. Sudan talks - Geneva rounds resume.',
    '33. Ramstein - Kyiv asks for interceptors.',
    '34. Deep strikes - US official criticises Kyiv.',
    '35. Takaichi - Xi refuses a bilateral meeting.',
    '36. Odisha - Coast Guard saves 27 crew.',
    '37. Socceroos - Beaten 2-0 by Jordan in Doha.',
    '38. France - 1.6% wage rise called inadequate.',
    '39. Gaza - Aid agencies report shortages.',
    '40. Moscow - 1,441 drones downed overnight.',
    '41. Kyiv power - Substations hit in Zaporizhzhia.',
    '42. Oil - Brent near $92.70; WTI $84.39.',
    '43. Gold - Slips to $3,819 an ounce.',
    '44. Qeshm - Explosions reported again.',
    '45. Australia - Refugee intake cut proposed.',
)


def draw_map_and_briefs(canvas):
    canvas.rect(20, 662, 356 - 20, 988 - 662, CREAM)
    canvas.rect(20, 662, 356 - 20, 1, INK)
    canvas.rect(20, 988 - 1, 356 - 20, 1, INK)
    canvas.rect(20, 662, 1, 988 - 662, INK)
    canvas.rect(356 - 1, 662, 1, 988 - 662, INK)
    draw_text_block(canvas, 30, 672, 'WHERE THE NEWS HAPPENED', 1, RED, 320, 9)
    for row_index, row in enumerate(MAP_ROWS):
        for column_index, cell in enumerate(row):
            if cell == '#':
                canvas.rect(26 + column_index * 5, 700 + row_index * 5, 4, 4, INK)
    for digit, column_index, row_index in MAP_MARKERS:
        marker_x = 26 + column_index * 5 - 4
        marker_y = 700 + row_index * 5 - 4
        canvas.rect(marker_x, marker_y, 12, 12, RED)
        draw_text_block(canvas, marker_x, marker_y + 2, str(digit), 1, WHITE, 12, 10, align='center')
    draw_text_block(canvas, 30, 928, 'Numbered dots mark stories 1-9.', 1, GREY, 320, 9)
    draw_text_block(canvas, 30, 944, '45 stories, six continents, one day.', 1, GREY, 320, 9)

    draw_text_block(canvas, 372, 672, 'ALSO ON WEDNESDAY 18 NOVEMBER - 36 MORE STORIES', 1, RED, 632, 9)
    canvas.rect(688, 692, 1, 273, DARK_GREY)
    for brief in BRIEFS:
        if text_width(brief, 1) > 312:
            raise ValueError(f'Brief exceeds 312px: {brief}')
    for column_index, x in enumerate((372, 692)):
        for row_index in range(18):
            brief = BRIEFS[column_index * 18 + row_index]
            y = 692 + row_index * 16
            dot = brief.index('.') + 1
            number = brief[:dot]
            body = brief[dot:]
            number_width = text_width(number, 1)
            draw_text(canvas, x, y, number, 1, RED, 312, 10)
            draw_text(canvas, x + number_width, y, body, 1, DARK_GREY, 312 - number_width, 10)


def verify_text_rendering():
    width = text_width(DATE_TEXT, 6)
    print(f'date width at scale 6: {width} px (26 chars x 6 advance x 6 scale; advance 7 would give 1092 px)')
    if width != 936 or width > 1000:
        raise RuntimeError(f'date width {width} px is not the expected 936 px')
    samples = ((HEADLINE_SCALE, 'US AND IRAN TRADE FIRE OVER BAHRAIN'),
               (6, DATE_TEXT), (3, '16.09BN MI'))
    for scale, text in samples:
        seen = set()
        draw_text(Canvas(), 0, 0, text, scale, WHITE, seen=seen)
        expected = glyph_pixels(text)
        if len(seen) != expected:
            raise RuntimeError(f'scale {scale}: {len(seen)} blocks for {expected} font pixels')
    print('glyph paint check: one scale x scale block per font pixel, no second pass')


def main():
    verify_text_rendering()
    canvas = Canvas()
    draw_header(canvas)
    draw_leads(canvas)
    draw_mid_grid(canvas)
    draw_numbers(canvas)
    draw_map_and_briefs(canvas)
    footer = 'All stories reported on Wednesday 18 November 2026 - compiled from wire reports - make.fun'
    draw_text_block(canvas, 0, 1000, footer, 1, GREY, OUT_W, 9, align='center')

    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'))
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'entry.png'
    canvas.write_png(path)

    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('bad PNG signature')
    if struct.unpack('>II', data[16:24]) != (OUT_W, OUT_H):
        raise RuntimeError('bad PNG dimensions')
    if len(data) >= 1048576:
        raise RuntimeError('PNG too large')
    print(f'ok {len(data)}')


if __name__ == '__main__':
    main()
