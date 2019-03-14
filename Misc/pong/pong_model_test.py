import pytest
import mock, math
from pong_model import *
from pong_settings import *

class TestSuiteForBar:
    def setup_method(self):
        self.vertical_bar = GenericBar(xcenter=100,ycenter=100,size=40,inclination_angle_wrt_xaxis=math.pi/2,thickness=20,color="red",bar_id=1)
        self.deg45_bar = GenericBar(xcenter=10,ycenter=10,size=4,inclination_angle_wrt_xaxis=math.pi/4,thickness=2,color="blue",bar_id=2)
        self.leq_fun = HalfPlaneFactory().leq_fun
        self.geq_fun = HalfPlaneFactory().geq_fun

    def test_get_lines_vertical_edges_coefficients_vert_bar(self, capsys):
        extremes = self.vertical_bar._get_central_extremes(self.vertical_bar.x,self.vertical_bar.y,self.vertical_bar.inclination,self.vertical_bar.thickness)
        for e in extremes:
            print(e)
            assert e in [Point(90,100),Point(110,100)]
        coeffs = []
        for line in self.vertical_bar._get_lines(self.vertical_bar.inclination,self.vertical_bar.thickness):
            coeffs.append(line.get_coefficients())
        print(coeffs)
        for c in coeffs:
            assert c in [(1,0,-90),(1,0,-110)]

    def test_get_line_horizontal_edges_coefficients_vert_bar(self, capsys):
        extremes = self.vertical_bar._get_central_extremes(self.vertical_bar.x,self.vertical_bar.y,math.pi/2 - self.vertical_bar.inclination,self.vertical_bar.size)
        for e in extremes:
            print(e)
            assert e in [Point(100,80),Point(100,120)]
        coeffs = []
        for line in self.vertical_bar._get_lines(math.pi/2 - self.vertical_bar.inclination,self.vertical_bar.size):
            coeffs.append(line.get_coefficients())
        print(coeffs)
        for c in coeffs:
            assert c in [(0,1,-80),(0,1,-120)]

    def test_bouncing_half_planes_vert_bar(self, capsys):
        assert len(self.vertical_bar.bouncing_half_planes) == 4
        for l in self.vertical_bar.bouncing_half_planes:
            assert l.to_tuple() in [((1,0,-90),self.leq_fun,pi/2),
                         ((1,0,-110),self.geq_fun,pi/2),
                         ((0,1,-80),self.leq_fun,0),
                         ((0,1,-120),self.geq_fun,0)]

    def test_get_bouncing_half_planes_vert_bar(self, capsys):
        left_ball_pos = Point(80,100)
        left_ball_half_planes = self.vertical_bar.get_bouncing_half_planes(left_ball_pos)
        assert len(left_ball_half_planes) == 1
        assert left_ball_half_planes[0].to_tuple() == ((1,0,-90),self.leq_fun,pi/2)

        below_ball_pos = Point(100,70)
        below_ball_half_planes = self.vertical_bar.get_bouncing_half_planes(below_ball_pos)
        assert len(below_ball_half_planes) == 1
        assert below_ball_half_planes[0].to_tuple() == ((0,1,-80),self.leq_fun,0)

        nw_ball_pos = Point(120,130)
        nw_ball_half_planes = self.vertical_bar.get_bouncing_half_planes(nw_ball_pos)
        assert len(nw_ball_half_planes) == 2
        expected_half_planes = [((1,0,-110),self.geq_fun,pi/2),((0,1,-120),self.geq_fun,0)]
        for hf in nw_ball_half_planes:
            assert hf.to_tuple() in expected_half_planes

    def test_get_bouncing_angle_vert_bar(self, capsys):
        ball = Ball()

        # faraway
        ball.set_position(60,100)
        assert self.vertical_bar.get_bouncing_angle(ball,1) == None

        # too high
        ball.set_position(80,150)
        assert self.vertical_bar.get_bouncing_angle(ball,1) == None

        # too slow
        ball.set_position(68.9,100)
        assert self.vertical_bar.get_bouncing_angle(ball,1/12) == None

        # just too high
        ball.set_position(100,141)
        assert self.vertical_bar.get_bouncing_angle(ball,1) == None

        # should bounce, from left
        ball.inplay = True
        ball.kickoff(Point(0,0))
        ball.set_position(80,100)
        left_ball_bouncing_angle = self.vertical_bar.get_bouncing_angle(ball,1)
        assert left_ball_bouncing_angle != None
        assert abs(left_ball_bouncing_angle) == pi
        
        # should bounce, from top (not perfectly otherwise we will end up with the ball trapped between bar and wall)
        ball.set_position(100,125)
        ball.set_angle(-pi/2)
        top_ball_bouncing_angle = self.vertical_bar.get_bouncing_angle(ball,1)
        assert top_ball_bouncing_angle != None
        assert abs(top_ball_bouncing_angle) == pi/2 + pi/10

        # should bounce, from north-west (perfect reflection)
        ball.set_position(85,125)
        ball.set_angle(pi/6)
        nw_ball_bouncing_angle = self.vertical_bar.get_bouncing_angle(ball,1)
        assert nw_ball_bouncing_angle != None
        assert round(math.sin(nw_ball_bouncing_angle),3) == -1 * round(math.sin(pi/6),3)
        assert round(math.cos(nw_ball_bouncing_angle),3) == -1 * round(math.cos(pi/6),3)

        # should bounce on the corner (perfect reflection)
        ball.set_position(80,75)
        ball.set_angle(pi/6)
        (deltax,deltay) = ball.get_delta_future_position(1)
        se_ball_bouncing_angle = self.vertical_bar.get_bouncing_angle(ball,1)
        assert se_ball_bouncing_angle != None
        assert round(math.sin(se_ball_bouncing_angle),3) == -1 * round(math.sin(pi/6),3)
        assert round(math.cos(se_ball_bouncing_angle),3) == -1 * round(math.cos(pi/6),3)
 
    def test_ball_passing_close_to_corner(self, capsys):
        ball = Ball()
        ball.inplay = True
        ball.set_position(88,115)
        ball.set_angle(pi/2.1)
        out, err = capsys.readouterr()
        print(out)
        assert self.vertical_bar.get_bouncing_angle(ball,1) != None

    def test_runtime_bug_should_not_bounce(self, capsys):
        ball_going_outbound  = Ball()
        ball_going_outbound.inplay = True
        horizontal_bar = Wall(500, 0, 1000)
        ball_going_outbound.set_position(5.577422494468188,45.832295272374935)
        ball_going_outbound.set_angle(0)
        assert horizontal_bar.get_bouncing_angle(ball_going_outbound,1) == None

    def test_runtime_bug_ball_inside_bar(self, capsys):
        vertical_bar = Bar(2,GRID_SIZE//2)
        vertical_bar.set_position(960, 470)
        assert vertical_bar.x == 960
        ball_may_travel_inside_bar = Ball()
        ball_may_travel_inside_bar.inplay = True
        ball_may_travel_inside_bar.set_position(948.2869042038229,463.1045355058699)
        ball_may_travel_inside_bar.set_angle(-4.818420056475111)
        assert vertical_bar.get_bouncing_angle(ball_may_travel_inside_bar,10) == 1.6768274028853183 + pi / 10


    def test_runtime_bug_ball_inside_bar_again(self, capsys):
        vertical_bar = Bar(2,GRID_SIZE//2)
        vertical_bar.set_position(960,345.0)
        ball_may_travel_inside_bar = Ball()
        ball_may_travel_inside_bar.inplay = True
        ball_may_travel_inside_bar.set_position(968.745728992933,373.68641992827975)
        ball_may_travel_inside_bar.set_angle(-0.9478963128804839)
        assert vertical_bar.get_bouncing_angle(ball_may_travel_inside_bar,1) != None
        
    def test_runtime_bug_ball_stitched_to_the_bar_edge(self, capsys):
        vertical_bar = Bar(1,GRID_SIZE//2)
        vertical_bar.set_position(40,115)
        speed = 1
        ball = Ball()
        ball.inplay = True
        ball.set_position(60.281471485774496,100.79091907331336)
        init_angle = -2.0960963409908198
        ball.set_angle(init_angle)
        new_angle = vertical_bar.get_bouncing_angle(ball,speed)
        ball.bounce(new_angle,speed)
        new_new_angle = vertical_bar.get_bouncing_angle(ball,speed)
        #out, err = capsys.readouterr()
        #print(out)
        assert new_new_angle != init_angle

    def test_get_deg45_central_extremes(self, capsys):
        extremes = self.deg45_bar._get_central_extremes(self.deg45_bar.get_xpos(), self.deg45_bar.get_ypos(), self.deg45_bar.get_inclination(), self.deg45_bar.get_thickness())
        for ext in extremes:
            print(ext)
            assert round(ext.distance(self.deg45_bar.get_central_point()),3) == self.deg45_bar.thickness/2

        extremes = self.deg45_bar._get_central_extremes(self.deg45_bar.get_xpos(), self.deg45_bar.get_ypos(), -pi/2+self.deg45_bar.get_inclination(), self.deg45_bar.get_size())
        for ext in extremes:
            print(ext)
            assert round(ext.distance(self.deg45_bar.get_central_point()),3) == self.deg45_bar.size/2

    def test_get_line_coefficients_deg45_bar(self, capsys):
        print()
        lines = self.deg45_bar._get_lines(self.deg45_bar.inclination,self.deg45_bar.thickness)
        print(lines)
        for l in lines:
            c = l.get_coefficients()
            assert c in [(1,-1,round(1/cos(self.deg45_bar.inclination),3)),(1,-1,round(-1/cos(self.deg45_bar.inclination),3))]

        len(self.deg45_bar.bouncing_half_planes) == 4
        print(self.deg45_bar.bouncing_half_planes)
        expected_x_intercept_thickness_line = round((self.deg45_bar.thickness/2)*(1/cos(self.deg45_bar.inclination)),3)
        expected_first_x_intercept_size_line = round(2*(self.deg45_bar.get_central_point().distance(Point(0,0))-self.deg45_bar.size/2)*cos(self.deg45_bar.inclination),3)
        expected_second_x_intercept_size_line = round(2*(self.deg45_bar.get_central_point().distance(Point(0,0))+self.deg45_bar.size/2)*cos(self.deg45_bar.inclination),3)
        for bhf in self.deg45_bar.bouncing_half_planes:
            l = bhf.get_line()
            assert l.get_coefficients() in [(1,-1,expected_x_intercept_thickness_line),(1,-1,-expected_x_intercept_thickness_line),(-1,-1,expected_first_x_intercept_size_line),(-1,-1,expected_second_x_intercept_size_line)]



