import os
import struct
import zlib
from pathlib import Path

WIDTH = HEIGHT = 1024
PAPER = (246, 243, 234)
INK = (23, 32, 48)
RED = (178, 44, 44)
TEAL = (20, 90, 90)
OCHRE = (196, 140, 40)
CREAM = (252, 250, 244)
GREY = (110, 108, 104)
DARK_GREY = (60, 58, 56)
PALE = (200, 205, 215)
WHITE = (255, 255, 255)
SHADE = (236, 234, 228)

GLYPHS = {
    'A': '0110/1001/1001/1111/1001/1001/1001',
    'B': '1110/1001/1001/1110/1001/1001/1110',
    'C': '0111/1000/1000/1000/1000/1000/0111',
    'D': '1110/1001/1001/1001/1001/1001/1110',
    'E': '1111/1000/1000/1110/1000/1000/1111',
    'F': '1111/1000/1000/1110/1000/1000/1000',
    'G': '0111/1000/1000/1011/1001/1001/0111',
    'H': '1001/1001/1001/1111/1001/1001/1001',
    'I': '1111/0110/0110/0110/0110/0110/1111',
    'J': '0011/0001/0001/0001/1001/1001/0110',
    'K': '1001/1001/1010/1100/1010/1001/1001',
    'L': '1000/1000/1000/1000/1000/1000/1111',
    'M': '1001/1111/1111/1001/1001/1001/1001',
    'N': '1001/1101/1101/1011/1011/1001/1001',
    'O': '0110/1001/1001/1001/1001/1001/0110',
    'P': '1110/1001/1001/1110/1000/1000/1000',
    'Q': '0110/1001/1001/1001/1011/0110/0001',
    'R': '1110/1001/1001/1110/1010/1001/1001',
    'S': '0111/1000/1000/0110/0001/0001/1110',
    'T': '1111/0110/0110/0110/0110/0110/0110',
    'U': '1001/1001/1001/1001/1001/1001/0110',
    'V': '1001/1001/1001/1001/1001/0110/0110',
    'W': '1001/1001/1001/1001/1111/1111/1001',
    'X': '1001/1001/0110/0110/0110/1001/1001',
    'Y': '1001/1001/1001/0110/0110/0110/0110',
    'Z': '1111/0001/0010/0110/0100/1000/1111',
    'a': '0000/0000/0110/1001/1111/1001/0111',
    'b': '1000/1000/1110/1001/1001/1001/1110',
    'c': '0000/0000/0111/1000/1000/1000/0111',
    'd': '0001/0001/0111/1001/1001/1001/0111',
    'e': '0000/0000/0111/1001/1111/1000/0111',
    'f': '0010/0100/1110/0100/0100/0100/0100',
    'g': '0000/0111/1001/1001/0111/0001/0110',
    'h': '1000/1000/1110/1001/1001/1001/1001',
    'i': '0110/0000/0110/0110/0110/0110/0110',
    'j': '0010/0000/0010/0010/0010/1010/0100',
    'k': '1000/1000/1001/1010/1100/1010/1001',
    'l': '0110/0110/0110/0110/0110/0110/0110',
    'm': '0000/0000/1101/1111/1111/1001/1001',
    'n': '0000/0000/1110/1001/1001/1001/1001',
    'o': '0000/0000/0110/1001/1001/1001/0110',
    'p': '0000/1110/1001/1001/1110/1000/1000',
    'q': '0000/0111/1001/1001/0111/0001/0001',
    'r': '0000/0000/1011/1100/1000/1000/1000',
    's': '0000/0000/0111/1000/0110/0001/1110',
    't': '0100/0100/1110/0100/0100/0100/0011',
    'u': '0000/0000/1001/1001/1001/1011/0111',
    'v': '0000/0000/1001/1001/1001/0110/0110',
    'w': '0000/0000/1001/1001/1111/1111/1001',
    'x': '0000/0000/1001/0110/0110/0110/1001',
    'y': '0000/1001/1001/0111/0001/0001/0110',
    'z': '0000/0000/1111/0010/0100/1000/1111',
    '0': '0110/1001/1011/1001/1101/1001/0110',
    '1': '0010/0110/0010/0010/0010/0010/0111',
    '2': '0110/1001/0001/0010/0100/1000/1111',
    '3': '1110/0001/0001/0110/0001/0001/1110',
    '4': '1001/1001/1001/1111/0001/0001/0001',
    '5': '1111/1000/1000/1110/0001/0001/1110',
    '6': '0111/1000/1000/1110/1001/1001/0110',
    '7': '1111/0001/0010/0010/0100/0100/0100',
    '8': '0110/1001/1001/0110/1001/1001/0110',
    '9': '0110/1001/1001/0111/0001/0001/1110',
    ' ': '0000/0000/0000/0000/0000/0000/0000',
    '.': '0000/0000/0000/0000/0000/0110/0110',
    ',': '0000/0000/0000/0000/0110/0010/0100',
    ':': '0000/0110/0110/0000/0110/0110/0000',
    ';': '0000/0110/0110/0000/0110/0010/0100',
    "'": '0010/0010/0100/0000/0000/0000/0000',
    '-': '0000/0000/0000/1111/0000/0000/0000',
    '%': '1001/0001/0010/0010/0100/1000/1001',
    '$': '0010/0111/1010/0110/0101/1110/0100',
    '&': '0110/1001/1010/0100/1011/1001/0111',
    '/': '0001/0001/0010/0010/0100/1000/1000',
}


