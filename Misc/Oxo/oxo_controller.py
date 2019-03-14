#Dumb Noughts and Crosses Game.  Mark Handley, UCL, 2018
from tkinter import *
from oxo_view import View
from oxo_model import Model

class Controller():
    def __init__(self):
        self.root = Tk();
        self.windowsystem = self.root.call('tk', 'windowingsystem')
        self.root.bind_all('<Key>', self.key)
        self.view = View(self, self.root)
        self.model = Model(self)
        self.play_game = True

    def key(self, event):
        if event.char >= '1' and event.char <= '9':
            pos = ord(event.char) - ord('1')
            x = pos % 3
            y = pos // 3
            self.model.x_plays(x, y)
        elif event.char == 'q':
            self.play_game = False
        elif event.char == 'p':
            self.view.pause(True)
        elif event.char == 'u':
            self.view.pause(False)


    def click(self, x, y):
        print("click", x, y)
        self.model.x_plays(x, y)

    def clear_board(self):
        self.view.clear_board()

    def display_move(self, char, x, y):
        self.view.draw_move(char, x, y)
        self.root.update()

    def win(self, winning_line):
        self.view.win(winning_line);
        self.root.update()

    def thinking(self, msg, msg2, x, y):
        self.view.thinking(msg, msg2, x, y)
        self.root.update()

    def run(self):
        while self.play_game:
            self.view.update()
            self.root.update()
