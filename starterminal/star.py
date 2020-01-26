# Draws 'random stars' in the terminal
#  A star is a dot
#  Random means blinking, color

import sys
import time
import subprocess
import itertools
from collections import namedtuple
import random
# Just using for making the code less ambiguous (in my case)
from typing import Type
from enum import Enum

# User settings
# ------------
# Total number of stars to draw
nstars = 40
# Letting program loop allows more granular control over blinking star speed
# If set to false, only use bash escape sequences to keep blinking some stars
allow_loop = True
# Sleep seconds (fastest possible star change)
ticker_time = 0.1
# ------------

class ANSI:
    class Control:
        clear = '\033[2J'
        move = '\033[{};{}H'
        slowblink = '\033[5m'
        reset = '\033[m'
        bold = '\033[1m'
        faint = '\033[2m'
        normal = '\033[22m'
        conceal = '\033[8m'

    class Colors:
        """Only colors allowed as public variables, otherwise get_all will break"""
        black = '\033[30m'
        red = '\033[30m'
        green = '\033[30m'
        yellow = '\033[30m'
        blue = '\033[30m'
        magenta = '\033[30m'
        cyan = '\033[30m'
        white = '\033[30m'
        b_red = '\033[91m'
        b_green = '\033[92m'
        b_yellow = '\033[93m'
        b_blue = '\033[94m'
        b_magenta = '\033[95m'
        b_cyan = '\033[96m'
        b_white = '\033[97m'

        space_set = [red, yellow, blue, white, cyan, b_red, b_yellow]

        @classmethod
        def random(cls):
            """Returns a random color"""
            #colors = cls.get_all()
            colors = cls.space_set
            a_color = int(random.random()*len(colors))
            return colors[a_color]

        @classmethod
        def get_all(cls):
            """
            Weakly returns all color class variables
            It: 
                * filters variables that doesn't start with _
                * filters variables that are strs
            """
            return [v for k, v in cls.__dict__.items() 
                        if not k.startswith('_') and type(v) is str]

# Statically find window columns and rows
#  - if user resizes screen this no new stars will be drawn...
cp = subprocess.run(['stty', 'size'], capture_output=True, check=True)
W_COLS, W_ROWS = map(int, cp.stdout.split())

# Exclusively used for stars
Coord2D = namedtuple('Coord2D', ['c', 'r'])
class BlinkType(Enum):
    OFF = 0
    BASH = 1
    RANDOM = 2
    RANDOM_COLOR_ONLY = 3
    RANDOM_FREQ_ONLY = 4

    @classmethod
    def random(cls, bash_only=True):
        if bash_only:
            return random.choice([cls.OFF, cls.BASH])
        # Excluding bash binking
        return random.choice([
                cls.OFF, 
                cls.RANDOM, 
                cls.RANDOM_COLOR_ONLY, 
                cls.RANDOM_FREQ_ONLY])

class BlinkSpeed:
    """Fastest possible blink speed is controlled via overall redraw delay.
    1 - n corresponds to the number of ticks before it changes.
    1 is fastest.
    """
    SPEEDS = range(1, 6)

    @classmethod
    def random(cls):
        return random.choice(cls.SPEEDS)

class Intensity(Enum):
    OFF = ANSI.Control.conceal
    FAINT = ANSI.Control.faint
    NORMAL = ANSI.Control.normal
    BOLD = ANSI.Control.bold

    @classmethod
    def cycler(cls, init_val:Type[str]=None):
        """Returns a generator for infinite 'staircase' cycling 
            allowing a custom start initial value"""
        cycler = itertools.cycle([
            cls.OFF, 
            cls.FAINT, 
            cls.NORMAL, 
            cls.BOLD, 
            cls.NORMAL,
            cls.FAINT
            ])
        # Always start from FAINT if init val is not specified, else 
        #   cycle till hit init_val
        if init_val != None:
            while True:
                if next(cycler) == Intensity(init_val):
                    break
        return cycler

    @classmethod
    def random(cls):
        """Return a random member from the enumeration values"""
        return random.choice([v.value for v in cls.__members__.values()])

