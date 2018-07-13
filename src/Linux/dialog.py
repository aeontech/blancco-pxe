import curses
import textwrap
from math import ceil

def _display(stdscr, title, desc, options):
    if not options:
        raise ValueError('You did not provide any choices to the dialog')

    chosen = 0
    choosing = True

    curses.start_color()
    curses.curs_set(0)

    if not curses.has_colors():
        raise RuntimeError('Color not support by curses!')

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLUE)        # Backdrop
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Popup
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)       # Choices
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)      # OK inactive
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # OK active

    # The width will always be 50
    width = 50

    # Break the description into intended lines
    desc = desc.split('\n')
    # Wrap the lines by length
    desc = [textwrap.wrap(i, width - 2) for i in desc]
    # And flatten the 2D list into a 1D list
    desc = [x for y in desc for x in y]

    # Calculate the height of the popup
    height = 8 + (len(desc) if desc else -1) + len(options)

    # Calculate the size of the terminal
    t_height,t_width = stdscr.getmaxyx()

    # Add backdrop color
    stdscr.keypad(1)
    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.refresh()

    baseH = (t_height/2) + int(ceil(float(height)/2))
    baseW = (t_width/2) - (width/2)
    window = curses.newwin(height, width, baseH-height, baseW)
    window.bkgd(' ', curses.color_pair(2))
    window.addstr(title[:50].center(width, ' '), curses.A_REVERSE)
    # Output description, line by line
    for i in range(len(desc)):
        window.addstr(i+2, 1, desc[i])
    window.refresh()

    opL = len(options)
    choices = curses.newwin(opL + 2, width - 4, baseH - opL - 5, baseW + 2)
    choices.bkgd(' ', curses.color_pair(3))

    submit = curses.newwin(1, 8, baseH - 2, baseW + width - 10)
    submit.bkgd(' ', curses.color_pair(4))
    submit.addstr("   OK ")

    while True:
        # Write choices strings out
        for i in range(len(options)):
            if chosen == i:
                choices.addstr(i+1, 0, (" [X] %s" % options[i]).ljust(width-4), \
                    (curses.A_REVERSE if choosing else 0))
            else:
                choices.addstr(i+1, 0, (" [ ] %s" % options[i]).ljust(width-4))

        # Toggle between OK button and choices
        if choosing:
            submit.bkgd(' ', curses.color_pair(4))
        else:
            submit.bkgd(' ', curses.color_pair(5))

        # Draw interface changes
        choices.refresh()
        submit.refresh()

        # Get keypress
        ch = stdscr.getch()

        if ch == curses.KEY_DOWN and choosing:
            chosen = min(len(options) - 1, chosen + 1)
        elif ch == curses.KEY_UP and choosing:
            chosen = max(0, chosen - 1)
        elif ch == ord('\t'):
            choosing = not choosing
        elif ch == ord('\n') and not choosing:
            break

    return chosen

def dialog(title, desc, choices):
    return curses.wrapper(_display, title, desc, choices)
