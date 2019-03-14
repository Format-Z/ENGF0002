# PacMan Game.  Mark Handley, UCL, 2018

from tkinter import *
from pa_model import Model, Status
from pa_view import View
from pa_settings import Direction, LOGTIME
from pa_network import Network
from sys import argv
from getopt import getopt, GetoptError
import time

class Controller():
    def __init__(self, argv):
        self.parse_args(argv)
        self.root = Tk();
        self.windowsystem = self.root.call('tk', 'windowingsystem')
        self.views = []
        self.root.bind_all('<KeyPress>', self.keypress)
        self.root.bind_all('<KeyRelease>', self.keyrelease)
        self.running = True
        self.score = 0
        self.remote_score = 0
        self.level = -1
        self.ghosts = []
        self.pacmen = []
        self.food_coords = []
        self.powerpill_coords = []
        self.maze = None
        self.net = None
        self.model = Model(self, self.serv);
        self.add_view(View(self.root, self))
        self.net = Network(self, self.passwd)
        self.local_ip = self.net.get_local_ip_addr()
        for view in self.views:
            if self.serv:
                view.display_msg("Waiting for Player 2 to connect\nIP addr: " + self.local_ip)
            view.update(time.time())
        self.root.update()
        self.init_net()
        self.model.activate()

    def parse_args(self, argv):
        try:
            if "pacman.py" in argv[0]:
                opts, args = getopt(argv[1:], "sc:p:", ["serv=", "conn=", "pass="])
            else:
                opts, args = getopt(argv, "sc:p:", ["serv=", "conn=", "pass="])
        except GetoptError:
            self.usage()
        self.passwd = "000000"
        self.serv = False
        self.connect_to = "127.0.0.1"
        for opt, arg in opts:
            if opt in ("-s", "--server"):
                self.serv = True
            elif opt in ("-c", "--connect"):
                self.connect_to = arg
            elif opt in ("-p", "--passwd"):
                self.passwd = arg
            else:
                self.usage()
        if self.serv:
            print("Server mode, password is ", self.passwd)
        else:
            print("Client mode, password is ", self.passwd, "connecting to", self.connect_to)

    def init_net(self):
        if (self.serv):
            self.net.server(9872)
        else:
            self.net.client(self.connect_to, 9872)

    def usage(self):
        print("pacman.py [-s | --server] [-c <ip address> | --connect=<ip address>] \n          [-p <password> | --passwd=<password>]")
        sys.exit(2)

    def display_msg(self, msg):
        for view in self.views:
            view.display_msg(msg)

    def unregister_objects(self):
        self.ghosts.clear()
        for view in self.views:
            view.unregister_objects()

    def register_pacman(self, pacman):
        self.pacmen.append(pacman)
        for view in self.views:
            view.register_pacman(pacman)

    def unregister_pacman(self, pacman):
        self.pacmen.remove(pacman)
        for view in self.views:
            view.unregister_pacman(pacman)

    def register_ghost(self, ghost):
        self.ghosts.append(ghost)
        for view in self.views:
            view.register_ghost(ghost)

    def register_food(self, coordlist):
        self.food_coords = coordlist
        for view in self.views:
            view.register_food(coordlist)

    def register_powerpills(self, coordlist):
        self.powerpill_coords = coordlist
        for view in self.views:
            view.register_powerpills(coordlist)

    def eat(self, coords, is_powerpill):
        if is_powerpill:
            if coords in self.powerpill_coords:
                self.powerpill_coords.remove(coords)
        else:
            if coords in self.food_coords:
                self.food_coords.remove(coords)
        for view in self.views:
            view.eat(coords, is_powerpill)

    def ghost_died(self):
        for view in self.views:
            view.ghost_died()

    def add_view(self, view):
        self.views.append(view)
        for pacman in self.pacmen:
            view.register_pacman(pacman)
        for ghost in self.ghosts:
            view.register_ghost(ghost)
        view.register_food(self.food_coords)
        view.update_maze(self.maze)

    #some helper functions to hide the controller implementation from
    #the model and the controller
    def update_score(self, score):
        self.score = score
        if self.net is not None:
            self.net.send_score_update(score)

    def update_remote_score(self, remote_score):
        self.remote_score = remote_score

    def get_scores(self):
        return self.score, self.remote_score

    def send_maze(self, maze):
        self.net.send_maze(maze)

    def update_maze(self, maze):
        self.maze = maze
        for view in self.views:
            view.update_maze(maze)
        
    def update_level(self, level):
        self.level = level
        for view in self.views:
            view.reset_level()

    def get_level(self):
        return self.level

    def update_lives(self, lives):
        self.lives = lives

    def get_lives(self):
        return self.lives

    def died(self, pacman, clear_ghosts):
        if pacman.on_our_screen:
            for view in self.views:
                view.died(pacman, clear_ghosts)
        else:
            self.net.send_foreign_pacman_died()

    def game_over(self):
        for view in self.views:
            view.game_over()
        
    def keypress(self, event):
        if event.char == 'a' or event.keysym == 'Left':
            self.model.key_press(Direction.LEFT)
        elif event.char == 'w' or event.keysym == 'Up':
            self.model.key_press(Direction.UP)
        elif event.char == 's' or event.keysym == 'Down':
            self.model.key_press(Direction.DOWN)
        elif event.char == 'd' or event.keysym == 'Right':
            self.model.key_press(Direction.RIGHT)
        elif event.char == 'q':
            self.running = False
        elif event.char == 'r':
            for view in self.views:
                view.clear_messages()
            self.model.ready_to_restart()

    def keyrelease(self, event):
        if event.char == 'a' or event.keysym == 'Left':
            self.model.key_release()
        elif event.char == 'w' or event.keysym == 'Up':
            self.model.key_release()
        elif event.char == 's' or event.keysym == 'Down':
            self.model.key_release()
        elif event.char == 'd' or event.keysym == 'Right':
            self.model.key_release()

