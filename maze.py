from raysegCalc import *
from graphics import Canvas
from time import sleep

canvas = Canvas(400, 400)

segments = [
    Segment(Point(0, 0), Point(0, 400)),
    Segment(Point(0, 400), Point(400, 400)),
    Segment(Point(400, 400), Point(400, 0)),
    Segment(Point(400, 0), Point(0, 0))
]

def draw_segments(canvas):
    for segment in segments:
        canvas.create_line(
            segment.point1.x,
            segment.point1.y,
            segment.point2.x,
            segment.point2.y,
            color = segment.color
        )




maze_raw = [
    [0, 21, 100, 31],
    [52, 49, 137, 59],
    [127, 21, 137, 49],
    [0, 190, 15, 200],
    [0, 265, 20, 275],
    [0, 375, 78, 385],
    [40, 345, 50, 385],
    [40, 80, 50, 320],
    [100, 350, 110, 400],
    [172, 380, 182, 400],
    [133, 380, 143, 400],
    [213, 380, 223, 400],
    [270, 350, 280, 400],
    [305, 315, 315, 363],
    [305, 363, 363, 373],
    [363, 363, 373, 400],
    [373, 315, 400, 325],
    [340, 285, 350, 340],
    [230, 285, 315, 295],
    [230, 315, 280, 325],
    [145, 350, 245, 360],
    [193, 285, 203, 350],
    [70, 285, 80, 350],
    [80, 285, 165, 295],
    [40, 315, 193, 325],
    [70, 225, 80, 265],
    [50, 155, 85, 165],
    [85, 120, 95, 205],
    [50, 80, 173, 90],
    [95, 120, 173, 130],
    [95, 195, 163, 205],
    [163, 183, 173, 220],
    [118, 155, 205, 165],
    [205, 55, 215, 85],
    [205, 105, 215, 220],
    [163, 21, 173, 80],
    [173, 21, 255, 31],
    [245, 31, 255, 195],
    [245, 195, 400, 205],
    [105, 255, 400, 265],
    [280, 21, 375, 31],
    [335, 0, 345, 21],
    [245, 31, 255, 220],
    [311, 70, 321, 170],
    [321, 160, 357, 170],
    [357, 102, 367, 170],
    [311, 60, 370, 70],
    [255, 60, 280, 70],
    [255, 110, 280, 120],
    [255, 160, 280, 170]
]

walls = []
for wall_raw in maze_raw:
    if len(wall_raw) == 4:
        walls.append(Block(
            Point(wall_raw[0], wall_raw[1]),
            wall_raw[2]-wall_raw[0],
            wall_raw[3]-wall_raw[1],
            'red'
    ))
for wall in walls:
    segments.extend(wall.borders)


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
    
    for wall in walls:
        wall.draw_block(canvas)
    draw_segments(canvas)

    mouse = Point(canvas.get_mouse_x(), canvas.get_mouse_y())
    print(mouse.x, mouse.y)

    canvas.update()
    sleep(0.1)
