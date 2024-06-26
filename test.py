from time import sleep
from math import pi
from graphics import Canvas
from raysegCalc import *

canvas = Canvas(400, 400)

rect = canvas.create_rectangle(50, 50, 60, 60)

segments = [
    Segment(Point(0, 0), Point(0, 400)),
    Segment(Point(0, 400), Point(400, 400)),
    Segment(Point(400, 400), Point(400, 0)),
    Segment(Point(400, 0), Point(0, 0))
]

ray_count = 100
rays = []

for i in range(ray_count):
    direct = 2*pi*i/ray_count
    rays.append(Ray_XSegment(Point(0, 0), direct))

def join(canvas, point1: Point, point2: Point):
    canvas.create_line(point1.x, point1.y, point2.x, point2.y)

segments.append(Segment(Point(30, 30), Point(300, 200)))

def draw_segments(canvas):
    for segment in segments:
        canvas.create_line(
            segment.point1.x,
            segment.point1.y,
            segment.point2.x,
            segment.point2.y,
            color = segment.color
        )

while True:
    draw_segments(canvas)

    mouse = Point(canvas.get_mouse_x(), canvas.get_mouse_y())

    for ray in rays:
        ray.origin = mouse
        ray.segment = None
        for segment in segments:
            intersection = intersection_rayx_segment(ray, segment)
            if intersection != None:
                if ray.segment == None or distance_2P(ray.origin, ray.intersection) > distance_2P(ray.origin, intersection):
                    ray.segment = segment
                    ray.intersection = intersection
        
        if ray.segment != None:
            join(canvas, ray.origin, ray.intersection)

    canvas.update()
    canvas.clear()