#Terminology:
#    LOCAL      local object, currently local
#    AWAY       local object, currently on vacation abroad
#    FOREIGN    foreign object visiting us, needs displaying on our screen
#    REMOTE     foreign object on their screen, we don't display (but our Pacman
#               away may collide with)

    def received_maze(self, maze):
        self.model.received_maze(maze)

    def foreign_pacman_arrived(self):
        self.model.foreign_pacman_arrived()

    def send_foreign_pacman_arrived(self):
        self.net.send_foreign_pacman_arrived()

    def foreign_pacman_left(self):
        self.model.foreign_pacman_left()

    def send_foreign_pacman_left(self):
        self.net.send_foreign_pacman_left()

    def pacman_go_home(self):
        self.model.pacman_go_home()

    def send_pacman_go_home(self):
        self.net.send_pacman_go_home()

    def foreign_pacman_died(self):
        self.model.foreign_pacman_died()

    def send_foreign_pacman_died(self):
        self.net.send_foreign_pacman_died()

    def foreign_pacman_update(self, pos, dir, speed):
        self.model.foreign_pacman_update(pos, dir, speed)

    def send_pacman_update(self, pos, dir, speed):
        self.net.send_pacman_update(pos, dir, speed)

    def foreign_pacman_ate_ghost(self, ghostnum):
        self.model.foreign_pacman_ate_ghost(ghostnum)

    def send_foreign_pacman_ate_ghost(self, ghostnum):
        self.net.send_foreign_pacman_ate_ghost(ghostnum)

    def remote_ghost_update(self, ghostnum, pos, dir, speed, mode):
        self.model.remote_ghost_update(ghostnum, pos, dir, speed, mode)

    def send_ghost_update(self, ghostnum, pos, dir, speed, mode):
        self.net.send_ghost_update(ghostnum, pos, dir, speed, mode)

    # we receive this when food or powerpill is eaten on the remote maze
    # we need to receive it to update our shadow copy of that maze
    def remote_eat(self, pos, is_powerpill):
        self.model.remote_eat(pos, is_powerpill)

    # we receive this when a foreign pacman ate food or powerpill on our local maze
    # we need to update our model; the model will then update the screen.
    def foreign_eat(self, pos, is_powerpill):
        self.model.foreign_eat(pos, is_powerpill)

    # food was eaten on our screen
    def send_eat(self, pos, is_powerpill):
        self.net.send_eat(pos, False, is_powerpill)

    # our (foreign) pacman ate food on their screen
    def send_foreign_eat(self, pos, is_powerpill):
        self.net.send_eat(pos, True, is_powerpill)

    def send_status_update(self, status):
        self.net.send_status_update(status)

    def remote_status_update(self, status):
        self.model.remote_status_update(status)

    def run(self):
        t_count = 0
        t = [0.0,0.0,0.0,0.0]
        t_mean = [0.0,0.0,0.0,0.0]
        t_max = [0.0,0.0,0.0,0.0]
        while self.running:
            now = time.time()
            self.net.check_for_messages(now)
            if LOGTIME:
                now2 = time.time()
            self.model.update(now)
            if LOGTIME:
                now3 = time.time()
            for view in self.views:
                view.update(now)
            if LOGTIME:
                now4 = time.time()
            self.root.update()
            if LOGTIME:
                now5 = time.time()
            if LOGTIME:
                t[0] = now2 - now
                t[1] = now3 - now2
                t[2] = now4 - now3
                t[3] = now5 - now4
                for i in range(0,4):
                    t_mean[i] += t[i]
                    if t[i] > t_max[i]:
                        t_max[i] = t[i]
                t_count += 1
                if t_count % 600 == 0:
                    s = "Stats. Means: "
                    for i in range(0,4):
                        s += str(t_mean[i]/t_count)
                        s += " "
                    s += " Maxs: "
                    for i in range(0,4):
                        s += str(t_max[i])
                        s += " "
                    print(s)
                    t_mean = [0.0,0.0,0.0,0.0]
                    t_max = [0.0,0.0,0.0,0.0]
                    t_count = 0
                        
        self.root.destroy()
