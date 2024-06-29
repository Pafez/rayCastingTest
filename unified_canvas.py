from graphics import Canvas
from math import tan, sin, cos, pi
from time import sleep
from copy import deepcopy
from random import randint
from tapelist import TapeList
from raysegCalc import *

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
SEGMENT_COUNT = 4 + 7
COLORS = ["red", "green", "blue", "orange", "purple", "cyan", "yellow"]
FLOOR_COLOR = "lightgrey"
ROOF_COLOR = "white"

PLAYER_NECK_LENGTH = 10
PLAYER_MOVEMENT_SPEED = 3
PLAYER_ROTATION_SPEED = 0.1
RAY_COUNT = 500
FOV = pi/3

adjusted_fov = pi*((FOV/pi)%2)

CANVAS3D_STRIP_WIDTH = CANVAS_WIDTH/RAY_COUNT

VB_WIDTH = 10
VB_HEIGHT = 10

canvas = Canvas(CANVAS_WIDTH, CANVAS_WIDTH)
canvas_state = "2D"

canvas.set_canvas_background_fill(FLOOR_COLOR)

def main():
    global canvas_state
    
    player1 = Player(Point(300, 300), 0, adjusted_fov)

    run = True
    while run:
        
        goal = canvas.create_rectangle(300, 20, 310, 30, "lime")
        
        k = canvas.find_overlapping(player1.head.x, player1.head.y, player1.head.x+1, player1.head.y+1)
        if goal in k:
            canvas_state = "2D"
        else:
            canvas_state = "3D"

        if canvas_state == "3D":
            draw_background_3D(canvas)

        player_prev_pos = [player1.head, player1.back_left, player1.back_right]
        player_prev_pos_data = deepcopy(Ray(player1.centre, player1.direct))

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
                case 's':
                    player1.move(-PLAYER_MOVEMENT_SPEED)
                case 'a':
                    player1.rotate(PLAYER_ROTATION_SPEED)
                case 'd':
                    player1.rotate(-PLAYER_ROTATION_SPEED)
                case 'o':
                    toggle_canvas()
        
        player1.construct_vertices(player1.centre, player1.direct)
        player_new_pos = [player1.head, player1.back_left, player1.back_right]
 
        for segment in segments:
            for i in range(3):
                if intersection_2segment(segment, Segment(player_new_pos[i], player_prev_pos[i])) != None:
                    player1.centre = player_prev_pos_data.origin
                    player1.direct = player_prev_pos_data.direct
                    player1.construct_vertices(player1.centre, player1.direct)
                    break

        for ray_index in range(len(player1.vision_rays)):
            ray = player1.vision_rays[ray_index]
            ray.origin = player1.head
            ray.direct_offset = player1.direct
            ray.segment = None
            fisheye_corr_angle = ray.direct
            for segment in segments:
                intersection = intersection_rayx_segment(ray, segment)
                if intersection != None and (ray.segment == None or distance_2P(ray.origin, ray.intersection) > distance_2P(ray.origin, intersection)):
                    ray.segment = segment
                    ray.intersection = intersection
            if ray.segment != None:
                if canvas_state == "2D":
                    draw_ray(canvas, ray)
                elif canvas_state == "3D":
                    draw_strip(canvas, ray_index, find_height(cos(fisheye_corr_angle)*distance_2P(ray.origin, ray.intersection)), ray.segment.color)

        if canvas_state == "2D":
            for wall in walls:
                wall.draw_block(canvas)
            
            player1.draw_body()
            draw_segments(canvas)

        canvas.update()
        sleep(0.05)
        canvas.clear()

class Player:
    def __init__(self, centre, direct, adjusted_fov=2*pi, ray_count = RAY_COUNT):
        global canvas
        self.centre = centre
        self.direct = direct
        self.adjusted_fov = adjusted_fov

        self.vision_rays = []
        for i in range(ray_count):
            direct = adjusted_fov*i/ray_count - adjusted_fov/2
            self.vision_rays.append(Ray_XSegment(Point(0, 0), direct, direction_offset=self.direct, safe_distance=15))

        self.construct_vertices(self.centre, self.direct)

    def construct(self):
        self.construct_vertices(self.centre, self.direct)
        self.draw_body()

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

    def draw_body(self):
        self.body = {}
        self.body["body_left"] = canvas.create_line(self.head.x, self.head.y, self.back_left.x, self.back_left.y, width=3)
        self.body["body_right"] = canvas.create_line(self.head.x, self.head.y, self.back_right.x, self.back_right.y, width=3)
        self.body["body_back"] = canvas.create_line(self.back_left.x, self.back_left.y, self.back_right.x, self.back_right.y, width=3)

    def reconstruct(self):
        self.delete_body()
        self.construct()

    def delete_body(self):
        for body_part in self.body.values():
            canvas.delete(body_part)
        self.body = {}

    def rotate(self, direct):
        self.direct -= direct

    def move(self, distance):
        self.centre.x += distance*cos(self.direct)
        self.centre.y += distance*sin(self.direct)

segments = [
    Segment(Point(0, 0), Point(0, 400)),
    Segment(Point(0, 400), Point(400, 400)),
    Segment(Point(400, 400), Point(400, 0)),
    Segment(Point(400, 0), Point(0, 0))
]

walls = []
walls.append(Block(Point(50, 200), 100, 10, 'red'))
walls.append(Block(Point(300, 20), width=10, height=10, color="lime"))
for wall in walls:
    segments.extend(wall.borders)

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

def draw_ray(canvas, ray):
    join(canvas, ray.safe_origin, ray.intersection)

def draw_strip(canvas, index, height, color):
    canvas.create_rectangle(
        index*CANVAS3D_STRIP_WIDTH,
        CANVAS_HEIGHT/2 - height,
        (index+1)*CANVAS3D_STRIP_WIDTH,
        CANVAS_HEIGHT/2 + height,
        color
    )

def draw_background_3D(canvas):
    draw_roof_3D(canvas, ROOF_COLOR)
    draw_floor_3D(canvas, FLOOR_COLOR)

def draw_roof_3D(canvas, color):
    canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT/2, color)

def draw_floor_3D(canvas, color):
    canvas.create_rectangle(0, CANVAS_HEIGHT/2, CANVAS_WIDTH, CANVAS_HEIGHT, color)

def find_height(distance):
    if distance == 0:
        distance = 1
    height = 15*CANVAS_HEIGHT/distance
    return height

def toggle_canvas():
    global canvas_state
    if canvas_state == "3D":
        canvas_state = "2D"
    else:
        canvas_state = "3D"
    

main()
