from graphics import Canvas
from math import tan, sin, cos, pi
from time import sleep
from copy import deepcopy
from random import randint
from tapelist import TapeList
from raysegCalc import *
from mazedata import maze_raw

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
SEGMENT_COUNT = 4 + 7
COLORS = ["blue", "orange", "purple", "cyan", "yellow", "pink", "magenta", "violet"]
FLOOR_COLOR = "lightgrey"
ROOF_COLOR = "white"

PLAYER_NECK_LENGTH = 5
PLAYER_MOVEMENT_SPEED = 4
PLAYER_ROTATION_SPEED = 0.2
RAY_COUNT = 500
FOV = pi/3

adjusted_fov = pi*((FOV/pi)%2)

CANVAS3D_STRIP_WIDTH = CANVAS_WIDTH/RAY_COUNT

VB_WIDTH = 10
VB_HEIGHT = 10

canvas = Canvas(CANVAS_WIDTH, CANVAS_WIDTH)
canvas_state = "2D"

def main():
    global canvas_state, map_point_ids
    canvas.set_canvas_background_fill(FLOOR_COLOR)
    
    player1 = Player(Point(390, 230), pi, adjusted_fov)

    run = True
    gen = 0
    win = False
    while run:
        
        goal = canvas.create_rectangle(333, 143, 343, 153, "green")

        map_point_ids = []
        for map_point in map_points:
            map_point_ids.append(canvas.create_rectangle(map_point.point.x, map_point.point.y, map_point.point.x+map_point.width, map_point.point.y+map_point.height, map_point.color))
                
        player_head_sense = canvas.find_overlapping(player1.head.x-5, player1.head.y-5, player1.head.x+5, player1.head.y+5)

        for map_point_id in map_point_ids:
            if map_point_id in player_head_sense:
                canvas_state = "2D"
                break
            else:
                canvas_state = "3D"

        if goal in player_head_sense:
            win = True
            run = False
            break

        if canvas_state == "3D":
            draw_background_3D(canvas)

        player_prev_pos = [player1.head, player1.back_left, player1.back_right]

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
                    player1.moveX(PLAYER_MOVEMENT_SPEED, player_prev_pos)
                    player1.moveY(PLAYER_MOVEMENT_SPEED, player_prev_pos)
                case 's':
                    player1.moveX(-PLAYER_MOVEMENT_SPEED, player_prev_pos)
                    player1.moveY(-PLAYER_MOVEMENT_SPEED, player_prev_pos)
                case 'a':
                    player1.rotate(PLAYER_ROTATION_SPEED, player_prev_pos)
                case 'd':
                    player1.rotate(-PLAYER_ROTATION_SPEED, player_prev_pos)
        
        player1.construct_vertices(player1.centre, player1.direct)

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
                #if canvas_state == "2D":
                    #draw_ray(canvas, ray)
                if canvas_state == "3D":
                    draw_strip(canvas, ray_index, find_height(cos(fisheye_corr_angle)*distance_2P(ray.origin, ray.intersection)), ray.segment.color)

        if canvas_state == "2D":
            for wall in walls:
                wall.draw_block(canvas)
            
            player1.draw_body()
            draw_segments(canvas)

        canvas.update()
        canvas.clear()
        gen += 1

    canvas.quit()
    score = 1000000//gen
    print("Score: ", score)

def title_screen():
    global canvas
    canvas.create_text(50, 50, "Welcome to The Maze", "Callibri", 25, "red")

    canvas.create_text(20, 120, "Objective", "Arial", 15, "green")
    canvas.create_text(40, 145, "Objective", "Arial", 13, "green")


    canvas.wait_for_click()
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

    def rotate(self, direct, player_prev_pos):
        new_direct = self.direct - direct

        player_new_pos = []
        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(new_direct),
            self.centre.y+PLAYER_NECK_LENGTH*sin(new_direct)
        ))

        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(new_direct+pi*3/4),
            self.centre.y+PLAYER_NECK_LENGTH*sin(new_direct+pi*3/4)
        ))

        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(new_direct-pi*3/4),
            self.centre.y+PLAYER_NECK_LENGTH*sin(new_direct-pi*3/4)
        ))
        for segment in segments:
            for i in range(3):
                if intersection_2segment(segment, Segment(player_new_pos[i], player_prev_pos[i])) != None:
                    return 1
        self.direct = new_direct
        return 0

    def move(self, distance):
        self.centre.x += distance*cos(self.direct)
        self.centre.y += distance*sin(self.direct)

    def moveX(self, distance, player_prev_pos):
        new_x = self.centre.x + distance*cos(self.direct)
        player_new_pos = []
        player_new_pos.append(Point(
            new_x+PLAYER_NECK_LENGTH*cos(self.direct),
            self.centre.y+PLAYER_NECK_LENGTH*sin(self.direct)
        ))

        player_new_pos.append(Point(
            new_x+PLAYER_NECK_LENGTH*cos(self.direct+pi*3/4),
            self.centre.y+PLAYER_NECK_LENGTH*sin(self.direct+pi*3/4)
        ))

        player_new_pos.append(Point(
            new_x+PLAYER_NECK_LENGTH*cos(self.direct-pi*3/4),
            self.centre.y+PLAYER_NECK_LENGTH*sin(self.direct-pi*3/4)
        ))
        for segment in segments:
            for i in range(3):
                if intersection_2segment(segment, Segment(player_new_pos[i], player_prev_pos[i])) != None:
                    return 1
        self.centre.x = new_x
        return 0
    
    def moveY(self, distance, player_prev_pos):
        new_y = self.centre.y + distance*sin(self.direct)
        player_new_pos = []
        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(self.direct),
            new_y+PLAYER_NECK_LENGTH*sin(self.direct)
        ))

        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(self.direct+pi*3/4),
            new_y+PLAYER_NECK_LENGTH*sin(self.direct+pi*3/4)
        ))

        player_new_pos.append(Point(
            self.centre.x+PLAYER_NECK_LENGTH*cos(self.direct-pi*3/4),
            new_y+PLAYER_NECK_LENGTH*sin(self.direct-pi*3/4)
        ))
        for segment in segments:
            for i in range(3):
                if intersection_2segment(segment, Segment(player_new_pos[i], player_prev_pos[i])) != None:
                    return 1
        self.centre.y = new_y
        return 0

segments = [
    Segment(Point(0, 0), Point(0, 400)),
    Segment(Point(0, 400), Point(400, 400)),
    Segment(Point(400, 400), Point(400, 0)),
    Segment(Point(400, 0), Point(0, 0))
]

walls = []
for wall_raw in maze_raw:
    if len(wall_raw) == 4:
        walls.append(Block(
            Point(wall_raw[0], wall_raw[1]),
            wall_raw[2]-wall_raw[0],
            wall_raw[3]-wall_raw[1],
            COLORS[randint(0, len(COLORS) - 1)]
    ))
for wall in walls:
    segments.extend(wall.borders)

map_points = [
    Block(Point(340, 245), 5, 5, "red"),
    Block(Point(62, 139), 5, 5, "red"),
    Block(Point(14, 349), 5, 5, "red"),
    Block(Point(290, 380), 5, 5, "red")
]

walls.extend(map_points)

for map_point in map_points:
    segments.extend(map_point.borders)

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
    
title_screen()
main()
