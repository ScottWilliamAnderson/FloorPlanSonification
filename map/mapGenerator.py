import os
from PIL import Image
from PIL.ImageFilter import (
    GaussianBlur
    )
from .grid import Grid

class MapGenerator:
    """MapGenerator class
        takes the output of the DeepFloorPlan model and converts it to an image compatible with the grid
        populates the grid with the data from the DeepFloorPlan model
        contains functions to generate the grid from either the model output or an example
    """    
    def __init__(self, finalSize = 128):
        # resize the image to be axa size where a = 128
        # assumes that the output of the DeepFloorPlan model is a 512x512 image
        self.workingGridSize = 512
        # default final size is 128x128
        self.finalSize = finalSize
        #get parent directory:
        self.parentDirectory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        self.currentDirectory = os.path.abspath(os.getcwd())
        
        
    def create(self):
        """main function to convert the DeepFloorPlan output to an image compatible with the grid
        """        
        # # convert the jpg of the model to a png
        # try:
        #     self.saveAsPNG()
        # except:
        #     print("couldn't save as PNG")
        #     pass
        # create the grid based on the model output
        self.createGrid(filename="result.png")
        print("populating the grid with data")
        # populate the empty grid with the model output RGB values
        self.grid = self.populateGrid(self.floorplan.size[0], self.grid, self.floorplan)
        # print(self.grid.getAsList())
        print("fixing ML output noise")
        # Gaussian Blur to remove jpg noise, and to fix overfitting of the tiles
        self.blurGrid()
        print("adjusting final map")
        # first replaces all pixel colours with the closest tile colour, then shrinks the grid to final size 
        self.fixNoise()
        # replaces all pixel colours on the final size grid with the closest tile colour to further reduce blur noise from shrinkage
        self.crushDitheringTwice()     
        # populates the final grid with the RGB values of the final image
        self.createFromSaveFile()
        self.floorplan.close()   
        
    def createFromSaveFile(self, example = False):
        """populates the final grid with the RGB values of either the example image or the cleaned DeepFloorPlan model output image

        Args:
            example (bool, optional): indicate whether the example showcase was chosen. Defaults to False.
        """        
        if example == True:
            self.createGrid(fromMemory=True, filename="example.png")
        else:
            self.createGrid(fromMemory=False, filename="saved.png")
        print("populating the grid with data")
        self.grid = self.populateGrid(self.finalSize, self.grid, self.floorplan)
        self.floorplan.close()
        
    # not used
    def saveAsPNG(self):
        """get output of the DeepFloorPlan and save it as png
        """        
        colouredFloorPlan = Image.open(os.path.join(os.getcwd(), "map", "result.jpg"))
        colouredFloorPlan.save(os.path.join(os.getcwd(), "map", "result.png"))
        colouredFloorPlan.close()

    def createGrid(self, fromMemory = False, filename = "example.png"):
        """create a grid from either the DeepFloorPlan model output or an example image

        Args:
            fromMemory (bool, optional): indicate whether an image different from the DeepFloorPlan model output is going to be used as the grid source data. Defaults to False.
            filename (str, optional): file name of the custom image to use. Defaults to "example.png".
        """        
        if fromMemory == True:
            path = os.path.join("map", filename)
            # print("opening " + str(path))
            self.floorplan = Image.open(path)
            
            self.grid = Grid(self.floorplan.size[0], self.floorplan.size[0])
        else:
            self.floorplan = Image.open(os.path.join("map",filename))
            self.grid = Grid(self.floorplan.size[0], self.floorplan.size[1])
            

    def populateGrid(self, gridsize, givenGrid, image):
        """populate the grid with the RGB values of the given image

        Args:
            gridsize (int): size of the grid to populate
            givenGrid (grid): grid to populate
            image (Image): image to use as source data

        Returns:
            givenGrid: populated grid
        """        
        for x in range(0, gridsize):
            for y in range(0, gridsize):
                givenGrid.populate(x, y, image.getpixel((x,y)))
                # print(givenGrid.getRGBValue(x, y))
        return givenGrid
                
    def blurGrid(self):
        """Gaussian Blur to remove jpg noise, and to fix overfitting of the tiles
            saves to file blurredGrid.png
        """        
        printedGrid = Image.new('RGB', (self.workingGridSize, self.workingGridSize))
        printedGrid.putdata(self.grid.getAsList())
        # also rotates and transposes the image to handle having put the data in as a list 
        adjustedGrid = printedGrid.rotate(90).transpose(Image.FLIP_TOP_BOTTOM).filter(GaussianBlur(radius=1))
        adjustedGrid.save(os.path.join("map","blurredGrid.png"))
    
    def fixNoise(self):
        """first replaces all pixel colours with the closest tile colour, then shrinks the grid to final size
            saves to file crushedGrid.png
        """        
        self.crushedGrid = self.grid.crushDithering(self.grid)
        self.grid = self.crushedGrid
        printedCrushedGrid = Image.new('RGB', (self.workingGridSize, self.workingGridSize))
        printedCrushedGrid.putdata(self.crushedGrid.getAsList())
        # also rotates and transposes the image to handle having put the data in as a list 
        printedCrushedGrid = printedCrushedGrid.rotate(90).transpose(Image.FLIP_TOP_BOTTOM).resize((self.finalSize, self.finalSize), Image.BOX)
        printedCrushedGrid.save(os.path.join("map","crushedGrid.png"))

    def crushDitheringTwice(self):
        """ second time around, to reduce the blur noise from the first time around
            saves to file saved.png
        """        
        printedCrushedGrid = Image.open(os.path.join("map","crushedGrid.png"))
        # create the empty grid
        crushed2Grid = Grid(self.finalSize, self.finalSize)
        # populate it
        self.grid = self.populateGrid(self.finalSize, crushed2Grid, printedCrushedGrid)
        # crush dithering again
        twiceCrushedGrid = crushed2Grid.crushDithering(crushed2Grid)
        printed2xCrushedGrid = Image.new('RGB', (self.finalSize, self.finalSize))
        printed2xCrushedGrid.putdata(twiceCrushedGrid.getAsList())
        # rotates and transposes the image to handle having put the data in as a list 
        printed2xCrushedGrid = printed2xCrushedGrid.rotate(90).transpose(Image.FLIP_TOP_BOTTOM)
        printed2xCrushedGrid.save(os.path.join("map","saved.png"))
        # set the final self.floorplan to the final version of the image 
        self.floorplan = printed2xCrushedGrid

if __name__ == "__main__":
    pass





