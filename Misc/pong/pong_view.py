# Simple Pong Game View.

from tkinter import *
from tkinter import font
import time

from pong_settings import *

''' The View class handles everything to do with displaying the user interface to the user'''
class TkView(Frame):
    
    # Initialisation
    
    def __init__(self, controller, scale, root=None):
        self.controller = controller
        self.scale = scale
        self.init_gui(root)
        self.init_score()
        self.walls_view = []
        self.bars_view = []
        self.gameover_displayed = False
        self.waitfornet_displayed = False

    def init_gui(self, root):
        self.root = root
        if root == None:
            self.root = Tk()
            self.root.wm_title("Pong")
        self.canvas = Canvas(self.root, width=int(CANVAS_WIDTH*self.scale), height=int(CANVAS_HEIGHT*self.scale), bg="white")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=TRUE)
        self.canvas.create_line(int(self.scale*CANVAS_WIDTH/2), 0, int(self.scale*CANVAS_WIDTH/2), int(self.scale*CANVAS_HEIGHT), dash=(4, 2))
        self.init_fonts()
        self.root.bind('<Key>', self.key)
    
    def key(self,event):
        if event.char == 'q':
            self.controller.exit()
        elif event.char == 'r':
            self.controller.set_local_restart()
        elif event.char == 'k':
            self.controller.move_gui_player_bar(Direction.UP,is_local=True)
        elif event.char == 'm':
            self.controller.move_gui_player_bar(Direction.DOWN,is_local=True)       
        elif event.char == 'v':
            self.controller.add_view()

    def init_fonts(self):
        self.bigfont = font.nametofont("TkDefaultFont")
        self.bigfont.configure(size=int(48*self.scale))
        self.scorefont = font.nametofont("TkDefaultFont")
        self.scorefont.configure(size=int(20*self.scale))

    def init_score(self):
        self.score_text = self.canvas.create_text(self.scale*CANVAS_WIDTH/2, self.scale*CANVAS_HEIGHT/10, anchor="c")

    # Dynamic methods

    def register_ball(self, ball_model):
        self.ball_view = BallView(self.canvas, ball_model, self.scale)

    def register_wall(self, wall_model):
        wall_view = BarView(self.canvas, wall_model, self.scale)
        self.walls_view.append(wall_view)
        wall_view.draw(self.scale)

    def register_net(self, net_model):
        # don't need to visualize nets
        pass

    def register_bar(self, bar_model):
        self.bars_view.append(BarView(self.canvas, bar_model, self.scale))

    def display_score(self):
        self.canvas.itemconfig(self.score_text, text=self.controller.get_score_text(), font=self.scorefont, justify="center")

    def game_over(self):
        self.text = self.canvas.create_text(self.scale*CANVAS_WIDTH/2, self.scale*(CANVAS_HEIGHT/2-CANVAS_HEIGHT/9), anchor="c")
        self.canvas.itemconfig(self.text, text="NEW GAME", font=self.bigfont)
        self.text2 = self.canvas.create_text(self.scale*CANVAS_WIDTH/2, self.scale*(CANVAS_HEIGHT/2-CANVAS_HEIGHT/9) + CANVAS_HEIGHT/7, anchor="c")
        self.canvas.itemconfig(self.text2, text="Press r to play again.", font=self.scorefont)
        self.gameover_displayed = True

    def wait_for_remote_opponent(self):
        if self.gameover_displayed:
            self.canvas.itemconfig(self.text2, text="Waiting for network opponent...", font=self.scorefont)
            self.gameover_displayed = False
            self.waitfornet_displayed = True
 
    def clear_messages(self):
        if self.gameover_displayed or self.waitfornet_displayed:
            self.canvas.delete(self.text)
            self.canvas.delete(self.text2)
        self.update()

    def update(self):
        self.ball_view.redraw()
        for bar_view in self.bars_view:
            bar_view.redraw(self.scale)
        self.display_score()
        self.root.update()

    def destroy(self):
        self.root.destroy()
    
    
''' The BarView class has the task of displaying one bar '''
class BarView():
    def __init__(self, canvas, bar, scale):
        self.canvas = canvas
        self.bar = bar
        self.xpos = self.bar.get_xpos()
        self.ypos = self.bar.get_ypos()
        self.id_text = None
        self.main_rect = None
        self.draw(scale)
        
    ''' draw the bar '''
    def draw(self, scale):
        height = scale*self.bar.get_height()
        width = scale*self.bar.get_width()
        xpos = scale*self.bar.get_xpos()
        ypos = scale*self.bar.get_ypos()
        canvas_height = scale*CANVAS_HEIGHT
        self.main_rect = self.canvas.create_rectangle(xpos - width/2, ypos - height/2, xpos + width/2, ypos + height/2, fill=self.bar.color)
        if self.bar.get_id() != None and self.bar.get_id() != -1:
            self.id_text = self.canvas.create_text(xpos, ypos)
            idfont = font.nametofont("TkDefaultFont")
            idfont.configure(size=int(20*scale))
            self.canvas.itemconfig(self.id_text, text=self.bar.get_id(), font=idfont, fill="white")
        self.drawn = True

    ''' move the bar '''
    def redraw(self,scale):
        deltax = self.bar.get_xpos() - self.xpos
        deltay = self.bar.get_ypos() - self.ypos
        if self.drawn:
            self.canvas.move(self.main_rect, scale*deltax, scale*deltay)
            if self.id_text != None:
                self.canvas.move(self.id_text, scale*deltax, scale*deltay)
            self.xpos = self.bar.get_xpos()
            self.ypos = self.bar.get_ypos()

''' The BallView class has the task of displaying the ball '''
class BallView():
    def __init__(self, canvas, ball_model, scale):
        self.ball_model = ball_model
        self.points = [-self.ball_model.get_size()/2,-self.ball_model.get_size()/2,self.ball_model.get_size()/2,self.ball_model.get_size()/2]
        self.curr_x = 0
        self.curr_y = 0
        self.canvas = canvas
        self.scale = scale
        self.draw()

    ''' draw the ball at its current position '''
    def draw(self):
        scaled_points = [i * self.scale for i in self.points]
        self.polygon = self.canvas.create_oval(*scaled_points, fill="black")
        self.drawn = True

    ''' move the ball '''
    def redraw(self):
        if self.drawn:
            deltax = self.ball_model.get_position().getX() - self.curr_x
            deltay = self.ball_model.get_position().getY() - self.curr_y
            self.canvas.move(self.polygon, self.scale*deltax, self.scale*deltay)
            self.curr_x = self.ball_model.get_position().getX()
            self.curr_y = self.ball_model.get_position().getY()



