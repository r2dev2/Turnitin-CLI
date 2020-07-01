import configparser
import curses

p = configparser.ConfigParser()
p.read("config.ini")
print(p["keybindings"]["menu_up"], p["keybindings"]["menu_down"], p["keybindings"]["quit"])
input()

def main(stdscr):
    try:
        k = None
        while k != 'q':
            k = stdscr.getkey()
            if repr(k)[1:-1] == p["keybindings"]["menu_up"]:
                stdscr.addstr('hi')
            stdscr.refresh()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)

