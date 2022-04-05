
from hypothesis import given, strategies as st

import numpy as np

from map import *

from bresenham import bresenham


def runAllTests():
    gridSizeCheck()
    populateTest()
    getAsListTest()
    getRGBTest()
    averagePixelTest()
    getTileTypeTest()
    getAdjacentTest()
    tileSearchTest()
    findOpeningsTest()
    rgbDistanceTest()
    countTilesTest()
    lineTest()
    getObstructionsTest()


DefaultSize = 128

rgbMap = {
    "wall": (0,  0,  0, 255),
    "background": (255, 255, 255, 255),
    "closet": (192, 192, 224, 255),
    "bathroom": (192, 255, 255, 255),  # /washroom
    # livingroom/kitchen/dining room
    "dining room": (224, 255, 192, 255),
    "bedroom": (255, 224, 128, 255),
    "hall": (255, 160, 96, 255),
    "balcony": (255, 224, 224, 255),
    "opening": (255, 60, 128, 255),  # door & window
    "NaN": (0, 0, 0, 0)  # unused / used as an invalid tile
}

tileMap = {v: k for k, v in rgbMap.items()}


# the pixels of a drawing which contains many individual shapes
randomShapes = [(int(round(np.cos(2*np.pi*i/360)*10+i/2)),
                 int(round(np.sin(2*np.pi*i/360)*10+i/2))) for i in range(0, 360)]

# the shapes contained within the randomShapes drawing
expectedTileSearchResult = [[(10, 0), (10, 1), (11, 1), (11, 2)],
                            [(13, 4), (13, 5), (14, 5), (14, 6)],
                            [(16, 8), (16, 9), (17, 9), (17, 10)],
                            [(19, 12), (19, 13)],
                            [(20, 14), (20, 15), (21, 15), (21, 16)],
                            [(22, 17), (22, 18)], [(24, 20), (24, 21)],
                            [(25, 22), (25, 23), (26, 23), (26, 24), (26, 25), (27, 25),
                             (27, 26), (28, 26), (28, 27), (28, 28), (29, 28), (29, 29)],
                            [(30, 30), (30, 31), (31, 31), (31, 32), (31, 33), (32, 33),
                             (32, 34), (33, 34), (33, 35), (33, 36), (34, 36), (34, 37)],
                            [(35, 38), (35, 39)], [(36, 40), (36, 41)],
                            [(37, 42), (37, 43), (38, 43), (38, 44)],
                            [(39, 45), (39, 46)],
                            [(40, 47), (40, 48), (41, 48), (41, 49)],
                            [(42, 50), (42, 51), (43, 51), (43, 52)],
                            [(44, 53), (44, 54), (45, 54), (45, 55)],
                            [(46, 56), (46, 57), (47, 57), (47, 58)],
                            [(48, 59), (48, 60), (49, 60), (49, 61)],
                            [(50, 62), (50, 63), (51, 63),
                             (51, 64), (52, 64), (52, 65)],
                            [(53, 66), (53, 67), (54, 67), (54, 68),
                             (55, 68), (55, 69), (56, 69), (56, 70)],
                            [(60, 74), (60, 75), (61, 75)],
                            [(65, 79), (66, 79), (66, 80), (67, 80),
                             (67, 81), (68, 81), (68, 82), (69, 82)],
                            [(70, 83), (71, 83), (71, 84),
                             (72, 84), (72, 85), (73, 85)],
                            [(74, 86), (75, 86), (75, 87), (76, 87)],
                            [(77, 88), (78, 88), (78, 89), (79, 89)],
                            [(80, 90), (81, 90), (81, 91), (82, 91)],
                            [(83, 92), (84, 92), (84, 93), (85, 93)],
                            [(86, 94), (87, 94), (87, 95), (88, 95)],
                            [(89, 96), (90, 96)],
                            [(91, 97), (92, 97), (92, 98), (93, 98)],
                            [(94, 99), (95, 99)],
                            [(96, 100), (97, 100)],
                            [(98, 101), (99, 101), (99, 102), (100, 102), (101, 102), (101, 103),
                             (102, 103), (102, 104), (103, 104), (104, 104), (104, 105), (105, 105)],
                            [(106, 106), (107, 106), (107, 107), (108, 107), (109, 107), (109, 108),
                             (110, 108), (110, 109), (111, 109), (112, 109), (112, 110), (113, 110)],
                            [(114, 111), (115, 111)],
                            [(117, 113), (118, 113)],
                            [(119, 114), (120, 114), (120, 115), (121, 115)],
                            [(122, 116), (123, 116)],
                            [(125, 118), (126, 118), (126, 119), (127, 119)]]


