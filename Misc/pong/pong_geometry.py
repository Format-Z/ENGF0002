# Geometry utilities for the Pong Game.

import math

class Point():
    '''Creates a point on a coordinate plane with values x and y.'''
    def __init__(self, x, y):
        self.X = round(x,3)
        self.Y = round(y,3)

    '''create a new object from this one.  we use this when we want to
       create a modified copy of a point without modifying the original object'''
    def copy(self):
        return Point(self.X, self.Y)

    ''' vector addition of points '''
    def add(self, other):
        self.X = self.X + other.X
        self.Y = self.Y + other.Y

    def move(self, dx, dy):
        self.X = self.X + dx
        self.Y = self.Y + dy

    def __str__(self):
        return "Point (%s, %s)"%(self.X, self.Y) 

    def getX(self):
        return self.X

    def getY(self):
        return self.Y

    def distance(self, other):
        dx = self.X - other.X
        dy = self.Y - other.Y
        return math.sqrt(dx**2 + dy**2)

    def __eq__(self, other):
        return ((self.X, self.Y) == (other.X, other.Y))

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return ((self.X, self.Y) < (other.X, other.Y))

class Line():
    '''Creates a line ax + by + c = 0 from input coefficients a, b, c.'''
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def get_coefficients(self):
        return (self.a, self.b, self.c)

    def get_slope_and_intersect(self):
        if self.b == 0:
            return (math.inf,self.c/self.a)
        return (-self.a/self.b,-self.c/self.b)

    def get_min_distance_to_point(self, point):
        num_distance = abs(self.a * point.X + self.b * point.Y + self.c)
        den_distance = math.sqrt(self.a**2 + self.b**2)
        return num_distance / den_distance

    def get_xaxis_inclination_angle(self):
        (m,_) = self.get_slope_and_intersect()
        return math.atan(m)

    def get_intersection(self, other_line):
        intersection_x, intersection_y = 0, 0
        m1, q1 = self.get_slope_and_intersect()
        m2, q2 = other_line.get_slope_and_intersect()
        # parallel lines
        if m1 == m2:
            return None
        # non-parallel lines
        if m1 == math.inf:
            intersection_x = -q1
            intersection_y = m2 * intersection_x + q2
        elif m2 == math.inf:
            intersection_x = -q2
            intersection_y = m1 * intersection_x + q1
        else:
            intersection_x = (q2 - q1) / (m1 - m2)
            intersection_y = m1 * intersection_x + q1
        return Point(intersection_x,intersection_y)

    def __str__(self):
        return "Line (%sx + %sy + %s = 0)"%(self.a, self.b, self.c)

    def __repr__(self):
        return str(self)

class LineFactory():
    def get_line_traversing_point(self, a, b, point):
        c = round(- a * point.X - b * point.Y,3)
        return Line(a,b,c)

    def get_line_from_point_and_inclination(self,point,xaxis_angle):
        # vertical line
        if xaxis_angle == math.pi/2 or xaxis_angle == 3 * math.pi/2:
            a = 1
            b = 0
        # horizontal line
        elif xaxis_angle == 0 or xaxis_angle == math.pi:
            a = 0
            b = 1
        # any other inclination
        else:
            a = round(math.tan(xaxis_angle))
            b = -1
        return self.get_line_traversing_point(a,b,point)

class HalfPlane():
    def __init__(self, delimiting_line, hf_function):
        self.line = delimiting_line
        self.fun = hf_function

    def get_line(self):
        return self.line

    def get_function(self):
        return self.fun

    def get_xaxis_inclination_angle(self):
        return self.line.get_xaxis_inclination_angle()

    def contains(self, point):
        (a,b,c) = self.line.get_coefficients()
        return self.fun(a * point.X + b * point.Y + c, 0)

    def get_line_intersection(self, other_half_plane):
        return self.line.get_intersection(other_half_plane.get_line())

    def to_tuple(self):
        return (self.line.get_coefficients(),self.fun,self.get_xaxis_inclination_angle())

    def __str__(self):
        (a, b, c) = self.line.get_coefficients()
        function_str = ">"
        if self.fun == less_or_equal:
            function_str = "<"
        return "half plane: {}x + {}y + {} {} 0".format(a, b, c, function_str)

    def __repr__(self):
        return str(self)


def greater_or_equal(x,y):
    return x >= y

def less_or_equal(x,y):
    return x <= y

class HalfPlaneFactory():
    def __init__(self):
        self.geq_fun = greater_or_equal
        self.leq_fun = less_or_equal

    def get_halfplane_containing_point(self, line, point):
        (a,b,c) = line.get_coefficients()
        hf_function = self.geq_fun
        if a * point.X + b * point.Y + c < 0:
            hf_function = self.leq_fun
        return HalfPlane(line,hf_function)

    def get_halfplane_opposite_point(self, line, point):
        hf_with_point = self.get_halfplane_containing_point(line, point)
        new_fun = self.geq_fun
        if hf_with_point.get_function() == self.geq_fun:
            new_fun = self.leq_fun
        return HalfPlane(hf_with_point.get_line(),new_fun)


