# Simple Pong Game Model.

from math import pi,sqrt,cos,sin,tan,atan,inf
from random import Random
from abc import abstractmethod
from time import time

from pong_geometry import Point,Line,LineFactory,HalfPlaneFactory
from pong_settings import Direction,winning_score


#########
# Model #
#########

''' The Model class holds the game model, and manages the interactions
between the elements of the game.  It doesn't display anything. '''
class Model():

    # Initialisation
    
    def __init__(self, controller, number_players=2):
        self.controller = controller
        self._init_constants()
        self.init_game_objects(number_players)
        self.restart()

    def _init_constants(self):
        self.canvas_width = self.controller.get_canvas_width()
        self.canvas_height = self.controller.get_canvas_height()
        self.distance_bar_bound = self.controller.get_distance_bar_bound()
        self.bar_move_unit = self.controller.get_bar_move_unit()

    def init_game_objects(self, number_players):        
        # Ball (initially placed in the middle of the screen)
        self.ball = Ball()
        self.ball_starting_point = Point(self.canvas_width/2,self.distance_bar_bound*8) 
        self.ball.set_position(self.ball_starting_point.X,self.ball_starting_point.Y)
        self.controller.register_ball(self.ball)
        # Walls
        self.walls = [Wall(self.canvas_width/2,0,self.canvas_width), Wall(self.canvas_width/2,self.canvas_height,self.canvas_width)]
        for wall in self.walls:
            self.controller.register_wall(wall)
        # Nets
        self.nets = [Net(0,self.canvas_width/2,self.canvas_width-self.walls[0].get_thickness()*2,net_id=1),Net(self.canvas_width,self.canvas_height/2,self.canvas_height-self.walls[0].get_thickness()*2,net_id=2)]
        for net in self.nets:
            self.controller.register_net(net)
        # Players' bars
        self.bars = []
        for i in range(1,number_players+1):
            bar = Bar(i,self.bar_move_unit)
            self.bars.append(bar)
            self.controller.register_bar(bar)
        self._set_initial_bar_positions()
        # Players (initially empty, must be filled with set_players_info)
        self.bots = dict()
        self.local_players = dict()
        self.remote_players = dict()

    def set_players_info(self, players_info):
        for (player_id,player_type) in players_info:
            bar = self.bars[player_id-1]
            if player_type == 'local':
                self.local_players[player_id] = ManualPlayer(bar,self,is_local=True)
            elif player_type == 'remote':
                bar.set_color('red') 
                self.remote_players[player_id] = ManualPlayer(bar,self,is_local=False)
                # switch control between players depending on the position of the ball
                hf_factory = HalfPlaneFactory()
                remote_player_halfplane = hf_factory.get_halfplane_containing_point(Line(1,0,-self.canvas_width/2),bar.get_central_point())
                self.ball.set_remote_player_region(remote_player_halfplane)
            else:
                self.bots[player_id] = DumbBotPlayer(bar,self)

    def restart(self):
        self._set_initial_bar_positions()
        self.score = [0,0]
        self.controller.update_score(self.score)
        self.kickoff_time = True
        self.game_running = True

    def _set_initial_bar_positions(self):
        bars_positions = self._compute_initial_bar_positions()
        i = 0
        for bar_pos in bars_positions:
            self.bars[i].set_position(bar_pos.X,bar_pos.Y)
            i += 1

    # NOTE: the following assumes only two players -- could be extended for more players
    def _compute_initial_bar_positions(self):
        return [Point(self.distance_bar_bound,self.canvas_height/2), Point(self.canvas_width-self.distance_bar_bound,self.canvas_height/2)]

    # getter and setter methods

    def get_ball(self):
        return self.ball

    def get_walls(self):
        return self.walls

    def get_canvas_width(self):
        return self.canvas_width

    def get_local_players(self):
        return list(self.local_players.values()) + list(self.bots.values())

    def set_score(self, new_score):
        self.score = new_score
  
    # dynamic methods

    def kickoff_ball(self, init_angle=None):
        self.last_ball_hitter = -1
        if init_angle is not None:
            self.ball.set_angle(init_angle)
        self.ball.kickoff(self.ball_starting_point)
 
    def move_local_player_bar(self, direction, is_local_player, player_id = None):
        if is_local_player:
            [player] = self.local_players.values()
            player.move_bar(direction,self.walls)
            # moving the bar may have caused a collision with the ball, we should check
            self.check_ball(game_speed)
        else:
            raise RuntimeError("Model asked to move local player, but {} isn't a local player in {} nor a networked opponent in {}".format(player_id, self.local_players.keys(), self.remote_players.keys()))

    def move_remote_player_bar_to_point(self, player_id, xpos, ypos):
        if int(player_id) in self.remote_players:
            self.remote_players[int(player_id)].move_bar_to(xpos, ypos)
        else:
            print("Model asked to move bar of remote player, but {} isn't a remote player -- i.e., not in {}".format(player_id, self.remote_players.keys()))

    def _is_player_bar(self,bar):
        return bar.get_id() > 0 and bar.get_id() < len(self.score)+1

    def check_ball(self,game_speed):
        if not self.ball.is_inplay:
            return
        self._check_ball_bouncing(game_speed)
        self._check_ball_scoring(game_speed)
        
        # NOTE: the following conditions should not happen
        if self.ball.position.getX() < - self.ball.get_size()*2 or self.ball.position.getX() > self.canvas_width + self.ball.get_size()*2 or self.ball.position.getY() < 0 or self.ball.position.getY() > self.canvas_height:
            self.ball.set_outofbound()
            raise RuntimeError("Ball out of the screen!")
    
    def _check_ball_bouncing(self,game_speed):
        for bar in self.bars + self.walls:
            new_angle = bar.get_bouncing_angle(self.ball,game_speed)
            if new_angle != None:
                print("Ball (at {}) bouncing from angle {} to new angle {}".format(self.ball.position,self.ball.get_angle(),new_angle))
                self.ball.bounce(new_angle,self.controller.get_speed())
                if self._is_player_bar(bar):
                    self.last_ball_hitter = int(bar.get_id())
                return
    
    def _check_ball_scoring(self,game_speed):
        for net in self.nets:
            if net.get_bouncing_angle(self.ball,game_speed)!= None:
                print("Ball touched a net: updating score")
                self.update_score(net.get_id())
                self.ball.set_outofbound()

    def update_score(self,net_id):
        indices = self._select_player_indices_increasing_score(net_id)
        for index in indices:
            self._add_point(index)

    def _select_player_indices_increasing_score(self,net_id):
        indices = []
        last_hitter = int(self.last_ball_hitter)-1
        # normal case: somebody hit the ball beyond another player's bar
        if last_hitter != int(net_id)-1:
            indices = [last_hitter]
        # own goal case: every other player earns a point
        else:
            indices = list(range(len(self.bars)))
            indices.remove(last_hitter)
        return indices

    def _add_point(self,player_index):
        if player_index >= 0 and player_index < len(self.score): 
            self.score[player_index] += 1
            self.controller.update_score(self.score)
            if self.score[player_index] == winning_score:
                self.game_over()

    def game_over(self):
        if self.game_running:
            self.game_running = False
            self.controller.game_over()

    def _extract_initial_ball_angle(self):
        return Random().random() * pi/6 + pi/6  # set initial direction of the ball as random, within a reasonable angle

    def _is_ball_at_halfcourt(self, speed):
        return self.ball.get_position().X <= self.canvas_width/2 + speed or self.ball.get_position().X >= self.canvas_width/2 - speed 

    def update(self, game_speed):
        if self.game_running:
            if not self.ball.is_inplay():
                self.kickoff_ball(self._extract_initial_ball_angle())
            # move the ball, if it is not remotely controlled (or if it is close to be handed over to us)
            if not self.ball.is_remotely_controlled() or self._is_ball_at_halfcourt(game_speed):
                self.ball.move(game_speed)
            self.check_ball(game_speed)
            self.controller.update_score(self.score)
            for bot in self.bots.values():
                bot.act()