@given(st.integers(), st.integers())
# @settings(max_examples)
def gridSizeCheck(x, y):
    try:
        grid = Grid(x, y)
        assert grid.getSizeX() == x and grid.getSizeY() == y
    except ValueError:
        if x <= 0 or x > 1000 or y <= 0 or y > 1000:
            assert True


@given(st.integers(), st.integers(), st.tuples(st.integers(), st.integers(), st.integers()))
def populateTest(a, b, rgb):
    grid = Grid(DefaultSize, DefaultSize)
    try:
        grid.populate(a, b, rgb)
        assert grid.getRGBValue(a, b) == (rgb[0], rgb[1], rgb[2], 255)
    except ValueError:
        assert True


@given(st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1), st.tuples(st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255)))
def getAsListTest(x, y, rgb):
    grid = Grid(DefaultSize, DefaultSize)
    # empty 2d ndarray
    testAgainst = np.empty((DefaultSize, DefaultSize), dtype=tuple)
    try:
        grid.populate(x, y, rgb)
        testAgainst[x][y] = (rgb[0], rgb[1], rgb[2], 255)
        assert testAgainst.flatten == grid.getAsList()
    except ValueError:
        # print(x, y, rgb)
        assert True


@given(st.integers(), st.integers(), st.tuples(st.integers(), st.integers(), st.integers()))
def getRGBTest(a, b, rgb):
    grid = Grid(DefaultSize, DefaultSize)
    try:
        grid.populate(a, b, rgb)
        assert grid.getRGBValue(a, b) == (rgb[0], rgb[1], rgb[2], 255)
    except ValueError:
        assert True


@given(st.lists(st.tuples(st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1)), min_size=1))
def averagePixelTest(listOfPixels):
    grid = Grid(DefaultSize, DefaultSize)
    x = sum([pixel[0] for pixel in listOfPixels]) / len(listOfPixels)
    y = sum([pixel[1] for pixel in listOfPixels]) / len(listOfPixels)
    assert grid.averagePixel(listOfPixels) == (int(x), int(y))


@given(st.sampled_from(sorted(rgbMap.values())), st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1))
def getTileTypeTest(rgb, x, y):
    grid = Grid(DefaultSize, DefaultSize)
    try:
        grid.populate(x, y, rgb)
        assert grid.getTileType(x, y) == tileMap[rgb]
    except ValueError:
        assert True


@given(st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1))
def getAdjacentTest(x, y):
    grid = Grid(DefaultSize, DefaultSize)
    for coord in grid.getAdjacentCoords(x, y).values():
        assert sum(abs(np.subtract((x, y), coord))) == 1


@given(st.tuples(st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255)), st.tuples(st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255), st.integers(min_value=0, max_value=255)))
def rgbDistanceTest(start, end):
    grid = Grid(DefaultSize, DefaultSize)
    assert grid.rgbDistance(start, end) == np.linalg.norm(
        np.subtract(start, end))


def tileSearchTest():
    grid = Grid(DefaultSize, DefaultSize)

    for coord in randomShapes:
        if coord[0] < DefaultSize and coord[1] < DefaultSize:
            grid.populate(coord[0], coord[1], rgbMap["opening"])

    assert grid.tileSearch("opening") == expectedTileSearchResult


def findOpeningsTest():
    grid = Grid(DefaultSize, DefaultSize)
    for coord in randomShapes:
        if coord[0] < DefaultSize and coord[1] < DefaultSize:
            grid.populate(coord[0], coord[1], rgbMap["opening"])

    expectedOpenings = {expectedTileSearchResult.index(
        v): v for v in expectedTileSearchResult}
    grid.findOpenings()

    assert [opening.getPixels() for opening in grid.getOpenings().values()] == [
        opening for opening in expectedOpenings.values()]


def countTilesTest():
    grid = Grid(DefaultSize, DefaultSize)

    for coord in randomShapes:
        if coord[0] < DefaultSize and coord[1] < DefaultSize:
            grid.populate(coord[0], coord[1], rgbMap["opening"])

    assert grid.countTiles("opening") == len(
        list(filter(None, grid.getAsList())))
    
@given(st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1))
def lineTest(startX, startY, endX, endY):
    grid = Grid(DefaultSize, DefaultSize)
    
    assert grid.pixelsBetweenTwoPoints(startX, startY, endX, endY) == list(bresenham(startX, startY, endX, endY))

@given(st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1), st.integers(min_value=0, max_value=DefaultSize-1))
def getObstructionsTest(startX, startY, endX, endY):
    grid = Grid(DefaultSize, DefaultSize)
    
    for x in range(grid.getSizeX()):
        for y in range(grid.getSizeY()):
            grid.populate(x, y, rgbMap["wall"])
    
    assert grid.getObstructionsInLine(list(bresenham(startX, startY, endX, endY))) == len(list(bresenham(startX, startY, endX, endY)))

if __name__ == "__main__":
    runAllTests()
