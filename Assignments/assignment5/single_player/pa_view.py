# Simple Frogger Game.  Mark Handley, UCL, 2018

from tkinter import *
from tkinter import font
import time
from pa_settings import CANVAS_WIDTH, CANVAS_HEIGHT, GRID_SIZE, Direction
from pa_audio import Audio
from pa_model import GhostMode

L_OFF = 50
T_OFF = 50

'''GameObjectView is a generic view of a game object.  All it does is
   handle moving of the object - it just saves replicating this code into
   PacmanView, GhostView, etc.  Everything else needs to be handled by the
   subclasses themselves.'''

class GameObjectView():
    def __init__(self, canvas):
        self.canvas = canvas
        self.items = []
        self.x = 0
        self.y = 0

    def moveto(self, x, y):
        for item in self.items:
            self.canvas.move(item, x - self.x, y - self.y)
        self.x = x
        self.y = y

    def cleanup(self):
        for item in self.items:
            self.canvas.delete(item)

    
class PacmanView(GameObjectView):
    def __init__(self, canvas, pacman, pngs, dying_pngs):
        GameObjectView.__init__(self, canvas)
        self.pacman = pacman
        self.pngs = [[],[],[],[]]
        self.dying_pngs = dying_pngs
        self.pngs[Direction.LEFT] = pngs
        self.pointing_direction = Direction.LEFT

        # rotate the image to create a PacMan facing each direction
        prevlist = pngs
        for dir in [Direction.UP, Direction.RIGHT, Direction.DOWN]:
            pnglist = []
            for image in prevlist:
                newimage = self.rotate_image(image, Direction.RIGHT)
                pnglist.append(newimage)
            self.pngs[dir] = pnglist
            prevlist = pnglist
            
        self.pngnum = 0
        self.pngcounter = 0
        self.last_change = 0
        self.dying = False
        self.draw()

    def rotate_image(self, img, dir):
        w, h = img.width(), img.height()
        if dir in [Direction.LEFT, Direction.RIGHT]:
            newimg = PhotoImage(width=h, height=w)
        else: # 180 degree
            newimg = PhotoImage(width=w, height=h)
        for x in range(w):
            for y in range(h):
                rgb = '#%02x%02x%02x' % img.get(x, y)
                if dir == Direction.RIGHT: # 90 degrees
                    newimg.put(rgb, (h-y,x))
                elif dir == Direction.LEFT: # -90 or 270 degrees
                    newimg.put(rgb, (y,w-x))
                else: # 180 degrees
                    newimg.put(rgb, (w-x,h-y))
        return newimg

    def draw(self):
        if self.dying:
            if self.pngnum >= len(self.dying_pngs):
                return
            x, y = self.pacman.position
            image = self.canvas.create_image(L_OFF + x, T_OFF + y, image=self.dying_pngs[self.pngnum], anchor="c")
            self.items.append(image)
        else:
            x, y = self.pacman.position
            self.moveto(0, 0)
            d = self.pointing_direction
            image = self.canvas.create_image(L_OFF, T_OFF, image=self.pngs[d][self.pngnum], anchor="c")
            self.items.append(image)
            self.moveto(x, y)

    def redraw(self, time_now):
        if time_now - self.last_change > 0.1:
            self.last_change = time_now
            self.next_png()
            self.cleanup()
            self.draw()
        else:
            x, y = self.pacman.position
            self.moveto(x, y)

    def next_png(self):
        if self.dying:
            self.pngnum = self.pngnum + 1
            return
        if self.pacman.speed == 0:
            # Pacman stops with his mouth open
            self.pngnum = 2
        else:
            self.pngcounter = (self.pngcounter + 1) % 4
            self.pngnum = self.pngcounter
            if self.pngcounter == 3:
                self.pngnum = 1
            self.pointing_direction = self.pacman.direction

    def died(self):
        self.pointing_direction = Direction.UP
        self.pngcounter = 2
        self.pngnum = -1
        self.dying = True
        self.last_change = 0
        self.redraw(time.time())
            
class DummyPacman():
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.direction = Direction.LEFT

    @property
    def position(self):
        return (self.__x, self.__y)
    

class GhostView(GameObjectView):
    def __init__(self, canvas, ghost, pngs, eyes_pngs, scared_pngs):
        GameObjectView.__init__(self, canvas)
        self.ghost = ghost
        self.pngs = pngs
        self.eyes_pngs = eyes_pngs
        self.scared_pngs = scared_pngs
        self.pngnum = 0
        self.prev_direction = Direction.LEFT
        self.prev_mode = self.ghost.mode
        self.draw()

    def draw(self):
        x,y = self.ghost.position
        self.moveto(0, 0)
        if self.ghost.mode == GhostMode.CHASE:
            png = self.pngs[self.ghost.direction]
        elif self.ghost.mode == GhostMode.FRIGHTEN:
            if self.ghost.frighten_ending:
                png = self.scared_pngs[1]
            else:
                png = self.scared_pngs[0]
        elif self.ghost.mode == GhostMode.EYES:
            png = self.eyes_pngs[self.ghost.direction]
        image = self.canvas.create_image(L_OFF, T_OFF, image=png, anchor="c")
        self.items.append(image)
        self.moveto(x, y)
        self.prev_mode = self.ghost.mode

    def redraw(self, time_now):
        if self.ghost.direction == self.prev_direction \
           and self.ghost.mode == self.prev_mode:
            x, y = self.ghost.position
            self.moveto(x, y)
        else:
            self.cleanup()
            self.draw()
            self.prev_direction = self.ghost.direction

