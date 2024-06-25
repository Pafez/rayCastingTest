from graphics import Canvas
from math import tan, sin, cos, pi
from time import sleep
from random import randint
from raysegCalc import *

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
SEGMENT_COUNT = 4 + 7

PLAYER_NECK_LENGTH = 10
PLAYER_MOVEMENT_SPEED = 3
PLAYER_ROTATION_SPEED = 0.2
RAY_COUNT = 100
FOV = pi/2

canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

def main():
    
    player1 = Player(Point(300, 300), 0, FOV)

    run = True
    while run:
        key_events = canvas.get_new_key_presses()
        for i in range(len(key_events)):
            key_events[i] = key_events[i].keysym

        for key_event in key_events:
            match key_event:
                case 'Escape':
                    canvas.quit()
                    run = False
                    break
                case 'w':
                    player1.move(PLAYER_MOVEMENT_SPEED)
                case 'a':
                    player1.rotate(PLAYER_ROTATION_SPEED)
                case 'd':
                    player1.rotate(-PLAYER_ROTATION_SPEED)

        mouse = Point(canvas.get_mouse_x(), canvas.get_mouse_y())
        for ray in player1.vision_rays:
            ray.origin = player1.head
            ray.direct_offset = player1.direct
            ray.segment = None
            for segment in segments:
                intersection = is_intersect(ray, segment)
                if intersection != None and (ray.segment == None or distance_2P(ray.origin, ray.intersection) > distance_2P(ray.origin, intersection)):
                    ray.segment = segment
                    ray.intersection = intersection
            if ray.segment != None:
                join(canvas, ray.safe_origin, ray.intersection)

        player1.reconstruct()
        draw_segments(canvas)
        
        canvas.update()
        sleep(0.05)
        canvas.clear()
    
class Player:
    def __init__(self, centre, direct, fov=2*pi, ray_count = RAY_COUNT):
        global canvas
        self.centre = centre
        self.direct = direct
        self.fov = fov

        self.vision_rays = []
        for i in range(ray_count):
            direct = fov*i/ray_count - fov/2
            self.vision_rays.append(Ray_XSegment(Point(0, 0), direct, direction_offset=self.direct, safe_distance=15))

        self.construct()

    def construct(self):
        self.construct_vertices(self.centre, self.direct)
        self.construct_body()

    def construct_vertices(self, centre, direct):
        self.head = Point(
            centre.x+PLAYER_NECK_LENGTH*cos(direct),
            centre.y+PLAYER_NECK_LENGTH*sin(direct)
        )

        self.back_left = Point(
            centre.x+PLAYER_NECK_LENGTH*cos(direct+pi*3/4),
            centre.y+PLAYER_NECK_LENGTH*sin(direct+pi*3/4)
        )

        self.back_right = Point(
            centre.x+PLAYER_NECK_LENGTH*cos(direct-pi*3/4),
            centre.y+PLAYER_NECK_LENGTH*sin(direct-pi*3/4)
        )

    def construct_body(self):
        self.body = {}
        self.body["body_left"] = canvas.create_line(self.head.x, self.head.y, self.back_left.x, self.back_left.y)
        self.body["body_right"] = canvas.create_line(self.head.x, self.head.y, self.back_right.x, self.back_right.y)
        self.body["body_back"] = canvas.create_line(self.back_left.x, self.back_left.y, self.back_right.x, self.back_right.y)

    def reconstruct(self):
        self.delete_body()
        self.construct()

    def delete_body(self):
        for body_part in self.body.values():
            canvas.delete(body_part)
        self.body = {}

    def rotate(self, direct):
        self.direct -= direct

    def move(self, d):
        self.centre.x += d*cos(self.direct)
        self.centre.y += d*sin(self.direct)


segments = [
    Segment(Point(0, 0), Point(0, 400)),
    Segment(Point(0, 400), Point(400, 400)),
    Segment(Point(400, 400), Point(400, 0)),
    Segment(Point(400, 0), Point(0, 0))
]

for i in range(SEGMENT_COUNT-4):
    segments.append(
        Segment(
            Point(randint(0, CANVAS_WIDTH), randint(0, CANVAS_HEIGHT)),
            Point(randint(0, CANVAS_WIDTH), randint(0, CANVAS_HEIGHT))
        )
    )

def draw_segments(canvas):
    for segment in segments:
        canvas.create_line(
            segment.point1.x,
            segment.point1.y,
            segment.point2.x,
            segment.point2.y,
            color = segment.color
        )

def join(canvas, point1: Point, point2: Point):
    canvas.create_line(point1.x, point1.y, point2.x, point2.y)



main()