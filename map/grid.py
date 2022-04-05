from collections import Counter
import copy
from re import search
import numpy as np
from .opening import Opening

# (x=0,y=0) of the grid is in the top left corner

class Grid():
    """Grid class: a 2-dimensional nparray containing RGBA colours in the form of 4-tuples (r, g, b, a)
    """

    def __init__(self, sizeX, sizeY):
        """Grid class __init__ : creates an empty 2D grid of a given size when instantiated

        Args:
            sizeX (int): the horizontal size X of the grid
            sizeY (int): the vertical size Y of the grid
        """
        # check that the sizeX and sizeY are valid, if not throw an error
        if sizeX <= 0 or sizeY <= 0:
            raise ValueError("Grid size must be greater than 0")
        if sizeX > 1000 or sizeY > 1000:
            raise ValueError("Grid sizes must be less than 1000")
        self.sizeX = sizeX
        self.sizeY = sizeY

        # rgbMap dictionary specifying what each type of pixel "tile" corresponds to in RGBA (r, g, b, a)
        global rgbMap
        rgbMap = {
            "wall": (0,  0,  0, 255),
            "background": (255, 255, 255, 255),
            "closet": (192, 192, 224, 255),
            "bathroom": (192, 255, 255, 255),  # /washroom
            "dining room": (224, 255, 192, 255), # livingroom/kitchen/dining room
            "bedroom": (255, 224, 128, 255),
            "hall": (255, 160, 96, 255),
            "balcony": (255, 224, 224, 255),
            "opening": (255, 60, 128, 255),  # door & window
            "NaN": (0, 0, 0, 0)  # unused / used as an invalid tile
        }
        # tileMap dict specifies what each RGBA's (r, g, b, a) colour corresponds to as a tile type
        global tileMap
        tileMap = {v: k for k, v in rgbMap.items()}

        # dictionary containing the opening shapes in the grid
        # opened as empty
        self.openingDict = dict()

        # initialise the starting grid
        # create a 2d numpy array of the given size
        self.grid = self.createGrid(sizeX, sizeY)

    def createGrid(self, sizeX, sizeY):
        """Creates the empty grid of a given size

        Args:
            sizeX (int): the horizontal size X of the grid
            sizeY (int): the vertical size Y of the grid

        Returns:
            numpy ndarray: an empty 2D numpy ndarray, ready to contain tuples
        """
        return np.empty((sizeX, sizeY), dtype=tuple)

    # function to input a colour into the 2d grid
    def populate(self, locationX, locationY, rgbTuple):
        """Setter function to set a given colour rgbTuple on the grid 
        instance at a given coordinate locationX, locationY

        Args:
            locationX (int): the x coordinate of the grid's pixel you want to change
            locationY (int): the y coordinate of the grid's pixel you want to change
            rgbTuple (tuple): the RGBA colour as a 4-tuple (r, g, b, a)
        """
        if locationX < 0 or locationY < 0:
            raise ValueError("Grid coordinates must be greater than 0")
        if locationX > self.sizeX or locationY > self.sizeY:
            raise ValueError(
                "Grid coordinates must be less than the grid size")
        for value in rgbTuple:
            if value < 0 or value > 255:
                raise ValueError("RGBA values must be between 0 and 255")
        if not (len(rgbTuple) == 4 or len(rgbTuple) == 3):
            raise ValueError(
                "RGBA values must be a 3-tuple (r, g, b) or 4-tuple (r, g, b, a)")
        if len(rgbTuple) == 3:
            rgbTuple = rgbTuple + (255,)
            self.grid[locationX, locationY] = rgbTuple
        else:
            self.grid[locationX, locationY] = rgbTuple

    def getSelf(self):
        """returns the current grid instance, i.e. self

        Returns:
            Grid: the current grid
        """
        return self.grid

    def getSizeX(self):
        """getter function for the width of the grid

        Returns:
            int: the horizontal size of the grid 
        """
        return self.sizeX

    def getSizeY(self):
        """getter function for the height of the grid

        Returns:
            int: the vertical size of the grid 
        """
        return self.sizeY

    def getAsList(self):
        """returns all of the grid's individual colour tuples as a single list

        Returns:
            list: list containing all the pixel colour values as tuples of the current grid
        """
        return self.grid.flatten()

    def getRGBValue(self, x, y):
        """Returns the RGB value stored within the grid at a given x,y

        Args:
            x (int): the given x coordinate for which to retrieve the colour
            y (int): the given y coordinate for which to retrieve the colour

        Returns:
            tuple: A 4-tuple containing the RGBA colour (r, g, b, a)
        """
        if self.grid[int(x), int(y)] == None:
            return rgbMap["NaN"]
        else:
            return self.grid[int(x), int(y)]

    def averagePixel(self, listOfPixels):
        """returns the center pixel of a shape (a list of pixels)
            Does not assume that the returned pixel is part of the given shape

        Args:
            listOfPixels (list): the list of pixels as [(x, y), ...]

        Returns:
            tuple: the pixel closest to the center of that shape
        """
        if len(listOfPixels) == 0:
            raise ValueError("Cannot average an empty list of pixels")
        x = []
        y = []
        for pixel in listOfPixels:
            x.append(pixel[0])
            y.append(pixel[1])
        avgX = sum(x)/len(x)
        avgY = sum(y)/len(y)

        return (int(avgX), int(avgY))

    def getTileType(self, x, y):
        """returns the type of tile at that x, y location on the grid instance

        Args:
            x (int): the given x coordinate for which to retrieve the tile type
            y (int): the given y coordinate for which to retrieve the tile type

        Returns:
            string: tile (see rgbMap dict)
        """
        if x < 0 or y < 0:
            raise ValueError("Grid coordinates must be greater than 0")
        if x > self.getSizeX() or y > self.getSizeY():
            raise ValueError("Grid coordinates must be less than the grid size")
        
        return tileMap[(self.getRGBValue(x, y))]

    def getAdjacentCoords(self, x, y):
        """returns the adjacent pixel to the north, south, east, west of a given coordinate 
            making sure that only valid pixels are returned

        Args:
            x (int): the given x coordinate for which to retrieve the adjacent pixel coordinates
            y (int): the given y coordinate for which to retrieve the adjacent pixel coordinates

        Returns:
            dict: the adjacent pixels as a dictionary in format {"north" : (x, y-1)...}
        """
        adjacentCoords = {"north": (x, y-1),
                          "east": (x+1, y),
                          "south": (x, y+1),
                          "west": (x-1, y)}
        output = {}
        # check that we don't exit our grid boundaries
        
        if x < 0 or y < 0:
            raise ValueError("Grid coordinates must be greater than 0")
        if x > self.getSizeX() or y > self.getSizeY():
            raise ValueError("Grid coordinates must be less than the grid size")
        
        for coord in adjacentCoords:
            if 0 <= adjacentCoords[coord][0] < self.getSizeX() and 0 <= adjacentCoords[coord][1] < self.getSizeY():
                output[coord] = adjacentCoords[coord]
        return output

    def getAdjacentTiles(self, x, y):
        """returns the adjacent tile to the north, south, east, west of a given coordinate 

        Args:
            x (int): the given x coordinate for which to retrieve the adjacent tile
            y (int): the given y coordinate for which to retrieve the adjacent tile

        Returns:
            dict: the adjacent pixels as a dictionary in format {"north" : "wall"...}
        """
        adjacentTiles = {k: self.getTileType(
            v[0], v[1]) for k, v in self.getAdjacentCoords(x, y).items()}
        return adjacentTiles

    def tileSearch(self, tile):
        """returns a 2d list containing all the pixels 
        of each shape of a searched tile type as a sublist

        a shape is defined as at least two pixels 
        of the same colour touching each other with Four-Pixel Connectivity
        (up, down, left, right)

        Args:
            tile (string): the tile to search as a string (see rgbMap dict for tile list)

        Returns:
            list: a 2D list containing each shape as a sublist of its pixels
        """
        searchGrid = copy.deepcopy(self)
        resultList = list()
        # print(searchGrid.getSizeX(), searchGrid.getSizeY())
        for x in range(searchGrid.getSizeX()):
            for y in range(searchGrid.getSizeY()):
                # print("looking at " + str(x) + ", " + str(y))
                if searchGrid.getTileType(x, y) == tile:
                    adjacentTiles = list(
                        searchGrid.getAdjacentTiles(x, y).values())
                    if tile in adjacentTiles:
                        shapeList = list()
                        searchGrid.coagulateShape(tile, x, y, shapeList)
                        resultList.append(shapeList)
        return resultList

    # returns a list of instances of a tile which are all adjacent to each other
    # i.e. finds a window's individual tiles and returns them as a list
    def coagulateShape(self, tile, x, y, shapeList=[]):
        """ Performs a recursive Depth First Search

        returns a list of coordinates of a tile which are all adjacent to each other 
        through Four Pixel connectivity (up, down, left, right)

        i.e. finds a shape's individual tiles and returns them as a list

        Args:
            tile (string): the tile to search for (see rgbMap dict for tile list)
            x (int): the x coordinate of the starting pixel
            y (int): the y coordinate of the starting pixel
            shapeList (list): the list that the shape's coordinates will be appended to recursively
        """
        # base case
        if not self.getTileType(x, y) == tile:
            return

        # recursive case
        self.populate(x, y, (0, 0, 0, 0))
        shapeList.append((x, y))
        adjacentPixels = list(self.getAdjacentCoords(x, y).values())
        for pixel in adjacentPixels:
            self.coagulateShape(tile, pixel[0], pixel[1], shapeList)

    def findOpenings(self):
        """creates a dict of all the opening objects present in the grid
        """
        openingList = self.tileSearch("opening")
        i = 0
        for sublist in openingList:
            i += 1
            self.openingDict[i] = Opening(sublist)

    def getOpenings(self):
        """returns the dictionary of opening shapes present in the grid

        Returns:
            dict: dictionary of the openings in the format {int(1): Opening()...}
        """
        return self.openingDict

    def countTiles(self, tile):
        """Counts the amount of tiles of a certain type that exist on the grid

        Args:
            tile (string): the tile to search for (see rgbMap dict for tile list)

        Returns:
            int: the number of the given tile present in the grid
        """
        count = 0
        for pixel in self.getAsList():
            if pixel == rgbMap[tile]:
                count += 1
        return count

    def getLine(self, startX, startY, endX, endY):
        """finds the line between two coordinates

        Args:
            startX (int): the x coordinate of the starting pixel
            startY (int): the y coordinate of the starting pixel
            endX (int): the x coordinate of the end pixel
            endY (int): the y coordinate of the end pixel

        Returns:
            6 int: 
            deltaX: the change in width, 
            deltaY: the change in height, 
            xx: 0 or 1 or -1, 
            xy: 0 or 1 or -1, 
            yx: 0 or 1 or -1, 
            yy: 0 or 1 or -1
        """

        deltaX, deltaY = endX - startX, endY - startY

        if deltaX > 0:
            deltaXSign = 1
        else:
            deltaXSign = -1

        if deltaY > 0:
            deltaYSign = 1
        else:
            deltaYSign = -1

        deltaX, deltaY = abs(deltaX), abs(deltaY)

        if deltaX > deltaY:
            xx, xy, yx, yy = deltaXSign, 0, 0, deltaYSign
        else:
            deltaX, deltaY = deltaY, deltaX
            xx, xy, yx, yy = 0, deltaYSign, deltaXSign, 0

        return deltaX, deltaY, xx, xy, yx, yy

    def pixelsBetweenTwoPoints(self, startX, startY, endX, endY):
        """function that returns all the pixels in the line that connects two grid coordinates
            including both the start and the end points           

        Args:
            startX (int): the x coordinate of the starting pixel
            startY (int): the y coordinate of the starting pixel
            endX (int): the x coordinate of the end pixel
            endY (int): the y coordinate of the end pixel

        Returns:
            list: the list of pixels on the calculated line, including both the start and the end points
        """

        # Uses an implementation of Bresenham's algorithm
        # wikiwand.com/en/Bresenham%27s_line_algorithm

        deltaX, deltaY, xx, xy, yx, yy = self.getLine(
            startX, startY, endX, endY)

        line = []
        D = 2*deltaY - deltaX
        y = 0

        for x in range(deltaX + 1):
            line.append((startX + x*xx + y*yx, startY + x*xy + y*yy))
            if D >= 0:
                y += 1
                D -= 2*deltaX
            D += 2*deltaY
        return line

    # todo: remove OpeningX and openingY, replace with averagePixel()
    def passThroughOpening(self, startX, startY, openingX, openingY, openingListLength):
        """returns the two pixels on the opposite side of an opening shape from a starting position

        Args:
            startX (int): the x coordinate of the starting pixel
            startY (int): the y coordinate of the starting pixel
            openingX (int): the center pixel's x coordinate of an opening shape
            openingY (int): the center pixel's y coordinate of an opening shape
            openingListLength (list): the opening shape as a list of the pixels that it is made up of

        Returns:
            list: two pixels on the opposite side of the opening shape that follow the line from the starting position to the center of the shape
        """
        deltaX, deltaY, xx, xy, yx, yy = self.getLine(
            startX, startY, openingX, openingY)

        line = []
        D = 2 * deltaY - deltaX
        y = 0

        for x in range(deltaX, min(deltaX + openingListLength, self.getSizeX())):
            # print("checking: " + str((startX + x*xx + y*yx, startY + x*xy + y*yy)))
            # print(self.getTileType(startX + x*xx + y*yx, startY + x*xy + y*yy))
            if 0 <= (startX + x*xx + y*yx) < self.getSizeX() and 0 <= (startY + x*xy + y*yy) < self.getSizeY():
                if not self.getTileType(startX + x*xx + y*yx, startY + x*xy + y*yy) == "opening":
                    # print(str((startX + x*xx + y*yx, startY + x*xy + y*yy)) + " is not an opening")
                    if len(line) < 2:
                        line.append(
                            (startX + x*xx + y*yx, startY + x*xy + y*yy))
                if D >= 0:
                    y += 1
                    D -= 2 * deltaX
                D += 2 * deltaY
        # print("passthroughPixels: " + str(line))
        return line

    # todo: remove OpeningX and openingY, replace with averagePixel()
    def otherSide(self, startX, startY, openingX, openingY, openingListLength):
        """returns the most common type of tile on the other side of an opening from a given location

        Args:
            startX (int): the x coordinate of the starting pixel
            startY (int): the y coordinate of the starting pixel
            openingX (int): the center pixel's x coordinate of an opening shape
            openingY (int): the center pixel's y coordinate of an opening shape
            openingListLength (_type_): the size of the shape in pixels (i.e. the length of the shape as an array)

        Returns:
            string: the most common tile on the other side of an opening
        """
        flipsidePixels = self.passThroughOpening(
            startX, startY, openingX, openingY, openingListLength)
        pixelsToSearch = []
        for pixel in flipsidePixels:
            adjacent = self.getAdjacentCoords(pixel[0], pixel[1])
            for adjacentPixel in adjacent:
                if adjacent[adjacentPixel] not in pixelsToSearch:
                    pixelsToSearch.append(self.getTileType(
                        adjacent[adjacentPixel][0], adjacent[adjacentPixel][1]))
        # print(pixelsToSearch)
        tileCounts = Counter(pixelsToSearch)
        return tileCounts.most_common(1)[0][0]

    def getObstructionsInLine(self, lineAsListOfPixels, pixelsToIgnore=[]):
        """function that count how many wall pixels or opening pixels are in a given line on the grid

        Args:
            lineAsListOfPixels (list): the list of pixels that make up a line
            pixelsToIgnore (list, optional): list of pixels to ignore (e.g. the opening's own pixels)

        Returns:
            int: the number of wall or opening tiles encountered in that line
        """
        obstructionNum = 0
        searchable = [
            pixel for pixel in lineAsListOfPixels if pixel not in pixelsToIgnore]
        for pixel in searchable:
            # if that pixel is a wall
            if self.getTileType(pixel[0], pixel[1]) == "wall" or self.getTileType(pixel[0], pixel[1]) == "opening":
                obstructionNum += 1
        return obstructionNum

    def rgbDistance(self, start, end):
        """calculate the euclidian distance between two RGB values

        Args:
            start (tuple): (r, g, b, a)
            end (tuple): (r, g, b, a)

        Returns:
            int: the euclidian distance between the two colours
        """
        start = np.array(start)
        end = np.array(end)
        return np.linalg.norm(start-end)

    def crushDithering(self, givenGrid):
        """replaces all colours in the given grid with the closest colour present in rgbMap,
        using the rgbDistance function

        Args:
            grid (Grid): the grid to crush the dithering on

        Returns:
            Grid: the crushed grid post-processing
        """
        # print(givenGrid.getRGBValue(0, 0))
        crushedGrid = Grid(givenGrid.getSizeX(), givenGrid.getSizeY())
        for x in range(0, crushedGrid.getSizeX()):
            for y in range(0, crushedGrid.getSizeY()):
                closestColour = None
                closestDistance = (256*256*256*256+1)
                # print("looking at pixel " + str(x) + ", "+ str(y))
                for colour in rgbMap:
                    distance = givenGrid.rgbDistance(
                        givenGrid.grid[x, y], rgbMap.get(colour))
                    # print("distance to " + str(colour) + " is " + str(distance))
                    # print("closestDistance = " + str(closestDistance))
                    if distance < float(closestDistance):
                        closestDistance = distance
                        closestColour = colour

                # print("closest colour is " + str(closestColour) + " at distance " + str(closestDistance))
                # print(rgbMap.get(closestColour))
                rgb = rgbMap.get(closestColour, (255, 255, 255, 255))
                # print(rgb)
                crushedGrid.populate(x, y, rgb)

        return crushedGrid


if __name__ == "__main__":
    pass