def text_width(text, scale=1):
    return max(0, len(text) * 5 - 1) * scale


def wrap_text(text, max_w, scale=1):
    lines = []
    line = ''
    for word in text.split():
        if text_width(word, scale) > max_w:
            word = ''.join(ch for ch in word if text_width(ch, scale) <= max_w)
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


def draw_text_clipped(canvas, x, y, text, scale, colour, max_w, max_h):
    if max_w <= 0 or max_h <= 0:
        return
    right = x + max_w
    bottom = y + max_h
    for index, char in enumerate(text):
        glyph = GLYPHS.get(char, GLYPHS[' ']).split('/')
        gx = x + index * 5 * scale
        if gx >= right:
            break
        for row_index, row in enumerate(glyph):
            py = y + row_index * scale
            if py >= bottom:
                break
            sy0 = max(py, y)
            sy1 = min(py + scale, bottom)
            if sy0 >= sy1:
                continue
            for col_index, pixel in enumerate(row):
                if pixel != '1':
                    continue
                px = gx + col_index * scale
                sx0 = max(px, x)
                sx1 = min(px + scale, right)
                if sx0 < sx1:
                    canvas.rect(sx0, sy0, sx1 - sx0, sy1 - sy0, colour)


def draw_text_block(canvas, x, y, text, scale, colour, max_w, max_h, align='left', line_gap=None):
    line_px = 7 * scale
    if max_h < line_px:
        return
    gap = line_px if line_gap is None else line_gap
    usable = 1 + (max_h - line_px) // gap
    lines = wrap_text(text, max_w, scale)[:usable]
    for index, line in enumerate(lines):
        remaining = max_h - index * gap
        if remaining < line_px:
            break
        width = text_width(line, scale)
        if align == 'center':
            lx = x + (max_w - width) // 2
        elif align == 'right':
            lx = x + max_w - width
        else:
            lx = x
        draw_text_clipped(canvas, lx, y + index * gap, line, scale, colour, max_w, remaining)


