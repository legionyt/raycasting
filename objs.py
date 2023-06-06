import math
import copy
import pygame

from params import *
from math import *


def RHtoPygame(x=None, y=None, point=None):
    if point:
        return point.x, HEIGHT - point.y
    if x and y:
        return x, HEIGHT - y


class Point:
    def __init__(self, x, y, colour=(255, 255, 255)):
        self.x = x
        self.y = y
        self.colour = colour

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def revolve(self, anchor, rads):
        dx = (self.x - anchor.x)
        dy = (self.y - anchor.y)
        self.x = dx * cos(rads) - dy * sin(rads) + anchor.x
        self.y = dx * sin(rads) + dy * cos(rads) + anchor.y

    def draw(self, window):
        pygame.draw.circle(window, self.colour, RHtoPygame(self.x, self.y), 3)

    def findDisplacement(self, point):
        if not point:
            return None
        dx = point.x - self.x
        dy = point.y - self.y
        disp = sqrt(dx**2 + dy**2)
        return disp


class Line:
    def __init__(self, p1: Point, p2: Point, colour=(255, 255, 255), height=WALL_HEIGHT):
        self.p1 = p1
        self.p2 = p2
        slope = (p2.y - p1.y)/(p2.x - p1.x + 0.000000001)
        self.graph = [slope, p2.y - slope*p2.x]
        self.colour = colour
        self.length = sqrt((self.p1.x-self.p2.x)**2 + (self.p1.y - self.p2.y)**2)
        self.height = height

    def move(self, dx, dy):
        self.p1.x += dx
        self.p1.y += dy
        self.p2.x += dx
        self.p2.y += dy
        self.updateGraph()

    def revolve(self, anchor, radians):
        self.p1.revolve(anchor, radians)
        self.p2.revolve(anchor, radians)
        self.updateGraph()

    def draw(self, window):
        pygame.draw.line(window, self.colour, RHtoPygame(point=self.p1),RHtoPygame(point=self.p2))

    def updateGraph(self):
        slope = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x + 0.00000001)
        self.graph = [slope, self.p2.y - slope * self.p2.x]


class Ray(Line):
    def calculate_intersection(self, line: Line):
        if self.graph[0] == line.graph[0]:
            print("equal slope")
            return
        x = (self.graph[1] - line.graph[1])/(line.graph[0] - self.graph[0])
        y = x*self.graph[0] + self.graph[1]
        minMax = [min(line.p1.x, line.p2.x), max(line.p1.x, line.p2.x), min(line.p1.y, line.p2.y), max(line.p1.y, line.p2.y)]
                 #min x for intersection     max x for intersection     min y for intersection     max y for intersection
        if minMax[0] <= round(x, 5) <= minMax[1] and minMax[2] <= round(y, 5) <= minMax[3]:
            return Point(x, y)
        else:
            return

    def draw(self, window):
        newPointX = self.p2.x + ((self.p2.x-self.p1.x)/abs((self.p2.x-self.p1.x) + 0.000001))*WIDTH
        newPointY = self.p2.y + (((self.p2.x-self.p1.x)/abs((self.p2.x-self.p1.x) + 0.000001))*WIDTH*self.graph[0] if (self.p2.x-self.p1.x) else HEIGHT)
        pygame.draw.line(window, self.colour, RHtoPygame(point=self.p1), RHtoPygame(newPointX, newPointY))


class Camera:
    def __init__(self, point, dirPoint: Point, dirLine: Line):
        self.point = point
        self.dirPoint = dirPoint
        self.dirLine = dirLine
        planeWidth = 2*tan(FOV/2)*PROJECTION_PLANE_DISTANCE
        # note: this configuration works only when the projection plane is parallel to the x axis
        p1 = Point(self.point.x - planeWidth/2, self.point.y + PROJECTION_PLANE_DISTANCE)
        p2 = Point(self.point.x + planeWidth/2, self.point.y + PROJECTION_PLANE_DISTANCE)
        self.projectionPlane = Line(p1, p2)
        self.rayList = []
        self.pointList = []
        self.angle = 0

        # initialize intersection points
        increment_length = self.projectionPlane.length/(RAYCOUNT-1)
        slope = self.projectionPlane.graph[0]
        sign = (self.projectionPlane.p2.x - self.projectionPlane.p1.x) / abs(
            self.projectionPlane.p2.x - self.projectionPlane.p1.x) if self.projectionPlane.p2.x != self.projectionPlane.p1.x else 0
        print(sign)
        l = 0
        for i in range(RAYCOUNT):
            px = self.projectionPlane.p1.x + sign*sqrt(l**2/(slope**2 + 1))
            py = self.projectionPlane.p1.y + (slope*px if sign != 0 else l if self.projectionPlane.p2.y > self.projectionPlane.p1.y else -l)
            p = Point(px, py)
            self.pointList.append(p)
            self.rayList.append(Ray(self.point, p))
            l += increment_length

    def lookAround(self, angle):
        self.dirPoint.revolve(self.point, angle)
        self.dirLine.revolve(self.point, angle)
        for i in self.rayList:
            i.revolve(self.point, angle)
        self.angle += angle

    def move(self, velX, velY):
        dx = cos(self.angle)*velX - sin(self.angle)*velY
        dy = sin(self.angle)*velX + cos(self.angle)*velY
        self.dirPoint.move(dx, dy)
        self.dirLine.move(dx, dy)
        self.projectionPlane.move(dx, dy)
        self.point.move(dx, dy)
        for i in self.rayList:
            i.p2.move(dx, dy)
            i.updateGraph()

    def getPerpDist(self, point: Point):
        n = abs(point.y - self.dirLine.graph[0]*point.x - self.dirLine.graph[1])
        d = sqrt(1 + self.dirLine.graph[0]**2)
        return n/d

    def checkIfFacing(self, point: Point):
        dirPCheck = False
        pCheck = False
        if self.dirPoint.y > self.dirLine.graph[0]*self.dirPoint.x + self.dirLine.graph[1]:
            dirPCheck = True
        if point.y > self.dirLine.graph[0]*point.x + self.dirLine.graph[1]:
            pCheck = True
        if dirPCheck == pCheck:
            return True
        else:
            return False





