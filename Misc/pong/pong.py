# Simple Pong Game. 

import asyncio, argparse, time
from tkinter import *
from math import pi,sqrt,cos,sin,tan,atan,inf
from abc import abstractmethod

import pong_settings as settings
from pong_view import TkView
from pong_model import Model
from network_utils import UdpPeer2PeerDaemon


#############
# Constants #
#############

NETMSG_INFO_SEP = ";"
NETMSG_FIELD_SEP = ","
NETMSG_BALLPOS_ID = "Ball:"
NETMSG_BARPOS_ID = "Bar:"
NETMSG_SCORE_ID = "Score:"
NETMSG_RST_ID = "Restart:"
NETMSG_GAMERUN_ID = "Game-running:"


##############
# Controller #
##############

''' The Controller class handles input from the user, registering and
updating new views. It also serves to route updates from the Model to
the Views '''

class Controller():
    
    ### Initialisation ###
    
    def __init__(self):
        self.running = True
        self.decision_maker = True
        self.waiting_net_opponent = True
        self.remote_game_running = False
        self.local_restart = False
        self.remote_restart = False
        if settings.remote_players == 0:
            self.waiting_net_opponent = False
            self.remote_restart = True
            self.remote_game_running = True
        self.walls = []
        self.nets = []
        self.bars = []
        self.views = []
        self.score = []
        self.speed = 1.0
        self.run_update_frequency = 0.001
        self.net_sending_frequency = 0.001
        self.model = self.get_model()

    def get_model(self):
        return Model(self)   
    
    ### Getter and setter methods ###

    def get_speed(self):
        return self.speed
    
    def get_canvas_width(self):
        return settings.CANVAS_WIDTH

    def get_canvas_height(self):
        return settings.CANVAS_HEIGHT

    def get_distance_bar_bound(self):
        return settings.DISTANCE_BAR_BOUND

    def get_bar_move_unit(self):
        return settings.GRID_SIZE

    def get_score(self):
        return self.score

    def get_score_text(self):
        text = "Score:\n"
        for index in range(len(self.score)):
            text += "{}".format(self.model.score[index])
            if index < len(self.score) - 1:
                text += "\t"
        return text

    def update_score(self, score):
        self.score = score

    def set_local_restart(self, value=True):
        self.local_restart = value
        
    def set_remote_restart(self, value):
        self.remote_restart = value

    def set_remote_game_running(self, value):
        self.remote_game_running = value

    ### Methods to interact with model and view ###

    def register_ball(self, ball):
        self.ball = ball

    def register_wall(self, wall):
        self.walls.append(wall)

    def register_net(self, net):
        self.nets.append(net)

    def register_bar(self, bar):
        self.bars.append(bar)

    def add_view(self):
        view = TkView(self, 0.7)
        # we only support one view at the moment
        if len(self.views) > 0:
            return
        self.views.append(view)
        view.register_ball(self.ball)
        for bar in self.bars:
            view.register_bar(bar)
        for wall in self.walls:
            view.register_wall(wall)
        for net in self.nets:
            view.register_net(net) 

    def move_gui_player_bar(self, direction, is_local):
        if settings.local_human_players == 1:
            self.model.move_local_player_bar(direction, is_local)

    def game_over(self):
        for view in self.views:
            view.game_over()
        self.local_restart = False
        if settings.remote_players > 0:
            self.remote_restart = False

    def restart(self):
        for view in self.views:
            view.clear_messages()
        self.model.restart()

    def exit(self):
        self.running = False
        print("\nGame stop running.")

    ### Methods to run the game locally (on this machine) ###
       
    def get_players_info(self,remote_higher=True):
        tot_players = settings.local_human_players + settings.local_bot_players + settings.remote_players
        # we only support two players so far
        if tot_players != 2:
            raise RuntimeError ("Unsupported number of players: {} local users, {} local bots and {} remote players".format(settings.local_human_players, settings.local_bot_players, settings.remote_players))
            raise KeyboardInterrupt             # exit
        tot_ids = list(range(1,tot_players+1))
        players_features = ['local'] * settings.local_human_players + ['bot'] * settings.local_bot_players + ['remote'] * settings.remote_players
        if remote_higher:
            players_features.reverse()
        print("Players info: {}".format(list(zip(tot_ids,players_features))))
        return list(zip(tot_ids,players_features))

    def calibrate_speed(self):
        #do one round of display before we seed the speed measurement,
        #or we get a bad first value because it takes time to draw the
        #window the first time
        self.add_view()
        self.model.update(self.speed)
        for view in self.views:
            view.update()
        self.lastframe = time.time()
        self.framecount = 0

    ''' adjust game speed so it's more or less the same on different machines '''
    def checkspeed(self):
        self.framecount = self.framecount + 1
        # only check every ten frames
        if self.framecount == 10:
            now = time.time()
            elapsed = now - self.lastframe
            if self.speed == 0:
                #initial speed value: At 60fps, 10 frames take 1/6 of a second.
                self.speed = 6 * elapsed
            else:
                # use an EWMA to damp speed changes and avoid excessive jitter
                self.speed = self.speed * 0.9 + 0.1 * 6 * elapsed
            self.lastframe = now
            self.framecount = 0
     
    async def check_restart(self):
        if self.local_restart:
            for view in self.views:
                view.wait_for_remote_opponent()
                view.update()
            # if the opponent is ready, let's (re)start a new game
            if self.remote_restart:
                # wait a bit before restarting so that
                # generate_messages_for_net_opponent()
                # can notify the remote opponent
                await asyncio.sleep(self.run_update_frequency * 150)        
                self.restart()
                self.local_restart = False
                self.running = True

    async def run_game(self):
        while self.waiting_net_opponent:
            await asyncio.sleep(self.run_update_frequency)
        players_info = self.get_players_info(remote_higher=self.decision_maker)
        self.model.set_players_info(players_info)
        self.calibrate_speed()
        self.model.game_over()
        while self.running:
            await self.check_restart()
            self.checkspeed()
            self.model.update(self.speed)
            for view in self.views:
                view.update()
            await asyncio.sleep(self.run_update_frequency)
        for v in self.views:
            v.destroy()

    ### Methods for network interaction, i.e., to exchange messages with remote opponents ###
    
    def compose_position_message(self, message_id, fields_content_list):
        string = message_id + ''
        for field in fields_content_list:
            string += str(field) + NETMSG_FIELD_SEP
        k = string.rfind(NETMSG_FIELD_SEP)
        string = string[:k] 
        return string
        
    def parse_position_message(self, object_id, message):
        content = message.split(object_id)[1]
        return content.split(NETMSG_FIELD_SEP)

    async def generate_messages_for_net_opponent(self):
        try:
            while self.running:
                msg = ''
                if not self.ball.is_remotely_controlled():
                    ball_pos = self.ball.get_position()
                    msg += self.compose_position_message(NETMSG_BALLPOS_ID,[ball_pos.X,ball_pos.Y,self.ball.get_angle()]) + NETMSG_INFO_SEP
                for local in self.model.get_local_players():
                    bar = local.get_bar()
                    bar_id = bar.get_id()
                    bar_pos = bar.get_central_point()
                    msg += self.compose_position_message(NETMSG_BARPOS_ID,[bar_id,bar_pos.X,bar_pos.Y]) + NETMSG_INFO_SEP
                msg += self.compose_position_message(NETMSG_SCORE_ID,self.get_score()) + NETMSG_INFO_SEP
                msg += self.compose_position_message(NETMSG_RST_ID,[self.local_restart]) + NETMSG_INFO_SEP
                msg += self.compose_position_message(NETMSG_GAMERUN_ID,[self.model.game_running])
                yield msg.encode()
                await asyncio.sleep(self.net_sending_frequency)
        except KeyboardInterrupt:
            print('Got closing signal <Ctrl-C> from keyboard.')
        finally:
            print('Stopping inform opponent.')

    async def process_message_from_net_opponent(self, data, addr):
        if self.waiting_net_opponent:
            self.waiting_net_opponent = False
        message_string = data.decode()
        print("Pong received {}".format(message_string))
        for string in message_string.split(NETMSG_INFO_SEP):
            if string.startswith(NETMSG_BALLPOS_ID):
                [xpos,ypos,angle] = self.parse_position_message(NETMSG_BALLPOS_ID,string)
                # adjust the ball as said by the opponent if the ball
                # is remotely controlled or to (re)start the game
                if self.ball.is_remotely_controlled() or (not self.remote_game_running and not self.decision_maker):
                    self.ball.set_position(float(xpos),float(ypos))
                    self.ball.set_angle(float(angle))
            elif string.startswith(NETMSG_BARPOS_ID):
                [bar_id,xpos,ypos] = self.parse_position_message(NETMSG_BARPOS_ID,string)
                self.model.move_remote_player_bar_to_point(bar_id,float(xpos),float(ypos))
            elif string.startswith(NETMSG_RST_ID):
                [remote_start] = self.parse_position_message(NETMSG_RST_ID,string)
                self.set_remote_restart(remote_start.strip() == "True")
            elif string.startswith(NETMSG_GAMERUN_ID):
                [remote_run] = self.parse_position_message(NETMSG_GAMERUN_ID,string)
                self.set_remote_game_running(remote_run.strip() == "True")
            elif string.startswith(NETMSG_SCORE_ID):
                [score_p1,score_p2] = self.parse_position_message(NETMSG_SCORE_ID,string)
                score = [int(score_p1),int(score_p2)]
                if self.ball.is_remotely_controlled():
                    self.update_score(score)
                    self.model.set_score(score)

    ### Main method ###
            
    def run(self,local_ip,local_port,opponent_ip,opponent_port):
        # check whether we should be the ones making initial decisions (e.g., about ball's initial direction) 
        if local_ip > opponent_ip or (local_ip == opponent_ip and local_port > opponent_port): 
            self.decision_maker = False
        # setup infrastructure to handle the network connection
        loop = asyncio.get_event_loop()
        daemon = UdpPeer2PeerDaemon(local_port,opponent_port, listen_ip=local_ip, send_ip=opponent_ip)
        daemon.process_incoming_messages(loop, packet_handle_function = self.process_message_from_net_opponent)
        daemon.send(loop, packet_generator_function = self.generate_messages_for_net_opponent(), sending_interval=self.net_sending_frequency)
        # run the game
        try:
            loop.run_until_complete(self.run_game())
        except KeyboardInterrupt:
            pass
        # closing
        loop.run_until_complete(daemon.shutdown())
        loop.close()
        

############
# Run Pong #
############

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simple Pong game working over IP/TCP networks in a peer-to-peer fashion.')
    
    parser.add_argument('local_ip', type=str, help='A required string representation of the IP address of this machine')
    parser.add_argument('local_port', type=int, help='A required port number (int) where this application will run')
    
    parser.add_argument('opponent_ip', type=str, help='A required string representation of the IP address of the opponent')
    parser.add_argument('opponent_port', type=int, help='A required port number (int) of the opponent')
    args = parser.parse_args()
    return (args.local_ip,args.local_port,args.opponent_ip,args.opponent_port)

if __name__ == "__main__":
    (local_ip,local_port,opponent_ip,opponent_port) = parse_arguments()
    controller = Controller()
    controller.run(local_ip,local_port,opponent_ip,opponent_port)


