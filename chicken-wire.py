from collections import namedtuple
from PIL import Image

Point = namedtuple('Point', ['x', 'y', 'z'])

def add_altitude(world):
    return [[Point(x=p.x, y=p.y + p.z, z=p.z) for p in row] for row in world]

def rotate_x_y_45(world):
    ''' rotate and skew the world '''
    i = Point(x=1, y=0.5, z=0)
    j = Point(x=-1, y=0.5, z=0)
    def rotate(point):
        x = point.x * i.x + point.y * j.x
        y = point.x * i.y + point.y * j.y
        return Point(x=x, y=y, z=point.z)
    return [[rotate(point) for point in row] for row in world]

def world_to_points(world, smoothness):
    max_y = len(world) - 1
    return [[Point(x=x, y=max_y - y, z=1.0* z / smoothness) for x, z in enumerate(row)] for y, row in enumerate(world)]

def map_to_pixels(world, smoothness):
    pixels = world_to_points(world, smoothness)
    rotated_pixels = rotate_x_y_45(pixels)
    return add_altitude(rotated_pixels)

def make_line(p1, p2):
    delta_x = abs(p1.x - p2.x)
    delta_y = abs(p1.y - p2.y)
    line = []
    if p1.x == p2.x and p1.y == p2.y:
        line = [Point(x=int(p1.x), y=int(p1.y), z=max(p1.z, p2.z))]
    elif delta_x >= delta_y:
        p1, p2 = sorted([p1, p2])
        slope = 1.0 * (p2.y - p1.y) / (p2.x - p1.x)
        delta_z = 1.0 * (p2.z - p1.z) / (p2.x - p1.x)
        for x in range(0, p2.x - p1.x + 1):
            line.append(Point(x=int(p1.x + x), y=int(round(p1.y + x * slope)), z=p1.z + x * delta_z))
    elif delta_x < delta_y:
        p1, p2 = sorted([p1, p2], key=lambda p: (p.y, p.x, p.z))
        slope = 1.0 * (p2.x - p1.x) / (p2.y - p1.y)
        delta_z = 1.0 * (p2.z - p1.z) / (p2.y - p1.y)
        for y in range(0, p2.y - p1.y + 1):
            line.append(Point(x=int(round(p1.x + y * slope)), y=int(p1.y + y), z=p1.z + y * delta_z))
    return line

def scale_round_pixels(pixels, resolution):
    return [[Point(x=int(round(p.x * resolution)), y=int(round(p.y * resolution)), z=p.z) for p in row] for row in pixels]

def make_pixels(pixels, resolution):
    spixels = scale_round_pixels(pixels, resolution)
    all_pixels = []
    for i in range(len(spixels)):
        for j in range(len(spixels[0])):
            if i > 0: all_pixels.extend(make_line(spixels[i - 1][j], spixels[i][j]))
            if j > 0: all_pixels.extend(make_line(spixels[i][j - 1], spixels[i][j]))
    return all_pixels

def altitude_to_color(z, step=80, mountain=5, min_color=100):
    if z < 0: return (0, 0, int(min(255, min_color + -z * step)))
    elif z < 5: return (0, int(min(255, min_color + z * step)), 0)
    return (int(min(255, min_color + z * step)), 0, 0)

def normalize_pixels(pixels):
    min_x, max_x = min(pixels, key=lambda p: p.x).x, max(pixels, key=lambda p: p.x).x
    min_y, max_y = min(pixels, key=lambda p: p.y).y, max(pixels, key=lambda p: p.y).y
    res_x, res_y = max_x - min_x, max_y - min_y
    pixels = [Point(x=p.x - min_x, y=res_y - (p.y - min_y), z=p.z) for p in pixels]
    return pixels, res_x, res_y

def draw_pixels(pixels, res_x, res_y, filename):
    im = Image.new('RGB', (res_x + 1, res_y + 1))
    for x, y, z in pixels:
        im.putpixel((x, y), altitude_to_color(z))
    im.save(filename)

def read_map():
    '''
    File format:
    -----------------------------------------------
    <nb-of-lines> <unit-square-resolution> <smoothness>
    <altitudes>
    ...
    <altitudes>
    -----------------------------------------------
    e.g.
    4 50 10
    0 0 1 0
    0 2 8 0
    1 3 6 4
    '''
    n, resolution, smoothness = map(int, raw_input().split())
    return resolution, smoothness, [map(int, raw_input().split()) for _ in range(n)]

def main(resolution, smoothness, world):
    pixels = map_to_pixels(world, smoothness)
    all_pixels = make_pixels(pixels, resolution)
    normalized_pixels, res_x, res_y = normalize_pixels(all_pixels)
    draw_pixels(normalized_pixels, res_x, res_y, 'x.png')

if __name__ == '__main__':
    main(*read_map())
