"""
Module for creating polygon object and bounding box from list of coordinates. Designed to be used
for fine-grained geo-location filtering of tweets.
USAGE: (python) polygon.py "STATE"
"""

import sys
import re
import shapely.geometry as shp


def retrieve_polygon(state):
    co_list = state_coords(state)
    points = coords2points(co_list)
    poly = polygon(points)
    return poly


def retrieve_bbox(state):
    co_list = state_coords(state)
    points = coords2points(co_list)
    bbox = list(bounding_box(points))
    return bbox


def state_coords(state):
    with open("state_coordinates.js","rb") as f:
        statelist = f.read()
    coords = re.search(r'{}.*?borders:(.*?\]\]\])'.format(state), statelist, re.IGNORECASE).group(1)
    coords = re.sub(r'^\[\[(.*)\]\]$', r'\1', coords)
    coords = re.sub(r'\],\[', r']|[', coords)
    coords = coords.split("|")
    return coords


def coords2points(coord_list):
    points = []
    for coords in coord_list:
        if isinstance(coords, str):
            x = re.search(r'\[([\d\.-]+),', coords).group(1)
            y = re.search(r',([\d\.-]+)\]', coords).group(1)
        elif isinstance(coords, list):
            x = coords[0]
            y = coords[1]
        points.append(shp.Point(float(y), float(x)))
    return points


def bounding_box(pointlist):
    east = min([p.y for p in pointlist])
    west = max([p.y for p in pointlist])
    south = min([p.x for p in pointlist])
    north = max([p.x for p in pointlist])
    return (east, south, west, north)


def polygon(pointlist):
    poly = shp.MultiPoint(pointlist).convex_hull
    return poly


if __name__ == "__main__":
    try:
        retrieve_polygon(sys.argv[1])
        retrieve_bbox(sys.argv[1])
    except IndexError:
        sys.exit("ERROR: you must specify a state!")
