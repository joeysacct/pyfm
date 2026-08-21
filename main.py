import curses
from fm import run_fm

def main(stdcsr):
    curses.curs_set(0) # hide cursor NOTE needed?
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_BLUE, -1)
    curses.init_pair(2,curses.COLOR_CYAN, -1)
    curses.init_pair(3,curses.COLOR_GREEN, -1)
    curses.init_pair(4,curses.COLOR_MAGENTA, -1)
    curses.init_pair(5,curses.COLOR_RED, -1)
    curses.init_pair(6,curses.COLOR_WHITE, -1)
    curses.init_pair(7,curses.COLOR_YELLOW, -1)

    stdcsr.nodelay(True) # non-blocking input

    run_fm(stdcsr)

if __name__ == "__main__":
    curses.wrapper(main)