class Food():
    def __init__(self, canvas, coords, food_png):
        x, y = coords  # x and y coords in grid squares, not pixels
        self.canvas = canvas
        self.x = L_OFF + x * GRID_SIZE
        self.y = T_OFF + y * GRID_SIZE
        self.image = self.canvas.create_image(self.x, self.y, image=food_png, anchor="c")

    def eat(self):
        self.canvas.delete(self.image)

    def cleanup(self):
        self.eat()
            
class View(Frame):
    def __init__(self, root, controller):
        self.controller = controller
        root.wm_title("PacMan")
        self.windowsystem = root.call('tk', 'windowingsystem')
        self.frame = root
        self.canvas = Canvas(self.frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black")
        self.canvas.pack(side = LEFT, fill=BOTH, expand=FALSE)
        self.init_fonts()
        self.init_score()
        self.messages_displayed = False
        self.lives = 0
        self.lives_pacmen = []
        self.ghost_views = []
        self.pacman_views = []
        self.food = {}  # we use a dict to store food, indexed by grid coordinates
        self.powerpills = {} # also a dict
        self.audio = Audio()

        #Load all the images from files
        self.pacman_pngs = []
        for i in range(0, 3):
            self.pacman_pngs.append(PhotoImage(file = './assets/pacman' + str(i) + '.gif').zoom(2))
        self.pacman_dying_pngs = []
        for i in range(1, 11):
            self.pacman_dying_pngs.append(PhotoImage(file = './assets/pacman_dying' + str(i) + '.gif').zoom(2))
        self.ghost_left_pngs = []
        for i in range(0, 4):
            self.ghost_left_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + '.gif').zoom(2))
        self.ghost_up_pngs = []
        for i in range(0, 4):
            self.ghost_up_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'up.gif').zoom(2))
        self.ghost_down_pngs = []
        for i in range(0, 4):
            self.ghost_down_pngs.append(PhotoImage(file = './assets/ghost' + str(i) + 'down.gif').zoom(2))
        self.ghost_scared_pngs = []
        self.ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscared.gif').zoom(2))
        self.ghost_scared_pngs.append(PhotoImage(file = './assets/ghostscaredending.gif').zoom(2))
        self.ghost_eyes_pngs = []
        for i in range(0,4):
            self.ghost_eyes_pngs.append(PhotoImage(file = './assets/eyes' + str(i) + '.gif').zoom(2))
            
        self.food_png = PhotoImage(file = './assets/food.gif').zoom(2)
        self.powerpill_png = PhotoImage(file = './assets/powerpill.gif').zoom(2)

    def init_fonts(self):
        self.bigfont = font.nametofont("TkDefaultFont")
        self.bigfont.configure(size=48)
        self.scorefont = font.nametofont("TkDefaultFont")
        self.scorefont.configure(size=20)

    def init_score(self):
        self.score_text = self.canvas.create_text(5, 5, anchor="nw")
        self.canvas.itemconfig(self.score_text, text="Score:", font=self.scorefont, fill="white")

    def update_maze(self, maze):
        s = ""
        y = 0
        for row in maze:
            for x in range(0, len(row)//3):
                c = row[x*3:(x+1)*3]
                sx = x + 0.5  # x and y give the middle of the square,
                              # so sx, sy give the top left corner
                sy = y - 0.5
                if c == " /-":
                    tag = self.canvas.create_arc(L_OFF + x * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + (x+1) * GRID_SIZE,
                                                  T_OFF + (y+1) * GRID_SIZE,
                                                  start=90, extent=90, style=ARC, width=2,
                                                  outline = "blue")
                    s += " /-"
                elif c == "-/ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * GRID_SIZE,
                                                  T_OFF + (y-1) * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  start=270, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-/ "
                elif c == "---":
                    tag = self.canvas.create_line(L_OFF + (x-0.5) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + (x+0.5) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  width = 2, fill= "blue")
                    s += "---"
                elif c == "-\\ ":
                    tag = self.canvas.create_arc(L_OFF + (x-1) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y+1) * GRID_SIZE,
                                                  start=0, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += "-\\ "
                elif c == " \\-":
                    tag = self.canvas.create_arc(L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y-1) * GRID_SIZE,
                                                  L_OFF + (x+1) * GRID_SIZE,
                                                  T_OFF + y * GRID_SIZE,
                                                  start=180, extent=90, style=ARC, width=2,
                                                  outline= "blue")
                    s += " \\-"
                elif c == " | ":
                    tag = self.canvas.create_line(L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y-0.5) * GRID_SIZE,
                                                  L_OFF + x * GRID_SIZE,
                                                  T_OFF + (y+0.5) * GRID_SIZE,
                                                  width = 2, fill= "blue")
                    s += " | "
                elif c == "   ":
                    s += "   "
                elif c == " . ":
                    s += " . "
                elif c == " * ":
                    s += " * "
                elif c == " A ":
                    s += " A "
                elif c == " B ":
                    s += " B "
                else:
                    s += "ERROR>>>" + c + "<<<"
            s += "\n"
            y += 1
        #print(s)

    def register_pacman(self, pacman_model):
        self.pacman_views.append(PacmanView(self.canvas, pacman_model, self.pacman_pngs, self.pacman_dying_pngs))

    def unregister_pacman(self, pacman_model):
        for view in self.pacman_views:
            if view.pacman == pacman_model:
                view.cleanup()
            self.pacman_views.remove(view)
            return

    def register_ghost(self, ghost_model):
        ghostnum = ghost_model.ghostnum
        pngs = []
        pngs.append(self.ghost_up_pngs[ghostnum])
        pngs.append(self.ghost_left_pngs[ghostnum])
        pngs.append(self.reflect_image(self.ghost_left_pngs[ghostnum]))
        pngs.append(self.ghost_down_pngs[ghostnum])
        self.ghost_views.append(GhostView(self.canvas, ghost_model, pngs, self.ghost_eyes_pngs, self.ghost_scared_pngs))

    def register_food(self, coord_list):
        for coords in coord_list:
            food = Food(self.canvas, coords, self.food_png)
            self.food[coords] = food

    def register_powerpills(self, coord_list):
        for coords in coord_list:
            # we use a Food object with a powerpill image
            powerpill = Food(self.canvas, coords, self.powerpill_png)
            self.powerpills[coords] = powerpill

    def eat_food(self, coords):
        food = self.food[coords]
        food.eat()
        self.food.pop(coords)
        self.audio.play(0)

    def eat_powerpill(self, coords):
        powerpill = self.powerpills[coords]
        powerpill.eat()
        self.powerpills.pop(coords)
        self.audio.play(0)

    def ghost_died(self):
        self.audio.play(3)

    def unregister_objects(self):
        for view in self.ghost_views:
            view.cleanup()
        self.ghost_views.clear()
        for coords,food in self.food.items():
            food.cleanup()
        self.food.clear()
        for coords,pp in self.powerpills.items():
            pp.cleanup()
        self.powerpills.clear()

    def display_score(self):
        self.canvas.itemconfig(self.score_text, text="Level: " + str(self.controller.get_level())
                               + "  Score: " + str(self.controller.get_score()), font=self.scorefont)
        self.update_lives()

    def reflect_image(self, img):
        w, h = img.width(), img.height()
        newimg = PhotoImage(width=w, height=h)
        for x in range(w):
            for y in range(h):
                rgb = '#%02x%02x%02x' % img.get(x, y)
                newimg.put(rgb, (w-x, y))
        return newimg

    def update_lives(self):
        lives = self.controller.get_lives()
        if lives != self.lives:
            self.lives = lives
            for pacman_view in self.lives_pacmen:
                pacman_view.cleanup()
            self.lives_pacmen.clear()
            y = GRID_SIZE * 32  # 16 rows down is where we show the lives remaining
            life_pngs = [self.pacman_pngs[2]]
            for i in range(0, self.lives - 1):
                x = 2 * GRID_SIZE * (i + 1)
                dummy = DummyPacman(x, y)
                self.lives_pacmen.append(PacmanView(self.canvas, dummy, life_pngs, []))

    def died(self, pacman):
        if len(self.pacman_views) == 1:
            # only one pacman - normal gameplay
            self.pacman_views[0].died()
            self.audio.play(2)
            for ghost in self.ghost_views:
                ghost.cleanup()
            self.ghost_views.clear()
        else:
            # multiple pacmen - only one dies
            for view in self.pacman_views:
                if view.pacman == pacman:
                    view.died()
                    self.audio.play(2)

    def reset_level(self):
        self.clear_messages()
        self.audio.play(1)

    def game_over(self):
        x = 14 * GRID_SIZE + L_OFF
        y = 11 * GRID_SIZE + T_OFF
        self.text = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.text, text="GAME OVER!", font=self.bigfont,
                               fill="white")
        y = 17 * GRID_SIZE + T_OFF
        self.text2 = self.canvas.create_text(x, y, anchor="c")
        self.canvas.itemconfig(self.text2, text="Press r to play again.", font=self.scorefont,
                               fill="white")
        self.messages_displayed = True

    def clear_messages(self):
        if self.messages_displayed:
            self.canvas.delete(self.text)
            self.canvas.delete(self.text2)
            self.messages_displayed = False

    def update(self, now):
        for view in self.pacman_views:
            view.redraw(now)
        for view in self.ghost_views:
            view.redraw(now)
        self.display_score()