class Canvas:
    def __init__(self):
        self.pixels = bytearray(bytes(PAPER) * (WIDTH * HEIGHT))

    def rect(self, x, y, width, height, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(WIDTH, x + width)
        y1 = min(HEIGHT, y + height)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * WIDTH + x0) * 3
            self.pixels[start:start + len(row)] = row

    def semi_circle(self, x, y, width, height, colour):
        cx = x + width / 2.0
        rx = width / 2.0
        for yy in range(y, y + height + 1):
            offset = (y + height - yy) / float(height)
            span = rx * (1.0 - offset * offset) ** 0.5
            left = int(cx - span)
            right = int(cx + span)
            self.rect(left, yy, right - left + 1, 1, colour)

    def arc(self, x, y, width, height, colour, thickness=2):
        cx = x + width / 2.0
        rx = width / 2.0
        base = y + height
        for yy in range(y, y + height + 1):
            offset = (base - yy) / float(height)
            if offset < -1.0 or offset > 1.0:
                continue
            span = rx * (1.0 - offset * offset) ** 0.5
            for edge in (cx - span, cx + span):
                self.rect(int(round(edge)) - thickness // 2, yy, thickness, 1, colour)

    def write_png(self, path):
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

        rows = b''.join(b'\0' + self.pixels[y * WIDTH * 3:(y + 1) * WIDTH * 3] for y in range(HEIGHT))
        header = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
        path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def draw_illustration(canvas, index, x, y):
    if index == 0:
        canvas.rect(x, y + 42, 286, 30, TEAL)
        canvas.rect(x + 28, y + 31, 104, 13, OCHRE)
        canvas.rect(x + 44, y + 24, 72, 9, OCHRE)
        canvas.rect(x + 60, y + 18, 40, 8, OCHRE)
        canvas.arc(x + 178, y + 8, 64, 42, GREY, 2)
        canvas.rect(x + 205, y + 46, 5, 6, GREY)
        for px, py in ((166, 20), (226, 30), (258, 14)):
            canvas.rect(x + px, y + py, 6, 6, RED)
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
    canvas.rect(0, 0, WIDTH, 96, INK)
    draw_text_block(canvas, 20, 14, 'THE DAY IN WORLD NEWS', 1, WHITE, 400, 9)
    draw_text_block(canvas, 20, 14, '45 STORIES - 6 CONTINENTS - ONE PAGE', 1, WHITE, 984, 9, align='right')
    draw_text_block(canvas, 0, 30, 'WEDNESDAY 18 NOVEMBER 2026', 6, WHITE, WIDTH, 44, align='center', line_gap=42)
    subtitle = 'Every story here happened, or was first reported, on this day.'
    draw_text_block(canvas, 0, 82, subtitle, 1, PALE, WIDTH, 9, align='center')


def draw_leads(canvas):
    leads = [
        ('1  MIDDLE EAST - CONFLICT', 'US AND IRAN TRADE FIRE OVER BAHRAIN AND QESHM', "Iran's IRGC says its drones struck a US radar at Bahrain's Sheikh Isa base; Iranian media report blasts and smoke over Qeshm island. A tanker was hit in Hormuz and all 24 crew are safe.", RED),
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
        draw_text_block(canvas, x + 8, y + 26, headline.upper(), 3, INK, 280, 82, line_gap=24)
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
        draw_text_block(canvas, x + 5, y + 10, str(index + 4), 1, WHITE, 16, 10, align='center')
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
    '10. VOYAGER 1 - now 24 light-hours from Earth.',
    '11. MEASLES - US, Mexico, Bolivia lose status.',
    '12. INDIA - Bus crash in Uttarakhand kills nine.',
    '13. SUDAN - Army holds ICC fugitive Ahmed Haroun.',
    '14. APEC OPENS - 21 leaders meet in Shenzhen.',
    "15. QUAD - First leaders' summit in two years.",
    '16. KIM MEETING - Trump hints at talks in China.',
    '17. SANCTIONS - Australia lists three settlers.',
    '18. FOOTBALL - Jordan beat Australia 2-0 in Doha.',
    '19. UK INFLATION - Seen rising to 3.7%.',
    '20. EURO PRICES - Seen up 4.0%.',
    '21. UKRAINE ECONOMY - IMF sees GDP down 0.5%.',
    '22. TANKER - Tara Gas hit in Hormuz; crew safe.',
    '23. IRAN - Bus-crash mourning turns political.',
    '24. NSA - Classified network outage.',
    '25. CYBERATTACK - 178 sites hit via injected code.',
    '26. BANK APPS - A Chase fault hit accounts, Zelle.',
    '27. ANTHROPIC - IPO prices today.',
    '28. NVIDIA - Huang offers to return if asked.',
    '29. GHANA - Cabinet approves space agency.',
    '30. GAMBIA - Rivals pledge a peaceful poll.',
    '31. SOUTH SUDAN - UN warns on December polls.',
    '32. SUDAN TALKS - Geneva rounds resume.',
    '33. RAMSTEIN - Kyiv asks for interceptors.',
    '34. DEEP STRIKES - US official criticises Kyiv.',
    '35. TAKAICHI - Xi refuses a bilateral meeting.',
    '36. ODISHA - Coast Guard saves 27 crew.',
    '37. SOCCEROOS - Beaten 2-0 by Jordan in Doha.',
    '38. FRANCE - 1.6% wage rise called inadequate.',
    '39. GAZA - Aid agencies report shortages.',
    '40. MOSCOW - 1,441 drones downed overnight.',
    '41. KYIV POWER - Substations hit in Zaporizhzhia.',
    '42. OIL - Brent near $92.70; WTI $84.39.',
    '43. GOLD - Slips to $3,819 an ounce.',
    '44. QESHM - Explosions reported again.',
    '45. AUSTRALIA - Refugee intake cut proposed.',
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
        if text_width(brief, 1) > 308:
            raise ValueError(f'Brief exceeds 308px: {brief}')
    for column_index, x in enumerate((372, 692)):
        for row_index in range(18):
            brief = BRIEFS[column_index * 18 + row_index]
            y = 692 + row_index * 16
            dot = brief.index('.') + 1
            number = brief[:dot]
            body = brief[dot:]
            number_width = text_width(number, 1)
            draw_text_clipped(canvas, x, y, number, 1, RED, 308, 10)
            draw_text_clipped(canvas, x + number_width, y, body, 1, DARK_GREY, 308 - number_width, 10)


def main():
    canvas = Canvas()
    draw_header(canvas)
    draw_leads(canvas)
    draw_mid_grid(canvas)
    draw_numbers(canvas)
    draw_map_and_briefs(canvas)
    footer = 'ALL STORIES REPORTED ON WEDNESDAY 18 NOVEMBER 2026 - COMPILED FROM WIRE REPORTS - MAKE.FUN'
    draw_text_block(canvas, 0, 1000, footer, 1, GREY, WIDTH, 9, align='center')

    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'))
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'entry.png'
    canvas.write_png(path)

    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError('bad PNG signature')
    if struct.unpack('>II', data[16:24]) != (WIDTH, HEIGHT):
        raise RuntimeError('bad PNG dimensions')
    if len(data) >= 1048576:
        raise RuntimeError('PNG too large')
    print('ok')


if __name__ == '__main__':
    main()
