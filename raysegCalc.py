from math import sin, cos, atan2, sqrt, pi

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class Segment:
    def __init__(self, point1: Point, point2: Point, color: str = "black") -> None:
        self.point1 = point1
        self.point2 = point2
        self.color = color

class Block:
    def __init__(self, point: Point, width = 1, height = 1, color: str = "black", is_rigid: bool = True, is_visible: bool = True) -> None:
        self.point = point
        self.width = width
        self.height = height
        self.color = color
        self.is_rigid = is_rigid
        self.is_visible = is_visible
        self.borders = []

        self.set_vertices()
        
        if is_rigid:
            self.create_borders()

    def set_vertices(self):
        self.p1 = self.point
        self.p2 = Point(self.point.x, self.point.y + self.height)
        self.p3 = Point(self.point.x + self.width, self.point.y + self.height)
        self.p4 = Point(self.point.x + self.width, self.point.y)

    def create_borders(self):
        self.borders = [
            Segment(self.p1, self.p2, self.color),
            Segment(self.p2, self.p3, self.color),
            Segment(self.p3, self.p4, self.color),
            Segment(self.p4, self.p1, self.color),
        ]

    def draw_block(self, canvas):
        if self.is_visible:
            canvas.create_rectangle(self.p1.x, self.p1.y, self.p3.x, self.p3.y, self.color)
            return 0
        return 1

class Ray:
    def __init__(self, origin: Point, direction) -> None:
        self.origin = origin
        self.direct = direction

class Ray_XSegment(Ray):
    def __init__(self, origin: Point, direction, direction_offset = 0, segment: Segment = None, intersection: Point = None, safe_distance = 10) -> None:
        super().__init__(origin, direction)
        self.segment = segment
        self.intersection = intersection
        self.safe_distance = safe_distance
        self.safe_origin = None
        self.direct_offset = direction_offset

def intersection_rayx_segment(ray: Ray_XSegment, segment: Segment):
    acc = -10
    x1 = ray.origin.x
    y1 = ray.origin.y
    x2 = ray.origin.x+acc*cos(ray.direct+ray.direct_offset)
    y2 = ray.origin.y+acc*sin(ray.direct+ray.direct_offset)
    x3 = segment.point1.x
    y3 = segment.point1.y
    x4 = segment.point2.x
    y4 = segment.point2.y

    num_u = (x1-x2)*(y1-y3)-(y1-y2)*(x1-x3)
    den_u = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if den_u == 0:
        return None
    
    u = -num_u/den_u

    if not 0 <= u <= 1:
        return None
    
    intersection = Point(
        x3 + u*(x4-x3),
        y3 + u*(y4-y3)
    )

    dist1 = acc
    dist2 = distance_2P(Point(x2, y2), intersection)
    dist = distance_2P(ray.origin, intersection)
    if not (-0.0001 <= dist1 + dist2 - dist <= 0.0001):
        return None
    
    ray.safe_origin = Point(
        ray.origin.x+ray.safe_distance*cos(ray.direct+ray.direct_offset),
        ray.origin.y+ray.safe_distance*sin(ray.direct+ray.direct_offset)
    )

    return intersection

def intersection_2segment(segment1: Segment, segment2: Segment):
    x1 = segment1.point1.x
    y1 = segment1.point1.y
    x2 = segment1.point2.x
    y2 = segment1.point2.y
    x3 = segment2.point1.x
    y3 = segment2.point1.y
    x4 = segment2.point2.x
    y4 = segment2.point2.y

    num_u = (x1-x2)*(y1-y3)-(y1-y2)*(x1-x3)
    num_t = (x1-x3)*(y3-y4)-(y1-y3)*(x3-x4)
    den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if den == 0:
        return None
    
    u = -num_u/den
    t = num_t/den

    if not (0 <= u <= 1 and 0 <= t <= 1):
        return None

    intersection = Point(
        x3 + u*(x4-x3),
        y3 + u*(y4-y3)
    )

    return intersection

def distance_2P(point1: Point, point2: Point):
    d = sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    return d
