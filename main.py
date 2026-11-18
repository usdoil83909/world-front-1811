"""Draw a deterministic newspaper front page using only Python's standard library."""

import os
from pathlib import Path
import struct
import zlib


WIDTH = HEIGHT = 1024
INK = (25, 36, 43)
WHITE = (255, 255, 255)
RED = (163, 47, 37)
PAPER = (245, 241, 229)

# Four-pixel-wide bitmap letterforms; all text uses this embedded font.
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
    '|': '0010/0010/0010/0010/0010/0010/0010',
}

COLUMNS = [
    ('EUROPE', [
        'KERCH BRIDGE HIT FOR A SECOND DAY',
        'BIGGEST DRONE RAID OF THE WAR',
        "US CRITICISES KYIV'S DEEP STRIKES",
        'KYIV ASKS RAMSTEIN FOR INTERCEPTORS',
        '150,000 PROTEST IN FRANCE ON PAY',
        'MACRON OFFERS 1.6% WAGE RISE',
        'IMF SEES UKRAINE GDP FALLING 0.5%',
        'UK INFLATION SEEN AT 3.7%',
        'KYIV: 55% OF RUSSIAN REFINING HIT',
        'EURO AREA PRICES SEEN UP 4.0%',
    ]),
    ('MIDDLE EAST AND AFRICA', [
        'IRAN DRONE HITS US RADAR IN BAHRAIN',
        'BLASTS OVER MANAMA AFTER ALERT',
        'MISSILE HITS LPG TANKER IN HORMUZ',
        'ALL 24 CREW SAFE ON TARA GAS',
        'EXPLOSIONS REPORTED ON QESHM ISLAND',
        "GAZA TRUCE 'FACING COLLAPSE'",
        'SUDAN ARMY HOLDS ICC FUGITIVE',
        'GENEVA TALKS RESUME ON SUDAN WAR',
        'GAMBIA RIVALS PLEDGE PEACEFUL POLL',
        'GHANA SETS UP SPACE AGENCY',
    ]),
    ('ASIA-PACIFIC', [
        'APEC OPENS IN SHENZHEN',
        'TRUMP, XI AND PUTIN TO MEET',
        'XI REFUSES TALKS WITH TAKAICHI',
        'QUAD ADDS EXERCISE AND CABLE PACT',
        'TRUMP HINTS AT MEETING KIM JONG UN',
        'INDIA BUS CRASH KILLS NINE',
        '25 HURT IN GORGE PLUNGE',
        'AUSTRALIA SANCTIONS THREE SETTLERS',
        'JORDAN BEAT AUSTRALIA 2-0 IN DOHA',
        'UN WARNS SOUTH SUDAN ON POLLS',
    ]),
    ('AMERICAS AND THE WORLD', [
        'US AND MEXICO LOSE MEASLES STATUS',
        'DOW FALLS 1.6% BEFORE NVIDIA',
        'NVIDIA POSTS RECORD $115.8BN',
        'NVIDIA SEES $130BN NEXT QUARTER',
        'HUANG OFFERS TO RETURN TO NVIDIA',
        'DECEMBER FED RISE PRICED AT 95%',
        'ANTHROPIC LISTING SET TO PRICE',
        'BANK APPS HIT BY CHASE OUTAGE',
        'VOYAGER 1 REACHES ONE LIGHT-DAY',
        '178 SITES HIT BY INJECTED CODE',
    ]),
]

DAY_BOARD_TOP = 840
DAY_BOARD_ROWS = (
    'DOW 50,759 -1.6%   S&P 7,341 -1.0%   BRENT $92.70   GOLD $3,820   VOYAGER 1 16.09BN MI',
    "COP31 DRAFT: 'IMMEDIATE' FOSSIL-FUEL EXIT, $120BN ADAPTATION   NSA CLASSIFIED NET DOWN   ANTHROPIC DEBUT TODAY",
)


def text_width(text, scale=2):
    return max(0, len(text) * 5 - 1) * scale


def wrap(text, width, scale=2):
    lines = []
    line = ''
    for word in text.upper().split():
        if text_width(word, scale) > width:
            raise ValueError(f'Word exceeds wrap width: {word}')
        candidate = f'{line} {word}' if line else word
        if text_width(candidate, scale) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


