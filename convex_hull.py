from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 2


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # Determines if the points are clockwise, counterclockwise, or co-linear
    def orientation(self, p1, p2, p3):
        value = (p2.y() - p1.y()) * (p3.x() - p2.x()) - (p2.x() - p1.x()) * (p3.y() - p2.y())
        # value is co-linear
        if value == 0:
            return 0
        # value is clockwise
        if value > 0:
            return 1
        # value is counterclockwise
        return -1

    # Finds the upper tangent points of the Left Hull and the Right Hull
    def upper_tangent(self, L, R, L_rightmost, R_leftmost):
        Lsize = len(L)
        Rsize = len(R)
        Ltangent = L_rightmost
        Rtangent = R_leftmost
        isFound = False
        while not isFound:
            isFound = True
            # Find the upper tangent on the Left Hull
            while (self.orientation(R[Rtangent], L[Ltangent], L[(Lsize + Ltangent - 1) % Lsize]) >= 0 or
                   self.orientation(R[Rtangent], L[Ltangent], L[(Lsize + Ltangent + 1) % Lsize]) >= 0):
                # If the previous index on the Left Hull is clockwise or co-linear, decrement the left tangent point
                if self.orientation(R[Rtangent], L[Ltangent], L[(Lsize + Ltangent - 1) % Lsize]) >= 0:
                    Ltangent = (Lsize + Ltangent - 1) % Lsize
                # If the next index on the Left Hull is clockwise or co-linear, increment the left tangent point
                if self.orientation(R[Rtangent], L[Ltangent], L[(Lsize + Ltangent + 1) % Lsize]) >= 0:
                    Ltangent = (Lsize + Ltangent + 1) % Lsize
            # Find the upper tangent on the Right Hull
            while (self.orientation(L[Ltangent], R[Rtangent], R[(Rtangent + 1) % Rsize]) <= 0 or
                   self.orientation(L[Ltangent], R[Rtangent], R[(Rtangent - 1) % Rsize]) <= 0):
                # If the next index on the Right Hull is counterclockwise or co-linear, increment the right tangent point
                if self.orientation(L[Ltangent], R[Rtangent], R[(Rtangent + 1) % Rsize]) <= 0:
                    Rtangent = (Rtangent + 1) % Rsize
                    isFound = False
                # If the previous index on the Right Hull is counterclockwise or co-linear, decrement the right tangent point
                if self.orientation(L[Ltangent], R[Rtangent], R[(Rtangent - 1) % Rsize]) <= 0:
                    Rtangent = (Rtangent - 1) % Rsize
                    isFound = False
        return Ltangent, Rtangent

    # Finds the lower tangent points of the Left Hull and the Right Hull
    def lower_tangent(self, L, R, L_rightmost, R_leftmost):
        Lsize = len(L)
        Rsize = len(R)
        Ltangent = L_rightmost
        Rtangent = R_leftmost
        isFound = False
        while not isFound:
            isFound = True
            # Find the lower tangent on the Right Hull
            while (self.orientation(L[Ltangent], R[Rtangent], R[(Rsize + Rtangent + 1) % Rsize]) >= 0 or
                   self.orientation(L[Ltangent], R[Rtangent], R[(Rsize + Rtangent - 1) % Rsize]) >= 0):
                # if the next index on the Right Hull is clockwise or co-linear, increment the right tangent point
                if self.orientation(L[Ltangent], R[Rtangent], R[(Rsize + Rtangent + 1) % Rsize]) >= 0:
                    Rtangent = (Rsize + Rtangent + 1) % Rsize
                # if the previous index on the Right Hull is clockwise or co-linear, decrement the right tangent point
                if self.orientation(L[Ltangent], R[Rtangent], R[(Rsize + Rtangent - 1) % Rsize]) >= 0:
                    Rtangent = (Rsize + Rtangent - 1) % Rsize
            # Find the lower tangent on the Left Hull
            while (self.orientation(R[Rtangent], L[Ltangent], L[(Ltangent - 1) % Lsize]) <= 0 or
                   self.orientation(R[Rtangent], L[Ltangent], L[(Ltangent + 1) % Lsize]) <= 0):
                # if the previous index on the Left Hull is counterclockwise or co-linear, decrement the left tangent point
                if self.orientation(R[Rtangent], L[Ltangent], L[(Ltangent - 1) % Lsize]) <= 0:
                    Ltangent = (Ltangent - 1) % Lsize
                    isFound = False
                # if the next index on the Left Hull is counterclockwise or co-linear, increment the left tangent point
                if self.orientation(R[Rtangent], L[Ltangent], L[(Ltangent + 1) % Lsize]) <= 0:
                    Ltangent = (Ltangent + 1) % Lsize
                    isFound = False
        return Ltangent, Rtangent

    # Combines two Hulls into one Hull
    def merge(self, L, R):
        points = []

        Lsize = len(L)
        Rsize = len(R)
        L_rightmost = 0
        R_leftmost = 0

        # Find the rightmost point of L
        for i in range(1, Lsize):
            if L[i].x() > L[L_rightmost].x():
                L_rightmost = i

        # Find the leftmost point of R
        for i in range(1, Rsize):
            if R[i].x() < R[R_leftmost].x():
                R_leftmost = i

        # Finds the upper and lower tangent points
        Ltangent_upper, Rtangent_upper = self.upper_tangent(L, R, L_rightmost, R_leftmost)
        Ltangent_lower, Rtangent_lower = self.lower_tangent(L, R, L_rightmost, R_leftmost)

        # Creates the new Hull from lower tangent to upper tangent of the Left Hull
        # then to the upper tangent to the lower tangent of the Right Hull
        i = Ltangent_lower
        points.append(L[i])
        while i != Ltangent_upper:
            i = (i + 1) % Lsize
            points.append(L[i])
        i = Rtangent_upper
        points.append(R[i])
        while i != Rtangent_lower:
            i = (i + 1) % Rsize
            points.append(R[i])
        return points

    # Returns a set of three points in clockwise order
    def clockwise(self, p1, p2, p3):
        clockwise_points = []
        value = (p2.y() - p1.y()) * (p3.x() - p2.x()) - (p2.x() - p1.x()) * (p3.y() - p2.y())
        # When value is clockwise, return the points as previously ordered
        if value > 0:
            clockwise_points.append(p1)
            clockwise_points.append(p2)
            clockwise_points.append(p3)
            return clockwise_points
        # When value is counterclockwise, switch the order of the second and third points
        elif value < 0:
            clockwise_points.append(p1)
            clockwise_points.append(p3)
            clockwise_points.append(p2)
            return clockwise_points

    # Determines the smallest, clockwise set of points in a convex shape
    def convex_hull(self, points):
        # Return points in clockwise order
        if len(points) <= 2:
            return points
        elif len(points) == 3:
            return self.clockwise(points[0], points[1], points[2])
        midpoint = (int)(len(points) / 2)
        left = points[:midpoint]
        right = points[midpoint:]
        # Recursively splits the points in half and then merges the Left Hull and the Right Hull
        Left_Hull = self.convex_hull(left)
        Right_Hull = self.convex_hull(right)
        points_of_polygon = self.merge(Left_Hull, Right_Hull)
        # If `Show Recursion` box is checked on the GUI
        if self.pause:
            polygon = [QLineF(points_of_polygon[i], points_of_polygon[(i + 1) % len(points_of_polygon)]) for i in
                       range(len(points_of_polygon))]
            self.showHull(polygon, RED)
        return points_of_polygon

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # Sort points depending on the x direction
        points.sort(key=lambda point: point.x())
        print(points)
        t2 = time.time()

        t3 = time.time()
        # Creates a set of lines from the set of points returned from convex_hull
        points_of_polygon = self.convex_hull(points)
        polygon = [QLineF(points_of_polygon[i], points_of_polygon[(i + 1) % len(points_of_polygon)]) for i in
                   range(len(points_of_polygon))]
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))
