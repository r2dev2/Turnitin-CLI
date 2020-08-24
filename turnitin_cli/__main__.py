import curses
from curses.textpad import Textbox, rectangle
import os
import sys

from turnitin_cli.core import login, get_courses, get_assignments, submit, download, parser

up = parser["keybindings"]["menu_up"]
down = parser["keybindings"]["menu_down"]

width, height = os.get_terminal_size()


def log(*msg):
    if "--debug" in sys.argv:
        with open("log", 'a+') as fout:
            print(*msg, file=fout, flush=True)


class Menu:
    def __init__(self, options, previous=exit):
        self.width, self.height = width, height
        self.vnum = self.height // 2
        self.amount = len(options)
        self.options = options
        newamount = 0
        if self.amount % (self.vnum+1) != 0:
            newamount = (self.vnum+1)-self.amount%(self.vnum+1)
            self.options.extend(['']*newamount)
        self.pw = (self.amount+newamount)*2
        self.py = 1000
        self.scr = curses.newpad(self.pw, self.py)
        self.to_remove = None
        self.in_focus = 0
        self.update_scr()
        self.current_frame = Frame(0, self.vnum, self.vnum)

        self.actions = {
            down: self.move_down,
            up: self.move_up,
            'b': previous,
            parser["keybindings"]["quit"]: exit
        }

    def clear(self):
        self.scr.clear()

    def refresh(self):
        num = 2*self.in_focus
        if num/2 in self.current_frame:
            num = 0
        else:
            self.current_frame = self.current_frame.next(num/2)
            log("Changing frame")
        log(self.pw, self.py, self.width, self.height)
        self.scr.refresh(self.current_frame.beg*2, 0, 0, 0, self.height-1, self.width-1)

    def move_up(self):
        self.to_remove = self.in_focus
        self.in_focus -= 1
        if self.in_focus < 0:
            self.in_focus = 0
            self.to_remove = None
        self.update_scr()

    def move_down(self):
        self.to_remove = self.in_focus
        self.in_focus += 1
        if self.in_focus >= self.amount:
            self.in_focus = self.amount - 1
            self.to_remove = None
        self.update_scr()
    
    def display(self):
        self.init_scr()
        k = None
        while k != '\n':
            self.refresh()
            k = self.scr.getkey()
            try:
                self.actions[repr(k)[1:-1]]()
            except KeyError:
                log(repr(k)[1:-1], "not found") 
        return self.in_focus
            

    def init_scr(self):
        self.clear()
        for i, option in enumerate(self.options):
            if i == self.in_focus:
                self.scr.addstr(2*i, 0, str(option), curses.A_STANDOUT)
            else:
                self.scr.addstr(2*i, 0, str(option))

    def update_scr(self):
        i = self.in_focus
        j = self.to_remove
        self.scr.addstr(2*i, 0, str(self.options[i]), curses.A_STANDOUT)
        if j is not None:
            self.scr.addstr(2*j, 0, str(self.options[j]))

class Frame:
    def __init__(self, beg, end, delta):
        self.beg = beg
        self.end = end
        self.delta = delta

    def forward(self):
        return Frame(self.beg+self.delta, self.end+self.delta, self.delta)

    def previous(self):
        return Frame(self.beg-self.delta, self.end-self.delta, self.delta)

    def next(self, other):
        if other > self.end:
            return self.forward()
        return self.previous()

    def __contains__(self, other):
        return self.beg <= other <= self.end

class Represent:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def __str__(self):
        return NotImplemented

    def __repr__(self):
        return str(self)

class Course(Represent):
    def __str__(self):
        return self.value["title"]

class Assignment(Represent):
    def __str__(self):
        v = self.value
        return (f'{expand_string(v["title"], width-50)}  Due: {v["dates"]["due"][:-3]:5}  '
                f'Completed: {v["submission"]=="javascript:void(0);"}')


def expand_string(s1, target_length):
    """
    Adds whitespace to a string until it is a target length.

    :param s1: the original string
    :param target_length: the length to which the string should be
    :returns: the string with applied whitespace
    """
    string_length = len(s1)
    if string_length > target_length:
        return s1[:target_length]
    whitespace_to_add = (target_length-string_length)*' '
    return s1 + whitespace_to_add

def user_course(auth):
    courses = get_courses(auth)
    course_menu = Menu([Course(c) for c in courses])
    course = courses[course_menu.display()]
    return course

def user_assignments(auth, course):
    assignments = get_assignments(auth, course)
    assignment_menu = Menu([Assignment(a) for a in assignments])
    assignment = assignments[assignment_menu.display()]
    return assignment

def user_download(auth, assignment, stdscr, additional='Enter file name to save to'):
    stdscr.clear()
    stdscr.addstr(0, 0, f"{additional}: (hit ctrl-g to finish)")

    editwin = curses.newwin(5, 30, 2, 1)
    rectangle(stdscr, 1, 0, 1+5+1, 1+30+1)
    stdscr.refresh()

    box = Textbox(editwin)

    box.edit()
    message = box.gather().rstrip()
    log(message)
    try:
        open(message, 'wb+').close()
    except:
        return user_download(auth, assignment, stdscr, "Please enter a valid filename")
    download(auth, assignment, message)

def user_submit(auth, assignment, stdscr, contents=''):
    stdscr.clear()
    stdscr.addstr(0, 0, "Which file to submit: (hit ctrl-g to finish)")

    editwin = curses.newwin(5, 30, 2, 1)
    rectangle(stdscr, 1, 0, 1+5+1, 1+30+1)
    stdscr.addstr(1+5+2, 0, contents)
    stdscr.refresh()

    box = Textbox(editwin)

    box.edit()
    message = box.gather().rstrip()
    if message.startswith("!ls"):
        try:
            contents = repr(os.listdir(message[4:]))
        except:
            contents = ''
    try:
        open(message, 'rb').close()
    except:
        return user_submit(auth, assignment, stdscr, contents)

    stdscr.clear()
    stdscr.addstr(0, 0, "What should the submission be titled? (hit ctrl-g to finish)")
    editwin = curses.newwin(5, 30, 2, 1)
    rectangle(stdscr, 1, 0, 1+5+1, 1+30+1)
    stdscr.refresh()

    box = Textbox(editwin)
    box.edit()

    submit(auth, assignment, message, box.gather().rstrip())


def main(stdscr):
    try:
        stdscr.addstr(0, 0, "Logging in...")
        stdscr.refresh()
        auth = login()

        stdscr.clear()
        stdscr.addstr(0, 0, "Getting courses...")
        stdscr.refresh()
        course = user_course(auth)

        stdscr.clear()
        stdscr.addstr(0, 0, "Getting assignments...")
        stdscr.refresh()
        assignment = user_assignments(auth, course)

        if assignment["submission"] == "javascript:void(0);":
            user_download(auth, assignment, stdscr)
        else:
            user_submit(auth, assignment, stdscr)

        stdscr.clear()
        stdscr.addstr(0, 0, "Finished operation")
        stdscr.refresh()
        stdscr.getkey()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)