class Canvas:
    def __init__(self):
        self.pixels = bytearray(WIDTH * HEIGHT * 3)
        # A fixed paper grain gives the otherwise flat bitmap a printed texture.
        state = 18112026
        for i in range(0, len(self.pixels), 3):
            state = (1664525 * state + 1013904223) & 0xffffffff
            shade = (state >> 30) & 3
            self.pixels[i:i + 3] = bytes(c - shade for c in PAPER)

    def rect(self, x, y, width, height, color):
        assert 0 <= x <= x + width <= WIDTH
        assert 0 <= y <= y + height <= HEIGHT
        row = bytes(color) * width
        for yy in range(y, y + height):
            start = (yy * WIDTH + x) * 3
            self.pixels[start:start + len(row)] = row

    def text(self, x, y, text, scale=2, color=INK):
        assert x + text_width(text, scale) <= WIDTH
        assert y + 7 * scale <= HEIGHT
        for char in text.upper():
            for yy, row in enumerate(GLYPHS[char].split('/')):
                for xx, pixel in enumerate(row):
                    if pixel == '1':
                        self.rect(x + xx * scale, y + yy * scale,
                                  scale, scale, color)
            x += 5 * scale

    def paragraph(self, x, y, text, width, scale=2, color=INK):
        for line in wrap(text, width, scale):
            self.text(x, y, line, scale, color)
            y += 9 * scale
        return y

    def write_png(self, path):
        def chunk(kind, data):
            return (struct.pack('>I', len(data)) + kind + data
                    + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))

        rows = b''.join(b'\0' + self.pixels[y * WIDTH * 3:(y + 1) * WIDTH * 3]
                        for y in range(HEIGHT))
        header = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
        path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
                         + chunk(b'IDAT', zlib.compress(rows, 9))
                         + chunk(b'IEND', b''))


def draw_briefs(canvas):
    for index, (label, briefs) in enumerate(COLUMNS):
        x = 20 + index * 248
        assert x + 228 <= 1004
        canvas.rect(x, 380, 228, 22, INK)
        assert text_width(label) <= 220
        canvas.text(x + 4, 384, label, color=WHITE)
        y = 414
        for brief in briefs:
            lines = wrap(brief, 228)
            assert 1 <= len(lines) <= 2, brief
            bottom = y + (len(lines) - 1) * 18 + 14
            assert bottom <= min(940, DAY_BOARD_TOP - 16), brief
            for line in lines:
                assert x + text_width(line) <= x + 228
                canvas.text(x, y, line)
                y += 18
            # The last glyph row ends four pixels before the line advance.
            y = bottom + 10


def draw_day_board(canvas):
    bar_height = 70
    gap = 8
    padding = 10
    for index, text in enumerate(DAY_BOARD_ROWS):
        top = DAY_BOARD_TOP + index * (bar_height + gap)
        canvas.rect(20, top, 984, bar_height, INK)
        # Keep the supplied spacing on lines that fit; wrap longer rows.
        lines = [text] if text_width(text, 2) <= 984 - 2 * padding else wrap(
            text, 984 - 2 * padding, 2)
        text_height = (len(lines) - 1) * 18 + 14
        assert text_height <= bar_height - 2 * padding
        y = top + (bar_height - text_height) // 2
        for line in lines:
            canvas.text((WIDTH - text_width(line, 2)) // 2, y, line, 2, WHITE)
            y += 18


def main():
    canvas = Canvas()
    canvas.text(20, 18, 'THE DAILY WORLD / GLOBAL NEWS IN ONE PAGE', 2, RED)
    canvas.text(20, 49, 'THE WORLD', 16)
    canvas.rect(20, 176, 984, 3, INK)
    canvas.rect(20, 187, 984, 28, INK)
    canvas.text(30, 194, 'WEDNESDAY, 18 NOVEMBER 2026', 2, WHITE)
    canvas.text(734, 194, 'WORLD BRIEFING / NO. 1811', 2, WHITE)

    leads = [
        ('01 / EUROPE', 'WAR REACHES DEEPER',
         'KERCH BRIDGE HIT AGAIN AS UKRAINE REPORTS ITS BIGGEST DRONE RAID.'),
        ('02 / MIDDLE EAST', 'GULF ON ALERT',
         'BAHRAIN RADAR HIT. TANKER STRUCK IN HORMUZ; ALL 24 CREW SAFE.'),
        ('03 / ASIA', 'POWERS CONVERGE',
         'APEC OPENS IN SHENZHEN. TRUMP, XI AND PUTIN ARE SET TO MEET.'),
    ]
    for index, (label, headline, summary) in enumerate(leads):
        x = 20 + index * 334
        canvas.text(x, 231, label, 2, RED)
        end = canvas.paragraph(x, 257, headline, 316, 3)
        canvas.paragraph(x, end + 9, summary, 316, 1)
        canvas.rect(x, 350, 316, 2, INK)
    canvas.text(20, 362, 'THE WORLD IN BRIEF', 1, RED)
    draw_briefs(canvas)

    draw_day_board(canvas)
    canvas.text(20, 1001, 'THE WORLD / 18 NOVEMBER 2026', 1)
    canvas.text(654, 1001, 'FOUR REGIONS. FORTY BRIEFS. ONE WORLD.', 1)

    output = Path(os.environ.get('MAKEFUN_OUTPUT_DIR', 'out'))
    output.mkdir(parents=True, exist_ok=True)
    canvas.write_png(output / 'entry.png')


if __name__ == '__main__':
    main()