class Clock:
    """To keep track of which global tick the program is at"""
    ticker = 1

    @classmethod
    def tick(cls):
        cls.ticker += 1


class Star:
    """A bash dot represented by color, terminal row and column, blinking etc..."""
    coord: Type[Coord2D] = None
    color: str = None
    blink: int = BlinkType.OFF
    # Keep track of both generator and current intensity state
    intensity: str = None
    intensity_cycler: Type[itertools.cycle] = None
    # See BlinkSpeed
    blink_freq = 0
    # So everything doesn't blink at the same time, depends on blink_freq
    blink_offset = 0
    bash_blink_only = True

    def __init__(self):
        pass

    @staticmethod
    def init_random(custom_blink=False):
        """Initialize all star settings to something random
        custom_blink=False implies bash blinking only
        """
        self = Star()
        self.set_rand_coord()
        self.set_rand_color()
        self.set_rand_intensity()
        self.bash_blink_only = not custom_blink
        self.set_rand_blink()
        return self
        
    def set_rand_coord(self):
        c = int(random.random()*W_COLS)
        r = int(random.random()*W_ROWS)
        self.coord = Coord2D(c, r)

    def set_rand_color(self):
        self.color = ANSI.Colors.random()

    def set_rand_intensity(self):
        init_val = Intensity.random()
        self.intensity_cycler = Intensity.cycler(init_val)
        self.intensity = init_val

    def set_next_intensity(self):
        self.intensity = next(self.intensity_cycler).value

    def set_rand_blink(self):
        self.blink = BlinkType.random(bash_only=self.bash_blink_only)
        # Always set random blink seed (even if not used)
        self.blink_freq = BlinkSpeed.random()
        # Start blink offset should never be bigger than freq (to avoid unnatural waits)
        self.blink_offset = random.choice(range(self.blink_freq))

    def update_star_via_blink(self):
        """Update stars depending on blink settings"""
        #import pdb; pdb.set_trace()

        # No updates if blink is off
        if self.blink == BlinkType.OFF:
            return

        # If global clock matches the blink frequency, go to next state
        if (Clock.ticker + self.blink_offset) % self.blink_freq == 0:
            #self.set_rand_color()
            # Stairtype i,ii,iii,ii,i,ii,iii,ii...
            self.set_next_intensity()

    @property
    def draw(self):
        sequence = ''

        # If only using ANSI sequences, add to sequence, else update star
        if self.bash_blink_only:
            # Can either be on or off
            if self.blink == BlinkType.BASH:
                sequence += ANSI.Control.slowblink
        else:
            self.update_star_via_blink()

        # Move cursor to draw location
        sequence += ANSI.Control.move.format(self.coord.c, self.coord.r)
        sequence += self.color
        sequence += self.intensity

        # Add the 'star'
        # Unfortunate hack following: 
        #  since most terminals don't allow 'conceal' ->
        #  manually check for state and either draw star or space
        if self.intensity == Intensity.OFF.value:
            sequence += '\x20'
        else:
            sequence += '.'

        # This is not strictly necessary to do here
        #  but avoiding pre-mature optimization
        sequence += ANSI.Control.reset

        sys.stdout.write(sequence)
        sys.stdout.flush()

def window_setup():
    """Clear screen and move cursor to upper corner"""
    sys.stdout.write(ANSI.Control.move.format(0, 0))
    sys.stdout.write(ANSI.Control.clear)
    sys.stdout.flush()

def window_clean():
    """Reset style and move cursor to final row"""
    sys.stdout.write(ANSI.Control.reset)
    sys.stdout.write(ANSI.Control.move.format(W_COLS, 1))
    sys.stdout.flush()

def draw(stars):
    for s in stars:
        s.draw
        


window_setup()
stars = [Star.init_random(custom_blink=allow_loop) for _ in range(nstars)]

if allow_loop:
    while True:
        draw(stars)
        window_clean()
        time.sleep(ticker_time)
        Clock.tick()
else:
    # Draw stars once for bash
    draw(stars)

window_clean()
