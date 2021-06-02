'''Module holding constants used to format lines that are printed to the
terminal.
'''

import os
import sys


def color_enabled():
    COLOR_ENV = os.getenv('COLOR', 'auto')
    if COLOR_ENV == 'auto' and sys.stdout.isatty():
        return True
    if COLOR_ENV == 'yes':
        return True
    return False


try:
    import colorama

    colorama.init(strip=not color_enabled())
    GREEN, YELLOW, RED = (
        colorama.Fore.GREEN,
        colorama.Fore.YELLOW,
        colorama.Fore.RED,
    )
    MAGENTA, CYAN, WHITE = (
        colorama.Fore.MAGENTA,
        colorama.Fore.CYAN,
        colorama.Fore.WHITE,
    )
    BRIGHT, RESET = colorama.Style.BRIGHT, colorama.Style.RESET_ALL
except ImportError:  # pragma: no cover
    # No colorama, so let's fallback to no-color mode
    GREEN = YELLOW = RED = MAGENTA = CYAN = WHITE = BRIGHT = RESET = ''

RANKS_COLORS = {
    'A': GREEN,
    'B': GREEN,
    'C': YELLOW,
    'D': YELLOW,
    'E': RED,
    'F': RED,
}

LETTERS_COLORS = {'F': MAGENTA, 'C': CYAN, 'M': WHITE}

MI_RANKS = {'A': GREEN, 'B': YELLOW, 'C': RED}
TEMPLATE = '{0}{1} {reset}{2}:{3} {4} - {5}{6}{reset}'