#################
# Model Objects #
#################

''' Class representing the ball. There must be only one ball per game, and it must not move if not in play.'''
class Ball():
    def __init__(self):
        self.inplay = False
        self.radius = 20
        self.position = Point(0,0)
        self.angle = 0
        self.remote_player_region = None
        self.remotely_controlled = False

    def get_size(self):
        return self.radius
    
    def get_position(self):
        return self.position

    def set_position(self,xpos,ypos):
        self.position = Point(float(xpos),float(ypos))
    
    def get_angle(self):
        return self.angle

    def set_angle(self, angle):
        self.angle = angle

    def set_remote_player_region(self,region):
        self.remote_player_region = region

    def is_remotely_controlled(self):
        return self.remote_player_region != None and self.remote_player_region.contains(self.position)

    def set_outofbound(self):
        self.inplay = False

    def is_inplay(self):
        return self.inplay

    def get_delta_future_position(self,speed):
        ball_speed = 12 * speed
        delta_x = ball_speed * cos(self.angle)
        delta_y = ball_speed * sin(self.angle)
        return delta_x,delta_y

    def move(self,speed,angle=None):
        if self.inplay:
            if angle != None:
                self.angle = angle
            (delta_x, delta_y) = self.get_delta_future_position(speed)
            self.position.move(delta_x,delta_y)

    def bounce(self,new_angle,speed):
        self.move(speed,new_angle)

    def kickoff(self, point):
        # don't put another ball in play 
        if self.inplay:
            return
        self.inplay = True
        self.position = point.copy()

