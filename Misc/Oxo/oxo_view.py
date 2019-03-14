# Simple Frogger Game.  Mark Handley, UCL, 2018

from tkinter import *
from tkinter.font import Font
import time
from oxo_settings import CANVAS_SIZE

class View(Frame):
    def __init__(self, controller, root):
        self.controller = controller
        root.wm_title("OXO")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        self.canvas = Canvas(self.frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=FALSE)
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.init_fonts()
        self.init_board()
        self.pieces = []
        self.thinking_tags = []
        self.last_move = 0
        self.is_thinking = False
        self.paused = False
        #self.draw_move("X", 0, 0)
        #self.draw_move("O", 2, 1)

    def init_board(self):
        self.margin = CANVAS_SIZE//10
        board_width = CANVAS_SIZE - 2 * self.margin
        self.square_size = board_width // 3
        self.canvas.create_line(self.margin, self.square_size + self.margin, board_width + self.margin, self.square_size + self.margin, fill="darkblue")
        self.canvas.create_line(self.margin, 2 * self.square_size + self.margin, board_width + self.margin, 2 * self.square_size + self.margin, fill="darkblue")
        self.canvas.create_line(self.square_size + self.margin, self.margin, self.square_size + self.margin, board_width + self.margin, fill="darkblue")
        self.canvas.create_line(2 * self.square_size + self.margin, self.margin, 2 * self.square_size + self.margin, board_width + self.margin, fill="darkblue")

    def clear_board(self):
        for piece in self.pieces:
            self.canvas.delete(piece)
        self.pieces.clear()

    def init_fonts(self):
        self.bigfont = Font(family="TkDefaultFont", size=90)
        self.smallfont = Font(family="TkDefaultFont", size=16)
        self.tinyfont = Font(family="TkDefaultFont", size=12)

    def map_coords(self, x, y):
        nx = (x + 0.5)*self.square_size + self.margin
        ny = (y + 0.5)*self.square_size + self.margin
        return nx,ny

    def draw_move(self, char, x, y):
        nx,ny = self.map_coords(x,y)
        text = self.canvas.create_text(nx, ny, anchor="c")
        self.canvas.itemconfig(text, text=char, font=self.bigfont, fill="black")
        self.pieces.append(text)
        self.last_move = time.time()
        if char == "X":
            self.clear_thinking()
        self.is_thinking = False

    def win(self, winning_line):
        x1,y1 = winning_line[0]
        nx1,ny1 = self.map_coords(x1,y1)
        x2,y2 = winning_line[2]
        nx2,ny2 = self.map_coords(x2,y2)
        line = self.canvas.create_line(nx1,ny1, nx2,ny2, fill="blue", width=3)
        self.pieces.append(line)

    def thinking(self, msg, msg2, x, y):
        nx,ny = self.map_coords(x,y)
        msgtag = self.canvas.create_text(nx, ny, anchor="c")
        self.canvas.itemconfig(msgtag, text=msg, font=self.smallfont, fill="red")
        self.thinking_tags.append(msgtag)
        msgtag = self.canvas.create_text(nx, ny+15, anchor="c")
        self.canvas.itemconfig(msgtag, text=msg2, font=self.tinyfont, fill="red")
        self.thinking_tags.append(msgtag)
        self.is_thinking = True

    def clear_moves(self):
        for piece in self.pieces:
            self.canvas.delete(piece)

    def clear_thinking(self):
        for tag in self.thinking_tags:
            self.canvas.delete(tag)
        self.thinking_tags.clear()

    def mouse_click(self, event):
        x = (event.x - self.margin)//self.square_size
        y = (event.y - self.margin)//self.square_size
        if x < 0 or x > 2 or y < 0 or y > 2:
            return
        self.controller.click(x, y)

    def pause(self, state):
        if state:
            self.paused = True
        else:
            self.paused = False
            self.clear_thinking()

    def update(self):
        if (not self.is_thinking) and len(self.thinking_tags) > 0 \
           and time.time() - self.last_move > 5 and (not self.paused):
            self.clear_thinking()
        self.frame.update()

