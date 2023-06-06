import pygame
from math import *
from params import *
from objs import *

# setup
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
running = True
objects = [Line(Point(200, 350), Point(400, 350), colour=(0,255, 0)), Line(Point(400, 350), Point(400, 150), colour=(255,0,0)),
           Line(Point(200, 350), Point(200, 150), colour=(0,0,255)), Line(Point(200, 150), Point(400, 150)),

           Line(Point(100, 450), Point(100, 50), colour=(255, 0, 0)), Line(Point(500, 450), Point(500, 50), colour=(0, 0, 255)),
           Line(Point(100, 450), Point(500, 450)), Line(Point(100, 50), Point(500, 50), colour=(0, 255, 0))]
clock = pygame.time.Clock()

# object initialization
camera = Camera(point=Point(300, 200), dirPoint=Point(300, 350, colour=(0,255,0)), dirLine=Line(Point(250, 200), Point(350, 200)))

# tracking variables
rotationRate = 0
rotating = False
currentVel = [0, 0]
moving = False


def draw3d():
    win.fill((0, 0, 0))
    pygame.draw.rect(win, SKY_COLOUR, pygame.Rect((0,0), (WIDTH, HEIGHT/2)))
    pygame.draw.rect(win, FLOOR_COLOUR, pygame.Rect((0,HEIGHT/2), (WIDTH, HEIGHT/2 )))
    blockLength = 0
    if WIDTH > RAYCOUNT:
        blockLength = WIDTH / RAYCOUNT

    for i in camera.rayList:
        intersection = None
        minDisp = inf
        wall = None
        for x in objects:
            inter = i.calculate_intersection(x)
            if inter:
                disp = camera.point.findDisplacement(inter)
                facing = camera.checkIfFacing(inter)
                if facing and disp <= minDisp:
                    intersection = inter
                    minDisp = disp
                    wall = x

        if intersection:
            # code for 3d
            index = camera.rayList.index(i)
            distance = camera.getPerpDist(intersection)
            height = (wall.height / (2 * distance * tan(FOV / 2))) * HEIGHT

            if blockLength:
                pygame.draw.rect(win, wall.colour,
                                 pygame.Rect(index * blockLength, (HEIGHT - height) / 2, index * (blockLength + 1),
                                             (HEIGHT - height) / 2 + height))
            else:
                pygame.draw.line(win, [
                    i * (((VANISHING_POINT - distance) + abs(VANISHING_POINT - distance)) / 2) / VANISHING_POINT for i
                    in wall.colour], (index, (HEIGHT - height) / 2), (index, (HEIGHT - height) / 2 + height))


def drawTopDown():
    win.fill((0, 0, 0))
    camera.point.draw(win)
    camera.dirLine.draw(win)
    camera.dirPoint.draw(win)
    for x in objects:
        x.draw(win)
    for i in camera.rayList:
        intersection = None
        minDisp = inf
        wall = None
        for x in objects:
            inter = i.calculate_intersection(x)
            if inter:
                disp = camera.point.findDisplacement(inter)
                facing = camera.checkIfFacing(inter)
                if facing and disp <= minDisp:
                    intersection = inter
                    minDisp = disp
                    wall = x

        if intersection:
            Line(camera.point, intersection).draw(win)
            intersection.draw(win)
        else:
           i.draw(win)

prevMouse = (0,0)

print(camera.getPerpDist(Point(220, 350)))
while running:

    drawTopDown()
    #draw3d()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                rotationRate = -ROTSPEED
                rotating = True
            if event.key == pygame.K_LEFT:
                rotationRate = ROTSPEED
                rotating = True
            if event.key == pygame.K_a:
                currentVel[0] = -1*VELX
                moving = True
            if event.key == pygame.K_d:
                moving = True
                currentVel[0] = VELX
            if event.key == pygame.K_w:
                moving = True
                currentVel[1] = VELY
            if event.key == pygame.K_s:
                moving = True
                currentVel[1] = -1*VELY
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                rotationRate = 0
                rotating = False
            if event.key == pygame.K_a or event.key == pygame.K_d:
                currentVel[0] = 0
            if event.key == pygame.K_w or event.key == pygame.K_s:
                currentVel[1] = 0

    if currentVel == [0, 0]:
        moving = False
    if rotating:
        camera.lookAround(rotationRate)
    if moving:
        camera.move(currentVel[0], currentVel[1])

    if running:
        pygame.display.flip()
        clock.tick(60)