''' The GenericBar class implements methods common to all kinds of bars in the game (players' bats, walls, nets).'''
class GenericBar():
    def __init__(self, xcenter, ycenter, size, inclination_angle_wrt_xaxis, thickness, color, bar_id):
        self.size = size
        assert inclination_angle_wrt_xaxis >= 0 and inclination_angle_wrt_xaxis < 2*pi
        self.inclination = inclination_angle_wrt_xaxis
        self.thickness = thickness
        self.color = color
        self.bar_id = bar_id
        self.line_factory = LineFactory()
        self.halfplane_factory = HalfPlaneFactory()
        self.set_position(xcenter,ycenter)

    def set_position(self,x,y):
        self.x = x
        self.y = y
        self._update_bouncing_half_planes()

    def get_xpos(self):
        return self.x

    def get_ypos(self):
        return self.y

    def get_central_point(self):
        return Point(self.get_xpos(),self.get_ypos())

    def get_max_dimension(self):
        return max(self.get_size(),self.get_thickness())

    def get_min_dimension(self):
        return min(self.get_size(),self.get_thickness())

    def get_size(self):
        return self.size

    def get_inclination(self):
        return self.inclination

    def get_thickness(self):
        return self.thickness

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def get_id(self):
        return self.bar_id

    # Methods to compute the lines corresponding to the bar edges
    
    def _update_bouncing_half_planes(self):
        self.bouncing_half_planes = []    # re-initialise the HalfPlane objects not containing the bar center
        angles = [self.inclination,self.inclination-pi/2]
        dimensions = [self.thickness,self.size]
        for index in range(len(angles)):
            for line in self._get_lines(angles[index], dimensions[index]):
                new_bouncing_halfplane = self.halfplane_factory.get_halfplane_opposite_point(line,self.get_central_point())
                self.bouncing_half_planes.append(new_bouncing_halfplane)


    def _get_lines(self,angle,dimension):
        lines = set([])
        for extreme in self._get_central_extremes(self.x,self.y,angle,dimension):
            lines.add(self.line_factory.get_line_from_point_and_inclination(extreme,angle))
        return lines
    
    def _get_central_extremes(self,x_center_bar_edge,y_center_bar_edge,angle,dimension):
        ext1 = Point(x_center_bar_edge - dimension/2 * sin(angle),y_center_bar_edge + dimension/2 * sin(pi/2 - angle))
        ext2 = Point(x_center_bar_edge + dimension/2 * sin(angle),y_center_bar_edge - dimension/2 * sin(pi/2 - angle))
        return [ext1,ext2]
   

    # Methods to compute if the ball should bounce and with which angle
    
    '''Returns an angle if the ball has crossed one or more bar edges, None otherwise.'''
    def get_bouncing_angle(self,ball,game_speed):
        crossed_half_planes = []
        ball_size = ball.get_size()
        ball_angle = ball.get_angle()
        ball_position = ball.get_position()
        bouncing_planes_containing_ball = self.get_bouncing_half_planes(ball_position)
        print("get_bouncing_angle, half planes ball is in: {}".format(bouncing_planes_containing_ball))
        # if the ball is inside the bar (e.g., because the bar moved),
        # bring the ball back outside
        while len(bouncing_planes_containing_ball) == 0:
            ball.move(game_speed, ball_angle - pi)
            ball_position = ball.get_position()
            bouncing_planes_containing_ball = self.get_bouncing_half_planes(ball_position)
        # if the ball faces only one bouncing half plane from this bar,
        # it should NOT bounce if it is getting farther away.
        # The ball should instead bounce if either:
        # (1) the ball would cross the bar's edge / half plane; OR
        # (2) the distance of the ball to the bar's edge is lower than
        #     the ball size (e.g., because the bar moved)
        if len(bouncing_planes_containing_ball) == 1:
            [bhf] = bouncing_planes_containing_ball
            
            line = bhf.get_line()
            distance_ball_bhf = line.get_min_distance_to_point(ball_position)
            
            (delta_x, delta_y) = ball.get_delta_future_position(game_speed)
            ball_future_position = Point(ball_position.X + delta_x, ball_position.Y + delta_y)
            future_distance_ball_bhf = line.get_min_distance_to_point(ball_future_position)

            if (bhf.contains(ball_position) and not bhf.contains(ball_future_position)) or (distance_ball_bhf <= ball.get_size()):
                crossed_half_planes = [bhf]
                # move the ball fully outside the bar
                self._move_ball_outside_bar(ball,line,game_speed)
        # if the ball is inside more than one bouncing half planes,
        # it means it is closer to a bar's corner rather than to any
        # bar's edge. So, we check that the distance of the ball
        # center to all bar's corner is smaller than the ball's size
        elif len(bouncing_planes_containing_ball) == 2:
            [bp1,bp2] = bouncing_planes_containing_ball
            corner = bp1.get_line_intersection(bp2)
            if corner.distance(ball_position) < ball.get_size():
                crossed_half_planes = bouncing_planes_containing_ball
        # it shouldn't be possible for the ball to face more than
        # two bar's edges
        else:
            raise RuntimeError("Ball ({},{}) facing an unexpected number of edges in Bar {}: {}".format(ball.get_position(),ball.get_angle(),self.get_id(),bouncing_planes_containing_ball))
        # return the bouncing angle
        print("\nFound intersected bar's edges: {}".format(crossed_half_planes))
        return self._get_new_angle(crossed_half_planes,ball_angle)

    def _get_min_distance_from_bar_extreme(self,ball_position):
        # NOTE: we could store extremes (and update them when move)
        # instead of recomputing them every time 
        min_dist = inf
        angles=[self.inclination,self.inclination-pi/2]
        dimensions=[self.thickness,self.size]
        for index in range(2):
            for extreme in self._get_central_extremes(self.x,self.y,angles[index],dimensions[index]):
                new_dist = ball_position.distance(extreme)
                min_dist = min(min_dist,new_dist)
        return min_dist

    def get_bouncing_half_planes(self,ball_center_position):
        matching_half_planes = []
        for hf in self.bouncing_half_planes:
            if hf.contains(ball_center_position):
                matching_half_planes.append(hf)
        return matching_half_planes

    def _move_ball_outside_bar(self,ball,edge_line,game_speed):
        ball_angle = ball.get_angle()
        while True:
            distance_ball_bhf = edge_line.get_min_distance_to_point(ball.get_position())
            if distance_ball_bhf > ball.get_size():
                return
            ball.move(game_speed, ball_angle - pi)
            print("Moved the ball backwards.\nBall angle: {}, new ball position: {}, new distance: {}".format(ball.get_angle(),ball.get_position(),distance_ball_bhf))
    
    def _get_new_angle(self,crossed_half_planes,initial_angle):
        if len(crossed_half_planes) == 0:
            return None
        elif len(crossed_half_planes) == 1:
            edge_inclination = crossed_half_planes[0].get_xaxis_inclination_angle()
            angle_wrt_bar = initial_angle + edge_inclination
            new_angle_wrt_bar = - angle_wrt_bar
            new_angle = new_angle_wrt_bar - edge_inclination
            # avoid angles which are too vertical
            if int(new_angle / (pi/2)) % 2 == 1 and new_angle % (pi/2) < pi/10:
                new_angle += pi / 10
            return new_angle
        # implements perfect reflection if the ball impacts two bar edges (i.e., a corner)
        return initial_angle + pi


''' A wall represent a fixed surface (at the top and bottom of the screen in a two-player game) against which the ball would bounce. '''
class Wall(GenericBar):
    def __init__(self, wall_xcenter, wall_ycenter, wall_length, wall_inclination=0, wall_thickness=30, wall_color="gray"):
        super().__init__(xcenter=wall_xcenter, ycenter=wall_ycenter, size=wall_length, inclination_angle_wrt_xaxis=wall_inclination, thickness=wall_thickness, color=wall_color, bar_id=-1)

    def get_width(self):
        return self.size

    def get_height(self):
        return self.thickness

''' A net represents the surface behind (and protected by) a player. '''
class Net(GenericBar):
    def __init__(self, net_xcenter, net_ycenter, net_length, net_inclination=pi/2, net_thickness=20, net_color="white",net_id=-2):
        super().__init__(xcenter=net_xcenter, ycenter=net_ycenter, size=net_length, inclination_angle_wrt_xaxis=net_inclination, thickness=net_thickness, color=net_color, bar_id=net_id)
        
    # ball doesn't bounce against a net
    def get_bouncing_angle(self,ball,game_speed):
        if super().get_bouncing_angle(ball,game_speed) != None:
            return ball.get_angle()
        return None

    # don't mind move the ball backwards when it hits a net
    def _move_ball_outside_bar(self,ball,edge_line,game_speed):
        pass

''' Bars represent players' bats (name of the class could have been more explicit, actually).'''
class Bar(GenericBar):
    def __init__(self, player_id, move_unit, bar_xcenter=0, bar_ycenter=0, bar_height=100, bar_width=20, bar_color="blue"):
        super().__init__(xcenter=bar_xcenter, ycenter=bar_ycenter, size=bar_height, inclination_angle_wrt_xaxis=pi/2, thickness=bar_width, color=bar_color, bar_id = player_id)
        self.move_unit = move_unit

    def get_move_unit(self):
        return self.move_unit

    def get_width(self):
        return self.thickness

    def get_height(self):
        return self.size

    ''' move due to user input '''
    def move_bar(self, direction, walls_array):
        wall_margin = walls_array[0].get_height()/2
        max_wall_height = max([w.get_ypos() for w in walls_array])
        new_y = self.y
        # NOTE: the following only works for vertical bars -- could be extended to multi-player games, relatively easily
        if direction == Direction.UP:
            new_y -= min(self.move_unit, self.y - self.get_height()/2 - wall_margin)
        elif direction == Direction.DOWN:
            new_y += min(self.move_unit, max_wall_height - wall_margin - self.y - self.get_height()/2)
        self.set_position(self.x,new_y)

###########
# Players #
###########

''' Abstract class for players '''
class AbstractPlayer():
    def __init__(self, own_bar, model):
        self.bar = own_bar
        self.model = model

    def get_bar(self):
        return self.bar

    @abstractmethod
    def get_type(self):
        pass

''' Abstract class modeling a player managed by computer '''
class AbstractBotPlayer(AbstractPlayer):
    @abstractmethod
    def act(self):
        pass

    def get_type(self):
        return "bot"

''' Computer player implementing a simple strategy '''
class DumbBotPlayer(AbstractPlayer):
    def __init__(self, own_bar, model):
        super().__init__(own_bar, model)
        self.last_move_time = time()
        self.move_frequency = 0.05
        # NOTE: decreasing the move_frequency variable makes bot players slower, and hence low delay over network games more and more important

    # Main method: the bot player tries to align its bar to the ball (only a very dumb strategy is implemented)
    def act(self):
        ball = self.model.get_ball()
        walls = self.model.get_walls()
        # skip if we moved shortly before (regulates the number of moves that the bot can do)
        curr_time = time()
        if curr_time - self.last_move_time < self.move_frequency:
            return
        # skip if ball is far away
        ball_distance = self.bar.get_central_point().distance(ball.get_position())
        if ball_distance > self.model.get_canvas_width()/3:
            return
        # otherwise, try to match ball's position
        if self.bar.get_ypos() - self.bar.get_height()/2 > ball.get_position().Y:
            self.bar.move_bar(Direction.UP,walls)
        elif self.bar.get_ypos() + self.bar.get_height()/2 < ball.get_position().Y:
            self.bar.move_bar(Direction.DOWN,walls)
        self.last_move_time = time()

''' Class modeling non-computer players -- e.g., manually controlled by the user or network opponents '''
class ManualPlayer(AbstractPlayer):
    def __init__(self, own_bar, model, is_local):
        super().__init__(own_bar, model)
        self.type_desc = 'local'
        if is_local:
            self.type_desc = 'remote'

    def move_bar(self, direction, walls_array):
        self.bar.move_bar(direction, walls_array)

    def move_bar_to(self, xpos, ypos):
        self.bar.set_position(xpos, ypos)

    def get_type(self):
        return self.type_desc





